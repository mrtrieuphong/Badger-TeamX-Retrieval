from setting import *


def textualFeature(query):

    with torch.no_grad():
        # Encode and normalize the description using CLIP
        text_encoded = model.encode_text(clip.tokenize(query).to(device))
        text_encoded /= text_encoded.norm(dim=-1, keepdim=True)

    # Retrieve the description vector and the photo vectors
    text_features = text_encoded.cpu().numpy()
    return text_features


def textualSearch(query, photo_features, photo_ids, output_range):

    with torch.no_grad():
        # Encode and normalize the description using CLIP
        text_encoded = model.encode_text(clip.tokenize(query).to(device))
        text_encoded /= text_encoded.norm(dim=-1, keepdim=True)

    # Retrieve the description vector and the photo vectors
    text_features = text_encoded.cpu().numpy()

    # Compute the similarity between the description and each photo using the Cosine similarity
    similarities = list((text_features @ photo_features.T).squeeze(0))

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
