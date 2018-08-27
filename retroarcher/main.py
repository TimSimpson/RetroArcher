import argparse
import pathlib
import sys

from . import games
from . import settings


def main() -> None:
    parser = argparse.ArgumentParser("retroarcher")
    parser.add_argument(
        "--settings",
        help="Settings for a particular install of RetroArch",
        required=True,
    )
    parser.add_argument("--games", help="List of games.", required=True)
    args = parser.parse_args()

    s = settings.load(pathlib.Path(args.settings))
    g = games.load(pathlib.Path(args.games))

    s.write_playlists(g)
    sys.exit(0)
