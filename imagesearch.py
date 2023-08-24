from setting import *
from PIL import Image


def imageFeature(query):
    with torch.no_grad():
        image = Image.open(query)
        image_encoded = model.encode_image(preprocess(image).unsqueeze(0).to("cpu"))
        image_encoded /= image_encoded.norm(dim=-1, keepdim=True)
    image_features = image_encoded.cpu().numpy()
    return image_features


def imageSearch(query, photo_features, photo_ids, output_range):
    with torch.no_grad():
        image = Image.open(query)
        image_encoded = model.encode_image(preprocess(image).unsqueeze(0).to("cpu"))
        image_encoded /= image_encoded.norm(dim=-1, keepdim=True)

    # Retrieve the description vector and the photo vectors
    image_features = image_encoded.cpu().numpy()

    # Compute the similarity between the description and each photo using the Cosine similarity
    similarities = list((image_features @ photo_features.T).squeeze(0))

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


