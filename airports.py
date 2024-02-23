import airportsdata


def getAirportsByCityName(cityName: str) -> list[dict[str, str]]:
    airports = airportsdata.load("IATA")
    result = dict(filter(lambda item: item[1]["city"] == cityName, airports.items())).values()
    result = [{"code": entry["iata"], "name": entry["name"]} for entry in result]
    return result
