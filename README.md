# jellyfin-empty-season-fix

python script to remove empty seasons and missing episodes from your Jellyfin library

## Warning

This script will PERMANENTLY delete data from your Jellyfin server. Do not run this script unless you have a backup of your Jellyfin database and your media files.

This script is the first time I've written anything that interacts with the Jellyfin API, I can not guarantee that it will work for you.

In other words, you should probably read the code and understand what it's doing before running it.

## Why?

All fixes for [this issue](https://github.com/jellyfin/jellyfin/issues/12208) that I've found [in this forum thread](https://forum.jellyfin.org/t-how-to-disable-empty-seasons-missing-episode-fetcher) require you to either remove and re-add the your entire library or to manually edit the database.
Directly editing the database is scary, so I wrote this script to automate the process via the Jellyfin API.

## What does it do?

1. It will check your Jellyfin for TV episodes that are in the library but not on disk (aka "Virtual") and delete them from the library.
2. It will check your Jellyfin for seasons that contain no episodes and delete them from the library.

The second step can technically be done without the first one, but because "empty" seasons usually actually contain hidden episodes, it probably won't do much on its own.

The second step could also be done by doing a metadata refresh, but I didn't want to do that because I have a bunch of custom metadata that I don't want to lose.

## Requirements

### On NixOS

simply run `nix develop` in the root of this repo, this will open a shell with all the required dependencies installed.

### On other systems

You'll need Python 3.12 (older versions may work, but I haven't tested them) and the following packages:

- requests
- urllib3

## Usage

You can run this script from any machine that has access to your Jellyfin server over the network. It doesn't need to be on the same machine as your Jellyfin server.

1. Clone this repo and `cd` into it
2. rename `config.local.json.example` to `config.local.json` and fill in the values as described in the comments
3. run `python main.py`

## Options

- `--skip-episode-deletion`: skips the episode deletion step
- `--skip-season-deletion`: skips the season deletion step

## Issues

If you run into any problems, please open an issue on this repo. I'll try to help as much as I can.
