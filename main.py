import subprocess
import sys
import os
import json
import requests
import webbrowser
from datetime import datetime
from setting import *
from PIL import Image
import threading
from PyQt5.QtGui import QPixmap
from qtpy.QtCore import Slot
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStyledItemDelegate
from PyQt5.QtWidgets import QCompleter, QTableWidgetItem, QFileDialog, QLabel
from UI.frameless import ModernWindow, dark
from PyQt5.QtCore import QTimer
from UI.style import Ui_MainWindow
from textualsearch import textualSearch
from multitextualsearch import textAndTextSearch
from imagesearch import imageSearch
from combinesearch import combineSearch

# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable high dpi scaling
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiBitmaps, True)  # use high dpi icons


old_frame = []
new_frame = []
with open("CLIP/mapping.csv", 'r', encoding='utf-8') as m:
    mapping = m.readlines()
for item in mapping:
    old_frame.append(item.split(",")[0])
    new_frame.append(item.split(",")[1].strip("\n"))
old2new = dict(zip(old_frame, new_frame))
new2old = dict(zip(new_frame, old_frame))

with open("Materials/class-descriptions.csv", 'r', encoding='utf-8') as r:
    class_list = r.readlines()


class Delegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.text = "{}".format(option.text[-10:])


def makeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


class MainWindow(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        self.resized.connect(self.scaleItem)
        # self.showFullScreen()

        # InitVariables
        self.search_thread = None
        self.id_holder = None
        self.tab = None
        self.horizontal = None
        self.pixmap = None
        self.item = None
        self.item_name = None
        self.item_folder = None
        self.filenames_iterator = None
        self.index_temp = None
        self.image4search = None
        self.submission = None
        self.photo_feature = None
        self.photo_ids = None
        self.num = 100

        # Data
        self.loadBatch()

        # TabButtons
        self.ui.tabWidget.tabCloseRequested.connect(self.removeTab)
        self.ui.tabWidget.currentChanged.connect(self.tabChanged)

        # MainButtons
        self.ui.searchNewTab.clicked.connect(self.insertTab)
        self.ui.searchThisTab.clicked.connect(self.searchScript)
        self.ui.insertTag.clicked.connect(self.insertTag)
        self.ui.searchTag.clicked.connect(self.searchTags)
        self.ui.add.clicked.connect(self.forceAdd)
        self.ui.add10Prev.clicked.connect(self.add10Prev)
        self.ui.add10Next.clicked.connect(self.add10Next)
        self.ui.openImage.clicked.connect(self.openImage)
        self.ui.openVideo.clicked.connect(self.openVideo)
        self.ui.time2Frame.clicked.connect(self.time2Frame)
        self.ui.importImage.clicked.connect(self.importImage)
        self.ui.imageSearch.clicked.connect(self.searchImage)
        self.ui.combineSearch.clicked.connect(self.searchCombine)
        self.ui.submit.clicked.connect(self.submit)
        self.ui.searchFrame.clicked.connect(self.checkFrame)
        self.ui.load.clicked.connect(self.loadBatch)

        # ListWidgets
        self.listWidget = [self.ui.listWidget]
        self.listWidgetChanged()

        # ImagesQueue
        self.timer_loading = QTimer()
        self.timer_loading.setInterval(1)
        self.timer_loading.timeout.connect(self.load_image)

        # Slider
        self.ui.horizontalSlider.valueChanged[int].connect(self.setImageFrame)
        self.ui.resultNum.valueChanged[int].connect(self.setResultNum)

        # Table
        self.table = []
        self.keyframe = []
        self.ui.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.ui.deleteRow.clicked.connect(self.deleteRow)
        self.ui.addRow.clicked.connect(self.addRow)
        self.ui.exportResult.clicked.connect(self.export)
        self.ui.tableWidget.itemDoubleClicked.connect(self.reviewSelected)

        # DataDump
        self.data_list = []

        # tagSearch
        self.ui.inputTags.textChanged.connect(self.autoUpper)
        self.completer = QCompleter(class_list)
        self.completer.popup().setStyleSheet('selection-background-color: orange; selection-color: black;')
        self.ui.inputTags.setCompleter(self.completer)
        self.ui.inputTags.editingFinished.connect(self.insertTag)
        self.ui.tagView.itemClicked.connect(self.deleteItem)

        # labelTags
        self.tags = []

        # Export
        self.saveFileNameLabel = QLabel()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            if self.ui.tableWidget.selectionModel().selectedRows():
                index = self.ui.tableWidget.selectionModel().currentIndex()
                self.ui.tableWidget.removeRow(index.row())
                self.table.pop(index.row())
        if event.modifiers() & QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
            if event.key() == QtCore.Qt.Key_S:
                self.searchScript()
            if event.key() == QtCore.Qt.Key_I:
                self.searchImage()
            if event.key() == QtCore.Qt.Key_C:
                self.searchCombine()
        else:
            super().keyPressEvent(event)

    def loadBatch(self):
        selected = str(self.ui.comboBox.currentText())
        if selected == "C00_V0X":
            self.photo_feature, self.photo_ids = c00()
        elif selected == "C01_V0X":
            self.photo_feature, self.photo_ids = c01()
            print("C01")
        elif selected == "C02_V0X":
            self.photo_feature, self.photo_ids = c02()
            print("C02")
        else:
            self.photo_feature, self.photo_ids = cTotal()
            print("ALL")
        self.ui.Information.setText("Loaded {} successfully!".format(selected))

    def checkFrame(self):
        input_frame = self.ui.lineEdit_4.text()
        if "/" in input_frame:
            item_name = os.path.basename(input_frame)
            item_folder = os.path.basename(os.path.dirname(input_frame))
            video_folder = "KeyFrames{}".format(item_folder[:-2])
            full_dir = "Images/{}/{}/{}.jpg".format(video_folder, item_folder, item_name)
            if os.path.exists(full_dir):
                self.ui.lineEdit.setText(full_dir.replace("Images/", "").strip(".jpg"))
                self.pixmap = QPixmap(full_dir)
                self.showReview()

    def submit(self):
        if self.submission:
            if self.ui.editResult.isChecked():
                itm = self.ui.tableWidget_2.item(0, 0).text().strip('.jpg')
                video = itm.split('/')[0]
                frame = int(itm.split('/')[1])
            else:
                itm = self.submission
                video = itm.split('/')[0]
                frame = int(itm.split('/')[1])
            submit = "https://eventretrieval.one/api/v1/submit?item={}&frame={}&session={}".format(
                video,
                frame,
                token
            )
            do_submit = requests.get(submit)
            try:
                info_submit = do_submit.json()['description']
            except KeyError:
                self.ui.submitStatus.setText("Something wrong!")
            else:
                self.ui.submitStatus.setText(info_submit)

    def searchCombine(self):
        if self.ui.tabWidget.count() == 0:
            self.insertTab()
        query = self.ui.plainTextEdit.toPlainText()
        if self.image4search:
            item_name = os.path.basename(self.image4search)
            item_folder = os.path.basename(os.path.dirname(self.image4search))
            video_folder = "KeyFrames{}".format(item_folder[:-2])
            full_dir = "Images/{}/{}/{}.jpg".format(video_folder, item_folder, item_name)
            if os.path.exists(full_dir):
                self.data_list = combineSearch(query, full_dir, self.photo_feature, self.photo_ids, self.num)
                self.search()

    def searchImage(self):
        if self.ui.tabWidget.count() == 0:
            self.insertTab()
        if self.image4search:
            item_name = os.path.basename(self.image4search)
            item_folder = os.path.basename(os.path.dirname(self.image4search))
            video_folder = "KeyFrames{}".format(item_folder[:-2])
            full_dir = "Images/{}/{}/{}.jpg".format(video_folder, item_folder, item_name)
            if os.path.exists(full_dir):
                self.data_list = imageSearch(full_dir,self.photo_feature, self.photo_ids, self.num)
                self.search()

    def setResultNum(self, index):
        self.ui.num.setText("{} results".format(str(index)))
        self.num = index

    def importImage(self):
        self.image4search = self.ui.lineEdit.text()
        self.ui.imageSearchReview.setPixmap(self.pixmap)
        self.ui.imageSearchReview.show()

    def time2Frame(self):
        item_dir = self.ui.lineEdit.text()
        fps = int(self.ui.lineEdit_3.text())
        if item_dir != "":
            item_folder = os.path.basename(os.path.dirname(item_dir))
            item_time = self.ui.lineEdit_2.text()
            try:
                time_value = datetime.strptime(item_time, '%M:%S')
                total_seconds = time_value.second + time_value.minute * 60
                frame = str(total_seconds * fps).rjust(6, "0")
                custom_item = "{}/{}".format(item_folder, frame)
                if "{}.jpg".format(custom_item) not in self.table:
                    if self.ui.tableWidget.selectionModel().selectedRows():
                        index = self.ui.tableWidget.selectionModel().currentIndex()
                        if self.table[index.row()] == "":
                            self.table[index.row()] = "{}.jpg".format(custom_item)
                    else:
                        self.table.append("{}.jpg".format(custom_item))
                    self.tableUpdate()
                    self.ui.lineEdit.setText("{}/{}".format(os.path.dirname(item_dir), frame))
                    self.ui.add.setEnabled(False)
            except ValueError:
                self.ui.lineEdit_2.clear()

    def openImage(self):
        item_dir = self.ui.lineEdit.text()
        item_name = os.path.basename(item_dir)
        item_folder = os.path.basename(os.path.dirname(item_dir))
        video_folder = "KeyFrames{}".format(item_folder[:-2])
        full_dir = "Images/{}/{}/{}.jpg".format(video_folder, item_folder, item_name)
        if os.path.exists(full_dir):
            im = Image.open(full_dir)
            im.show()

    def openVideo(self):
        item_dir = self.ui.lineEdit.text()
        item_name = os.path.basename(item_dir)
        item_folder = os.path.basename(os.path.dirname(item_dir))
        new_item = old2new.get("{}/{}".format(item_folder, item_name), "{}/{}".format(item_folder, item_name))
        new_frame_id = new_item.split("/")[-1]
        Meta_folder = "Metadata_{}".format(item_folder[:-2])
        full_dir = "Materials/MetaData/{}/{}.json".format(Meta_folder, item_folder)
        if os.path.exists(full_dir):
            json_file = json.load(open(full_dir, encoding="utf8"))
            youtube_url = json_file['watch_url']
            fps = json_file['fps']
            self.ui.lineEdit_3.setText(str(fps))
            frame2time = round(int(new_frame_id) / fps)
            watch_url = "{}&t={}s".format(youtube_url, frame2time)
            webbrowser.open(watch_url)

    def insertTag(self):
        tag = self.ui.inputTags.text().strip('\n')
        if len(tag) > 1:
            self.ui.tagView.addItem(tag)
            self.tags.append(tag)
        self.ui.inputTags.clear()

    def forceAdd(self):
        item_dir = self.ui.lineEdit.text()
        if item_dir != "":
            item_name = os.path.basename(item_dir)
            item_folder = os.path.basename(os.path.dirname(item_dir))
            new_item = "{}/{}.jpg".format(item_folder, item_name)
            self.addItem2Result(new_item)

    def add10Prev(self):
        item_dir = self.ui.lineEdit.text()
        if item_dir != "":
            item_name = os.path.basename(item_dir)
            item_folder = os.path.basename(os.path.dirname(item_dir))
            new_item = old2new.get("{}/{}".format(item_folder, item_name), "{}/{}".format(item_folder, item_name))
            new_name = new_item.split("/")[1]
            for i in range(1, 13):
                new_item = "{}/{}.jpg".format(item_folder, str(int(new_name) - 10 * i).rjust(6, "0"))
                if new_item not in self.table:
                    self.table.append(new_item)
                self.tableUpdate()

    def add10Next(self):
        item_dir = self.ui.lineEdit.text()
        if item_dir != "":
            item_name = os.path.basename(item_dir)
            item_folder = os.path.basename(os.path.dirname(item_dir))
            new_item = old2new.get("{}/{}".format(item_folder, item_name), "{}/{}".format(item_folder, item_name))
            new_name = new_item.split("/")[1]
            for i in range(1, 13):
                new_item = "{}/{}.jpg".format(item_folder, str(int(new_name) + 10 * i).rjust(6, "0"))
                if new_item not in self.table:
                    self.table.append(new_item)
                self.tableUpdate()

    def deleteItem(self):
        row = self.ui.tagView.currentRow()
        tag_item = self.ui.tagView.takeItem(row)
        self.ui.tagView.removeItemWidget(tag_item)
        self.tags.remove(tag_item.text())

    def autoUpper(self):
        text = self.ui.inputTags.text()
        if len(text) == 1:
            self.ui.inputTags.setText(str.upper(text))

    def setImageFrame(self, index):
        if self.item_folder is not None:
            file_list = os.listdir(self.item_folder)
            next_index = file_list.index(self.item_name) - 5 + index
            if next_index in range(len(file_list)):
                item_dir = "{}/{}".format(self.item_folder, file_list[next_index])
                self.ui.lineEdit.setText(item_dir.replace("Thumbnails/", "").strip(".jpg"))
                self.ui.add.setEnabled(True)
                self.pixmap = QPixmap(item_dir.replace("Thumbnails", "Images"))
                self.showReview()

    def reviewSelected(self, index):
        if self.ui.editResult.isChecked():
            self.ui.tableWidget_2.setEditTriggers(QtWidgets.QTableWidget.AllEditTriggers)
        else:
            self.ui.tableWidget_2.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.submission = self.table[index.row()].strip(".jpg")
        self.ui.tableWidget_2.setColumnCount(1)
        self.ui.tableWidget_2.setRowCount(1)
        self.ui.tableWidget_2.setItem(0, 0, QTableWidgetItem(self.table[index.row()]))
        self.ui.tableWidget_2.item(0, 0).setBackground(QtGui.QColor(0, 100, 0))
        item_converted = new2old.get(self.table[index.row()].strip(".jpg"), self.table[index.row()].strip(".jpg"))
        file = item_converted.split('/')[-1]
        video = item_converted.split('/')[0]
        video_folder = "KeyFrames{}".format(video[:-2])
        item_dir = "Images/{}/{}/{}.jpg".format(video_folder, video, file)
        self.ui.lineEdit.setText(item_dir.replace("Images/", "").strip(".jpg"))
        self.ui.add.setEnabled(True)
        if os.path.exists(item_dir):
            self.pixmap = QPixmap(item_dir)
            self.showReview()

    def export(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Save result as",
                                                  self.saveFileNameLabel.text(),
                                                  "Documents (*.csv)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as w:
                for element in self.table:
                    video = "{}.mp4".format(element.split("/")[0])
                    frame = element.split("/")[-1].strip(".jpg")
                    record = "{}, {}\n".format(video, frame)
                    w.write(record)
        if sys.platform == "win32":
            os.startfile(os.path.dirname(filename))
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, os.path.dirname(filename)])

    def itemClicked(self):
        self.ui.horizontalSlider.setSliderPosition(5)  # return review slider back
        self.item = self.listWidget[self.ui.tabWidget.currentIndex()].currentItem()
        item_dir = self.item.text()
        self.item_name = os.path.basename(item_dir)
        self.item_folder = os.path.dirname(item_dir)
        self.ui.lineEdit.setText(item_dir.replace("Thumbnails/", "").strip(".jpg"))
        self.ui.add.setEnabled(True)
        if self.item is not None:
            self.pixmap = QPixmap(item_dir.replace("Thumbnails", "Images"))
            self.showReview()

    def itemDoubleClicked(self):
        self.item = self.listWidget[self.ui.tabWidget.currentIndex()].currentItem()
        item_dir = self.item.text()
        item_name = os.path.basename(item_dir)
        item_folder = os.path.basename(os.path.dirname(item_dir))
        new_item = "{}/{}".format(item_folder, item_name)
        self.addItem2Result(new_item)

    def addItem2Result(self, new_item):
        item_converted = old2new[new_item.strip(".jpg")]
        if "{}.jpg".format(item_converted) not in self.table:
            if self.ui.tableWidget.selectionModel().selectedRows():
                index = self.ui.tableWidget.selectionModel().currentIndex()
                if self.table[index.row()] == "":
                    self.table[index.row()] = "{}.jpg".format(item_converted)
                    self.keyframe.append("{}.jpg".format(item_converted))
            else:
                self.table.append("{}.jpg".format(item_converted))
                self.keyframe.append("{}.jpg".format(item_converted))
            self.tableUpdate()

    def tableUpdate(self):
        self.ui.tableWidget.setColumnCount(1)
        row = len(self.table)
        self.ui.tableWidget.setRowCount(row)
        for i in range(row):
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.table[i]))
            if self.table[i] in self.keyframe:
                self.ui.tableWidget.item(i, 0).setBackground(QtGui.QColor(150, 50, 0))
        self.ui.tableWidget.selectionModel().reset()

    def deleteRow(self):
        if self.ui.tableWidget.selectionModel().selectedRows():
            index = self.ui.tableWidget.selectionModel().currentIndex()
            self.ui.tableWidget.removeRow(index.row())
            self.table.pop(index.row())

    def addRow(self):
        if self.ui.tableWidget.selectionModel().selectedRows():
            index = self.ui.tableWidget.selectionModel().currentIndex()
            self.table.insert(index.row() + 1, "")
            self.tableUpdate()

    def showReview(self):
        self.ui.reviewImage.setPixmap(self.pixmap)
        self.ui.reviewImage.show()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)

    def scaleItem(self):
        if self.listWidget[self.ui.tabWidget.currentIndex()].verticalScrollBar().visibleRegion().isEmpty():
            viewport = self.listWidget[self.ui.tabWidget.currentIndex()].viewport().width() - 16  # Scrollbar
        else:
            viewport = self.listWidget[self.ui.tabWidget.currentIndex()].viewport().width()
        horizon_num = int(viewport / ICON_SIZE)
        width_all = ICON_SIZE * horizon_num
        remainder = viewport - width_all
        extra = int((remainder / horizon_num))
        self.listWidget[self.ui.tabWidget.currentIndex()].setGridSize(QSize(ICON_SIZE + extra, ICON_SIZE))

    def searchTags(self):
        if self.ui.tabWidget.count() == 0:
            self.insertTab()
        if self.tags:
            self.data_list = textAndTextSearch(self.tags, self.photo_feature, self.photo_ids, self.num)
            self.search()

    def searchScript(self):
        if self.ui.tabWidget.count() == 0:
            self.insertTab()
        query = self.ui.plainTextEdit.toPlainText()
        self.data_list = textualSearch(query, self.photo_feature, self.photo_ids, self.num)
        self.search()

    def search(self):
        self.scaleItem()
        self.id_holder = self.ui.tabWidget.currentIndex()
        self.ui.Information.setText("Searching on tab {}".format(self.id_holder))
        self.search_thread = threading.Thread(target=self.start_loading())
        self.search_thread.start()

    def start_loading(self):
        if self.timer_loading.isActive():
            self.timer_loading.stop()
        self.filenames_iterator = self.load_images()
        self.listWidget[self.ui.tabWidget.currentIndex()].clear()
        self.timer_loading.start()

    def load_image(self):
        try:
            filename = next(self.filenames_iterator)
            self.ui.tabWidget.setTabsClosable(False)
        except StopIteration:
            self.timer_loading.stop()
            self.ui.tabWidget.setTabsClosable(True)
        else:
            it = QtWidgets.QListWidgetItem(filename, None)
            it.setIcon(QtGui.QIcon(filename))
            self.listWidget[self.id_holder].addItem(it)
            delegate = Delegate(self.listWidget[self.id_holder])
            self.listWidget[self.id_holder].setItemDelegate(delegate)

    def load_images(self):
        for element in self.data_list:
            yield element

    def tabChanged(self):
        self.ui.Information.setText("Changed to tab {}".format(self.ui.tabWidget.currentIndex()))
        self.listWidgetChanged()

    def listWidgetChanged(self):
        self.listWidget[self.ui.tabWidget.currentIndex()].itemClicked.connect(self.itemClicked)
        self.listWidget[self.ui.tabWidget.currentIndex()].itemDoubleClicked.connect(self.itemDoubleClicked)

    def removeTab(self, index):
        self.ui.tabWidget.removeTab(index)
        self.listWidget.pop(index)
        self.ui.Information.setText("Removed Tab!")

    def insertTab(self):
        text = "New Tab"
        self.tab = QtWidgets.QWidget()
        self.horizontal = QtWidgets.QHBoxLayout(self.tab)
        self.horizontal.setSpacing(6)
        self.horizontal.setContentsMargins(11, 11, 11, 11)
        self.listWidget.append(QtWidgets.QListWidget(self.tab))
        self.listWidget[-1].setIconSize(QtCore.QSize(130, 130))
        self.listWidget[-1].setMovement(QtWidgets.QListView.Static)
        self.listWidget[-1].setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget[-1].setViewMode(QtWidgets.QListView.IconMode)
        self.horizontal.addWidget(self.listWidget[-1])
        self.ui.tabWidget.addTab(self.tab, text)
        self.ui.Information.setText("Created new tab!")

    @Slot()
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Do you want to exit?')
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark(app)
    main = ModernWindow(MainWindow())
    main.setWindowIcon(QtGui.QIcon(ICON_PATH))
    main.setWindowTitle("Badger Team X Video Retrieval - Developed by Nguyen Trieu Phong")
    main.show()
    sys.exit(app.exec())
