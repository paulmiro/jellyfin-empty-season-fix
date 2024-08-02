import sys
import json

import requests
import urllib3


def main():
    setup()

    print(
        "######################################################\n"
        + "# WARNING: THIS SCRIPT WILL PERMANENTLY DELETE DATA  #\n"
        + "# FROM YOUR JELLYFIN SERVER. DO NOT RUN THIS SCRIPT  #\n"
        + "# UNLESS YOU HAVE A BACKUP OF YOUR JELLYFIN DATABASE #\n"
        + "# AND YOUR MEDIA FILES.                              #\n"
        + "######################################################"
    )

    input("Press enter to continue...")

    if "--skip-episode-deletion" not in sys.argv:
        episode_deletion()
    if "--skip-season-deletion" not in sys.argv:
        season_deletion()

    print("Done!")
    print(
        "It's probably a good idea to make a backup of the sanity check files so you can review them later"
    )


def episode_deletion():
    episodes_to_delete = [
        episode
        for episode in get_virtual_episodes()["Items"]
        if episode_is_missing(episode)
    ]

    sanity_check = generate_episodes_sanity_check(episodes_to_delete)

    with open("episodes_sanity_check.json", "w") as f:
        json.dump(sanity_check, f, indent=2)

    print(f"Found {len(episodes_to_delete)} missing episodes to delete")

    print(
        "This script will PERMANENTLY delete the episodes listed in episodes_sanity_check.json\n"
        + "Please take a good look at it and make sure the listed episodes are actually not on your disk"
    )

    if (
        input(
            'Please type "I want to continue" to delete the episodes or anything else to exit: '
        ).lower()
        == "i want to continue"
        or True
    ):
        pass
    else:
        sys.exit(0)

    print("Deleting episodes... (this may take a while)")
    delete_items([episode["Id"] for episode in episodes_to_delete])


def season_deletion():
    seasons = get_seasons()["Items"]

    seasons_to_delete = []

    print(
        f"Found {len(seasons)} seasons. Checking for empty ones... this may take a while)"
    )

    for season in seasons:
        episodes = get_episodes_for_season(season)
        if episodes["TotalRecordCount"] == 0:
            seasons_to_delete.append(season)

    sanity_check = generate_seasons_sanity_check(seasons_to_delete)

    with open("seasons_sanity_check.json", "w") as f:
        json.dump(sanity_check, f, indent=2)

    print(f"Found {len(seasons_to_delete)} emtpy seasons to delete")
    print(
        "This script will PERMANENTLY delete the seasons listed in seasons_sanity_check.json\n"
        + "Please take a good look at it and make sure the listed seasons are actually empty"
    )
    if (
        input(
            'Please type "I want to continue" to delete the seasons or anything else to exit: '
        ).lower()
        == "i want to continue"
        or True
    ):
        pass
    else:
        sys.exit(0)

    print("Deleting seasons... (this may take a while)")
    delete_items([season["Id"] for season in seasons_to_delete])


def setup():
    config = json.load(open("config.local.json"))
    global AUTH_HEADERS, URL, VERIFY_SSL
    AUTH_HEADERS = {"Accept": "application/json", "X-Emby-Token": config["api_token"]}
    URL = config["jellyfin_host"]
    VERIFY_SSL = config["verify_ssl"]

    if not VERIFY_SSL:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_virtual_episodes():
    return requests.request(
        "GET",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERIFY_SSL,
        params={
            "Recursive": True,
            "IncludeItemTypes": "Episode",
            "locationTypes": "Virtual",
            "fields": "Path",
        },
    ).json()


def get_seasons():
    return requests.request(
        "GET",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERIFY_SSL,
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
        verify=VERIFY_SSL,
        params={
            "seasonId": season["Id"],
        },
    ).json()


def delete_items(item_ids):
    for item_id_batch in range(0, len(item_ids), 100):
        requests.request(
            "DELETE",
            URL + "/Items",
            headers=AUTH_HEADERS,
            verify=VERIFY_SSL,
            params={
                "ids": ",".join(item_id_batch),
            },
        )


def episode_is_missing(episode):
    return episode["LocationType"] == "Virtual" and "Path" not in episode.keys()


def generate_episodes_sanity_check(episodes_to_delete):
    output = {}

    for episode in episodes_to_delete:
        if episode["SeriesId"] not in output.keys():
            output[episode["SeriesId"]] = {
                "Name": (
                    episode["SeriesName"]
                    if "SeriesName" in episode.keys()
                    else "NONAME"
                ),
            }
        if episode["SeasonId"] not in output[episode["SeriesId"]].keys():
            output[episode["SeriesId"]][episode["SeasonId"]] = {
                "Name": (
                    episode["SeasonName"]
                    if "SeasonName" in episode.keys()
                    else "NONAME"
                ),
                "Episodes": [],
            }
        output[episode["SeriesId"]][episode["SeasonId"]]["Episodes"].append(
            {
                "Name": (episode["Name"] if "Name" in episode.keys() else "NONAME"),
                "Id": episode["Id"],
                "Number": episode["IndexNumber"],
            }
        )

    return output


def generate_seasons_sanity_check(seasons_to_delete):
    output = {}

    for season in seasons_to_delete:
        if season["SeriesId"] not in output.keys():
            output[season["SeriesId"]] = {
                "Name": (
                    season["SeriesName"] if "SeriesName" in season.keys() else "NONAME"
                ),
                "Seasons": [],
            }
        output[season["SeriesId"]]["Seasons"].append(
            {
                "Name": (season["Name"] if "Name" in season.keys() else "NONAME"),
                "Id": season["Id"],
            }
        )
    return output


if __name__ == "__main__":
    main()
