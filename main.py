import json

import requests
import urllib3


def main():
    config = json.load(open("config.local.json"))
    global AUTH_HEADERS, URL, VERYFY_SSL
    AUTH_HEADERS = {"Accept": "application/json", "X-Emby-Token": config["api_token"]}
    URL = config["jellyfin_host"]
    VERYFY_SSL = config["verify_ssl"]

    if not VERYFY_SSL:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    virtual_episodes_result = requests.request(
        "GET",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "Recursive": True,
            "IncludeItemTypes": "Episode",
            "locationTypes": "Virtual",
        },
    ).json()

    num_virtual_episodes = virtual_episodes_result["TotalRecordCount"]
    virtual_episodes = virtual_episodes_result["Items"]

    seasons_result = requests.request(
        "GET",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "Recursive": True,
            "IncludeItemTypes": "Season",
        },
    ).json()

    num_seasons = seasons_result["TotalRecordCount"]
    seasons = seasons_result["Items"]

    for season in seasons:
        season_episodes_result = get_episodes(season)
        num_season_episodes = season_episodes_result["TotalRecordCount"]
        season_episodes = season_episodes_result["Items"]
        counter = 0
        for episode in season_episodes:
            if episode["LocationType"] == "Virtual":
                counter += 1

        if counter > 0:
            print(
                f"{counter} virtual episodes in Season {season['Name']} in Series {season['SeriesName']}"
            )


def get_episodes(season):
    result = requests.request(
        "GET",
        URL + "/Shows/" + season["SeriesId"] + "/Episodes",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "seasonId": season["Id"],
        },
    ).json()
    return result


if __name__ == "__main__":
    main()
