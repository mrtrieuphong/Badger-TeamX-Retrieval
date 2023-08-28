# python3 Tools/4_mapping.py
with open("mapping.csv", 'w', encoding='utf-8') as w:
    count = 0
    with open("photo_ids.csv", 'r', encoding='utf-8') as r:
        lines = r.readlines()
    for line in lines[1:]:
        record = "{},{}".format(line.strip('\n'), line)
        w.write(record)
        count += 1
print(count)
