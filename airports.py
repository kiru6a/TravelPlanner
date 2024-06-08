import airportsdata


def get_airports_by_city_name(city_name: str) -> list[dict[str, str]]:
    airports = airportsdata.load("IATA")
    result = dict(filter(lambda item: item[1]["city"] == city_name, airports.items())).values()
    result = [{"code": entry["iata"], "name": entry["name"]} for entry in result]
    return result
