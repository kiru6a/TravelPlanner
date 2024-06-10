import requests
import os


def get_city_predictions(search_query):
    base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    api_key = os.environ['PLACES_ACCESS_KEY']
    params = {"key": api_key, "input": search_query, "types": "(cities)"}

    response = requests.get(base_url, params=params)
    data = response.json()

    if data:
        predictions = [prediction["description"] for prediction in data["predictions"]]
        return predictions
    else:
        return None


def get_city_sights(city_name: str):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    api_key = os.environ["PLACES_ACCESS_KEY"]
    query = "city attractions in " + city_name
    limit = 5

    url = base_url + f"query={query}&key={api_key}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    result = []

    if "results" in data:
        for place in data["results"]:
            temp = {"name": place["name"]}

            place_id = place["place_id"]
            maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            temp["mapsLink"] = maps_link

            address = place['formatted_address']
            temp["address"] = address
            photo_reference = place['photos'][0]['photo_reference']

            image_url = (
                f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=200&photoreference={photo_reference}'
                f'&key={api_key}')
            temp["imageUrl"] = image_url

            result.append(temp)
            if len(result) == 5:
                break
    return result
