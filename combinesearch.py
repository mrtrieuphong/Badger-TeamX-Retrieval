from textualsearch import textualFeature
from imagesearch import imageFeature


def combineSearch(text_query, image_query, photo_features, photo_ids, output_range):
    image_feature = imageFeature(image_query)
    text_feature = textualFeature(text_query)
    total_feature = image_feature + text_feature
    similarities = list((total_feature @ photo_features.T).squeeze(0))

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
