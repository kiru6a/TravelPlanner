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
