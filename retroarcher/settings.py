import json
import pathlib

import typing as t


class Remap:
    def __init__(self, remap_name: str, file_path: pathlib.Path) -> None:
        #: Name of the remap. This alias will need to match entries in the
        #: game list.
        self.name = remap_name
        #: An absolute file path (though the settings file will store it
        #: as a relative file path from the settings file directory) to a
        #: remap file
        self.file_path = file_path

    @classmethod
    def from_json(
        cls, root_path: pathlib.Path, remap_name: str, j_dict: dict
    ) -> "Remap":
        file_path = root_path / pathlib.Path(j_dict["file_path"])
        return Remap(remap_name=remap_name, file_path=file_path)

    def to_json(self) -> dict:
        return {"file_path": str(self.file_path)}


def remap_dict_from_json(
    root_path: pathlib.Path, j_dict: t.Dict[str, dict]
) -> t.Dict[str, Remap]:
    return {
        remap_name: Remap.from_json(
            root_path=root_path, remap_name=remap_name, j_dict=data
        )
        for remap_name, data in j_dict.items()
    }


def remap_dict_to_json(remaps: t.Dict[str, Remap]) -> dict:
    return {remap.name: remap.to_json() for name, remap in remaps.items()}


class Emu:
    def __init__(
        self,
        platform_name: str,
        emu_name: str,
        lib_path: pathlib.Path,
        remaps: t.Dict[str, Remap],
    ) -> None:
        self.platform_name = platform_name
        self.emu_name = emu_name
        self.lib_path = lib_path
        self.remaps = remaps

    def to_json(self) -> dict:
        return {
            "platform_name": self.platform_name,
            "emu_name": self.emu_name,
            "lib_path": self.lib_path,
            "remaps": remap_dict_to_json(self.remaps),
        }


class Settings:
    def __init__(
        self,
        playlists_path: pathlib.Path,
        remaps_path: t.Optional[pathlib.Path],
        platforms: t.Dict[str, Emu],
    ) -> None:
        self.playlists_path = playlists_path
        self.remaps_path = remaps_path
        self.platforms = platforms

    # def _write(
    #     self, pl_name: str, entries: t.List[games.Entry], root_rom_path: pathlib.Path
    # ) -> None:
    #     file_path = self.playlists_path / f"{pl_name}.lpl"
    #     with open(file_path, "w") as f:
    #         for entry in entries:
    #             try:
    #                 emu = self.platforms[entry.platform_name]
    #             except KeyError as ke:
    #                 raise KeyError(
    #                     f'Could not find platform "{entry.platform_name}" '
    #                     f"in entry {entry.to_json()}"
    #                 ) from ke

    #             f.write(os.path.join(root_rom_path, entry.rom_path) + "\n")
    #             f.write(entry.name + "\n")
    #             f.write(str(emu.lib_path) + "\n")
    #             f.write(emu.emu_name + "\n")
    #             # Not sure what this is:
    #             f.write("\n")
    #             # For some reason, the playlist must be written
    #             f.write(str(file_path) + "\n")

    # def write_playlists(self, game_list: games.GameListLoadOp) -> None:
    #     for pl_name, entries in game_list.play_lists.items():
    #         self._write(pl_name, entries, game_list.root_path)


def load(file_path: pathlib.Path) -> Settings:
    """Loads a settings file, returning the platforms."""
    with open(file_path, "r") as f:
        content = json.loads(f.read())

    file_path_directory = file_path.parent

    platforms: t.Dict[str, Emu] = {}

    for data in content["platforms"]:
        remaps = remap_dict_from_json(
            file_path_directory, data.pop("remaps", {})
        )
        emu = Emu(remaps=remaps, **data)
        platforms[emu.platform_name] = emu

    remaps_path = (
        None
        if "remaps_path" not in content
        else pathlib.Path(content["remaps_path"]).expanduser()
    )

    return Settings(
        playlists_path=pathlib.Path(content["playlists_path"]).expanduser(),
        remaps_path=remaps_path,
        platforms=platforms,
    )
