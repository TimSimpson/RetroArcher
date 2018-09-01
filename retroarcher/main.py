import argparse
import json
import pathlib
import sys
import textwrap

from . import games
from . import render
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

    result = render.Renderer(s, g).run()

    for entry in result.missing_platforms:
        print(f'Could not find platform "{entry.platform_name}" for:')
        print(textwrap.indent(json.dumps(entry.to_json(), indent=4), "    "))

    print("Summary:")
    print(
        f"    Added {result.successes} out of "
        f"{result.successes + result.errors} entries "
        f"({result.errors} skipped)"
    )
    print(
        f"    Added {result.playlists} out of "
        f"{result.playlists + result.skipped_playlists} playlists "
        f"({result.skipped_playlists} skipped)"
    )
    print(f"    Missed {len(result.missing_remaps)} remap(s)")

    sys.exit(0)
