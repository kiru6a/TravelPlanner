import requests
import os


def search_for_trips(cityFrom: str, cityTo: str, dateFrom: str, returnFrom: str, curr: str):
    base_url = "https://api.tequila.kiwi.com/v2/search"
    api_key = os.environ.get("KIWI_ACCESS_KEY")

    headers = {"apikey": api_key}
    parameters = {"fly_from": cityFrom, "date_from": dateFrom, "date_to": dateFrom,
                  "return_from": returnFrom, "return_to": returnFrom, "fly_to": cityTo, "curr": curr, "limit": 5}

    response = requests.get(base_url, headers=headers, params=parameters)
    data = response.json()
    if "data" in data:
        data = data["data"]
    else:
        return None

    result = []

    for flight in data:
        temp = {"cityFrom": flight["cityFrom"],
                "cityTo": flight["cityTo"],
                "airportFrom": flight["flyFrom"],
                "airportTo": flight["flyTo"],
                "price": flight["price"],
                "local_departure": flight["local_departure"],
                "local_arrival": flight["local_arrival"],
                "curr": curr}

        if "id" in flight and "booking_token" in flight:
            booking_link = f"https://www.kiwi.com/uk/booking?flightsId={flight['id']}&token={flight['booking_token']}"
            temp["bookingLink"] = booking_link
        result.append(temp)

    return result
