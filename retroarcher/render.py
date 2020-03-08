import os
import pathlib
import shutil
import typing as t

from . import games
from . import settings


class Result:
    def __init__(self) -> None:
        self._platform_misses: t.List[games.Entry] = []
        self._successes = 0
        self._errors = 0
        self._playlists = 0
        self._skipped_playlists = 0
        self._missing_remaps: t.List[games.Entry] = []

    def add_missing_remap(self, entry: games.Entry) -> None:
        self._missing_remaps.append(entry)

    def add_playlist(self) -> None:
        self._playlists += 1

    def add_skipped_playlist(self) -> None:
        self._skipped_playlists += 1

    def add_success(self) -> None:
        self._successes += 1

    def add_missing_platform(self, entry: games.Entry) -> None:
        self._platform_misses.append(entry)
        self._errors += 1

    @property
    def errors(self) -> int:
        return self._errors

    @property
    def missing_platforms(self) -> t.List[games.Entry]:
        return self._platform_misses

    @property
    def missing_remaps(self) -> t.List[games.Entry]:
        return self._missing_remaps

    @property
    def playlists(self) -> int:
        return self._playlists

    @property
    def skipped_playlists(self) -> int:
        return self._skipped_playlists

    @property
    def successes(self) -> int:
        return self._successes


class Renderer:
    def __init__(
        self, settings_arg: settings.Settings, game_list: games.GameListLoadOp
    ) -> None:
        self._settings = settings_arg
        self._game_list_load_op = game_list

    def run(self) -> Result:
        self._result = Result()

        for pl_name, entries in self._game_list_load_op.play_lists.items():
            self._write_playlist(
                pl_name, entries, self._game_list_load_op.root_path
            )

        return self._result

    def _write_playlist(
        self,
        pl_name: str,
        entries: t.List[games.Entry],
        root_rom_path: pathlib.Path,
    ) -> None:
        file_path = self._settings.playlists_path / f"{pl_name}.lpl"

        entry_count_per_playlist = 0
        with open(file_path, "w") as f:
            for entry in entries:
                try:
                    emu = self._settings.platforms[entry.platform_name]
                except KeyError:
                    self._result.add_missing_platform(entry)
                    continue

                f.write(str(root_rom_path / entry.rom_path) + "\n")
                f.write(entry.name + "\n")
                f.write(str(emu.lib_path) + "\n")
                f.write(emu.emu_name + "\n")
                # Not sure what this is:
                f.write("\n")
                # For some reason, the playlist must be written
                f.write(str(file_path) + "\n")
                self._result.add_success()
                entry_count_per_playlist += 1

                if entry.remap:
                    if self._settings.remaps_path is None:
                        self._result.add_missing_remap(entry)
                        continue

                    try:
                        remap = emu.remaps[entry.remap]
                    except KeyError:
                        self._result.add_missing_remap(entry)
                        continue

                    src_file = remap.file_path
                    dst_dir = self._settings.remaps_path / emu.emu_name
                    os.makedirs(dst_dir, exist_ok=True)
                    dst_file = (
                        self._settings.remaps_path
                        / emu.emu_name
                        / f"{entry.rom_path.stem}.rmp"
                    )
                    shutil.copy(src_file, dst_file)

        if entry_count_per_playlist == 0:
            os.remove(file_path)
            self._result.add_skipped_playlist()
        else:
            self._result.add_playlist()
