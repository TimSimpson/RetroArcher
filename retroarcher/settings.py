import json
import os
import pathlib

import typing as t

from . import games


class Emu:
    def __init__(
        self, platform_name: str, emu_name: str, lib_path: pathlib.Path
    ) -> None:
        self.platform_name = platform_name
        self.emu_name = emu_name
        self.lib_path = lib_path

    def to_json(self) -> dict:
        return {
            "platform_name": self.platform_name,
            "emu_name": self.emu_name,
            "lib_path": self.lib_path,
        }


class Settings:
    def __init__(
        self, playlists_path: pathlib.Path, platforms: t.Dict[str, Emu]
    ) -> None:
        self.playlists_path = playlists_path
        self.platforms = platforms

    def _write(
        self, pl_name: str, entries: t.List[games.Entry], root_rom_path: pathlib.Path
    ) -> None:
        file_path = self.playlists_path / f"{pl_name}.lpl"
        with open(file_path, "w") as f:
            for entry in entries:
                try:
                    emu = self.platforms[entry.platform_name]
                except KeyError as ke:
                    raise KeyError(
                        f'Could not find platform "{entry.platform_name}" '
                        f"in entry {entry.to_json()}"
                    ) from ke

                f.write(os.path.join(root_rom_path, entry.rom_path) + "\n")
                f.write(entry.name + "\n")
                f.write(str(emu.lib_path) + "\n")
                f.write(emu.emu_name + "\n")
                # Not sure what this is:
                f.write("\n")
                # For some reason, the playlist must be written
                f.write(str(file_path) + "\n")

    def write_playlists(self, game_list: games.GameListLoadOp) -> None:
        for pl_name, entries in game_list.play_lists.items():
            self._write(pl_name, entries, game_list.root_path)


def load(file_path: pathlib.Path) -> Settings:
    """Loads a settings file, returning the platforms."""
    with open(file_path, "r") as f:
        content = json.loads(f.read())

    platforms: t.Dict[str, Emu] = {}

    for data in content["platforms"]:
        emu = Emu(**data)
        platforms[emu.platform_name] = emu

    return Settings(
        playlists_path=pathlib.Path(content["playlists_path"]), platforms=platforms
    )
