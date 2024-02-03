import requests
import os


def unsplashApiCitySearch(query: str, maxHeight=None):
  if query is None:
    return None
    
  apiUrl = "https://api.unsplash.com/search/photos"
  apiKey = os.environ["UNSPLASH_ACCESS_KEY"]

  params = {"query": query, "client_id": apiKey}

  
  
  try:
    result = requests.get(apiUrl, params=params, allow_redirects=True)
    data = result.json()

    if not data.get("total"):
        return None

    filteredImages = [image for image in data["results"] if image["height"] <= maxHeight]
    
    if not filteredImages:
      return None
    
    return filteredImages[0]["urls"]["raw"]
    
  except requests.exceptions.RequestException:
    return None

print(unsplashApiCitySearch("Bi", 3500))
