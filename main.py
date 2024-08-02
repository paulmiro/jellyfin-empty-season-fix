import sys
import json

import requests
import urllib3


def main():
    setup()

    if "--skip-episode-deletion" not in sys.argv:
        episode_deletion()
    if "--skip-season-deletion" not in sys.argv:
        season_deletion()


def episode_deletion():
    episodes_to_delete = [
        episode
        for episode in get_virtual_episodes()["Items"]
        if episode_is_placeholder(episode)
    ]

    sanity_check = generate_sanity_check(episodes_to_delete)

    with open("episodes_sanity_check.json", "w") as f:
        json.dump(sanity_check, f, indent=2)

    print(f"Found {len(episodes_to_delete)} episodes to delete")

    print(
        "This script will PERMANENTLY delete the episodes listed in episodes_sanity_check.json\nPlease take a good look at it and make sure the listed episodes are actually placeholders"
    )

    if (
        input(
            'Please type "I want to continue" to delete the episodes or anything else to exit: '
        ).lower()
        == "i want to continue"
    ):
        pass
    else:
        sys.exit(0)


def season_deletion():
    pass


def generate_sanity_check(episodes_to_delete):
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
            "fields": "Path",
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


def delete_episodes(episode_ids):
    if len(episode_ids) == 0:
        return
    if len(episode_ids) > 100:
        raise Exception("Cannot delete more than 100 episodes at a time")
    requests.request(
        "DELETE",
        URL + "/Items",
        headers=AUTH_HEADERS,
        verify=VERYFY_SSL,
        params={
            "ids": ",".join(episode_ids),
        },
    )


def episode_is_placeholder(episode):
    return episode["LocationType"] == "Virtual" and "Path" not in episode.keys()


if __name__ == "__main__":
    main()
