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
    parser.add_argument(
        "--show-missing-platforms",
        help="Print out everytime an entry in the game list refers to a "
        "platform not in the settings file",
        action="store_true",
    )
    parser.add_argument(
        "--show-missing-remaps",
        help="Print out a warning everytime an entry in the game list "
        "refers to a remap that is not specified in the settings file",
        action="store_true",
    )
    args = parser.parse_args(sys.argv[1:])

    s = settings.load(pathlib.Path(args.settings).expanduser())
    g = games.load(pathlib.Path(args.games).expanduser())

    result = render.Renderer(s, g).run()

    if args.show_missing_platforms:
        for entry in result.missing_platforms:
            print(f'Could not find platform "{entry.platform_name}" for:')
            print(
                textwrap.indent(json.dumps(entry.to_json(), indent=4), "    ")
            )

    if args.show_missing_remaps:
        for entry in result.missing_remaps:
            print(f'Could not find remap "{entry.remap}" for:')
            print(
                textwrap.indent(json.dumps(entry.to_json(), indent=4), "    ")
            )

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


if __name__ == "__main__":
    main()
