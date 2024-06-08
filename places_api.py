import requests
import os


def getCityPredictions(searchQuery):
    baseUrl = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    apiKey = os.environ['PLACES_ACCESS_KEY']
    params = {"key": apiKey, "input": searchQuery, "types": "(cities)"}

    response = requests.get(baseUrl, params=params)
    data = response.json()

    if data:
        predictions = [prediction["description"] for prediction in data["predictions"]]
        return predictions
    else:
        return None


def getCitySights(cityName: str):
    baseUrl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    apiKey = os.environ["PLACES_ACCESS_KEY"]
    query = "city attractions in " + cityName
    limit = 5

    url = baseUrl + f"query={query}&key={apiKey}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    result = []

    if "results" in data:
        for place in data["results"]:
            temp = {"name": place["name"]}

            placeId = place["place_id"]
            mapsLink = f"https://www.google.com/maps/place/?q=place_id:{placeId}"
            temp["mapsLink"] = mapsLink

            address = place['formatted_address']
            temp["address"] = address
            photoReference = place['photos'][0]['photo_reference']

            imageUrl = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=200&photoreference={photoReference}&key={apiKey}'
            temp["imageUrl"] = imageUrl

            result.append(temp)
            if len(result) == 5:
                break
    return result
