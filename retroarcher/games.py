import json
import pathlib

import typing as t


class Entry:
    def __init__(
        self,
        name: str,
        rom_path: pathlib.Path,
        platform_name: str,
        remap: t.Optional[str] = None,
    ) -> None:
        #: The name of the game as it appears in the menu
        self.name = name
        #: The relative path to the ROM file
        self.rom_path = rom_path
        #: Name of the platform - this is an alias which is expected to
        #: be matched up with a `platform_name` given in the settings file.
        self.platform_name = platform_name
        #: Name of a `remap`. Again, remaps are defined in settings files.
        #: They are unique to each emulator.
        self.remap = remap

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "platform_name": self.platform_name,
            "remap": self.remap,
            "rom_path": str(self.rom_path),
        }


class GameListLoadOp:
    def __init__(
        self, root_path: pathlib.Path, play_lists: t.Dict[str, t.List[Entry]]
    ) -> None:
        self.root_path = root_path
        self.play_lists = play_lists


def load(file_path: pathlib.Path) -> GameListLoadOp:
    with open(file_path, "r") as f:
        content = json.loads(f.read())

    play_lists: t.Dict[str, t.List[Entry]] = {}

    for playlist_name, data in content.items():
        play_lists[playlist_name] = [
            Entry(
                name=element["name"],
                rom_path=pathlib.Path(element["rom_path"]),
                platform_name=element["platform_name"],
                remap=element.get("remap"),
            )
            for element in data
        ]

    directory = file_path.parent

    return GameListLoadOp(directory, play_lists)
