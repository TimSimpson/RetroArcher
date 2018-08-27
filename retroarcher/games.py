import json
import os.path
import pathlib

import typing as t


class Entry:
    def __init__(self, name: str, rom_path: pathlib.Path, platform_name: str) -> None:
        self.name = name
        self.rom_path = rom_path
        self.platform_name = platform_name

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "platform_name": self.platform_name,
            "rom_path": self.rom_path,
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
        play_lists[playlist_name] = [Entry(**element) for element in data]

    directory = pathlib.Path(os.path.dirname(file_path))

    return GameListLoadOp(directory, play_lists)
