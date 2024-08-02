import json

import requests
import urllib3


def main():
    setup()

    virtual_episodes_result = get_virtual_episodes()

    num_virtual_episodes = virtual_episodes_result["TotalRecordCount"]
    virtual_episodes = virtual_episodes_result["Items"]

    seasons_result = get_seasons()

    num_seasons = seasons_result["TotalRecordCount"]
    seasons = seasons_result["Items"]

    for season in seasons:
        season_episodes_result = get_episodes_for_season(season)
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


def setup():
    config = json.load(open("config.local.json"))
    global AUTH_HEADERS, URL, VERYFY_SSL
    AUTH_HEADERS = {"Accept": "application/json", "X-Emby-Token": config["api_token"]}
    URL = config["jellyfin_host"]
    VERYFY_SSL = config["verify_ssl"]

    if not VERYFY_SSL:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_virtual_episodes():
    return requests.request(
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


def get_seasons():
    return requests.request(
        "GET",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "Recursive": True,
            "IncludeItemTypes": "Season",
        },
    ).json()


def get_episodes_for_season(season):
    return requests.request(
        "GET",
        URL + "/Shows/" + season["SeriesId"] + "/Episodes",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "seasonId": season["Id"],
        },
    ).json()


if __name__ == "__main__":
    main()
