from textualsearch import textualFeature
from setting import *


def textAndTextSearch(text_input, photo_features, photo_ids, output_range):
    total_features = np.empty(shape=(1, 512))
    for text in text_input:
        each_feature = textualFeature(text)
        total_features += each_feature
    # Compute the similarity between the description and each photo using the Cosine similarity
    similarities = list((total_features @ photo_features.T).squeeze(0))

    # Sort the photos by their similarity score
    best_photos = sorted(zip(similarities, range(photo_features.shape[0])), key=lambda x: x[0], reverse=True)

    # Iterate over the top 10 results
    results = []
    for i in range(output_range):
        # Retrieve the photo ID
        idx = best_photos[i][1]
        photo_id = "{}".format(photo_ids[idx])
        results.append(photo_id)
    return results
