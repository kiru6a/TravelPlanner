import requests
import os


def searchForTrips(cityFrom: str, cityTo: str, dateFrom: str, returnFrom: str, curr: str):
  baseUrl = "https://api.tequila.kiwi.com/v2/search"
  apiKey = os.environ.get("KIWI_ACCESS_KEY")

  
  headers = {"apikey": apiKey}
  parameters = {"fly_from": cityFrom, "date_from": dateFrom, "date_to": dateFrom, \
  "return_from": returnFrom, "return_to": returnFrom, "fly_to": cityTo, "curr": curr, "limit": 5}

  response = requests.get(baseUrl, headers=headers, params=parameters)
  data = response.json()["data"]

  result = []
  
  for flight in data:
    temp = {}
    
    temp["cityFrom"] = flight["cityFrom"]
    temp["cityTo"] = flight["cityTo"]
    temp["airportFrom"] = flight["flyFrom"]
    temp["airportTo"] = flight["flyTo"]
    temp["price"] = flight["price"]
    temp["local_departure"] = flight["local_departure"]
    temp["local_arrival"] = flight["local_arrival"]
    
    if "id" in flight and "booking_token" in flight:
        bookingLink = f"https://www.kiwi.com/uk/booking?flightsId={flight['id']}&token={flight['booking_token']}"
        temp["bookingLink"] = bookingLink
    result.append(temp)

  return result

