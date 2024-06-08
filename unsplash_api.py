import requests
import os


def find_city_image(query: str, max_height=3500):
    if query is None:
        return None

    api_url = "https://api.unsplash.com/search/photos"
    api_key = os.environ["UNSPLASH_ACCESS_KEY"]

    params = {"query": query, "client_id": api_key}

    try:
        result = requests.get(api_url, params=params, allow_redirects=True)
        data = result.json()

        if not data.get("total"):
            return None

        filtered_images = [image for image in data["results"] if image["height"] <= max_height]

        if not filtered_images:
            return None

        return filtered_images[0]["urls"]["raw"]

    except requests.exceptions.RequestException:
        return None
