import json
import os
import pathlib
import shutil
import sys
import tempfile
import textwrap
import typing as t

import pytest

from retroarcher import main


TEST_CONFIGS = pathlib.Path(__file__).parent / "configs"


class CliOutput:
    def __init__(self) -> None:
        self.exit_code: int = -1
        self.output: str = ""


CliFunc = t.Callable[[t.List[str]], CliOutput]


@pytest.fixture(autouse=True)
def cli(capsys: t.Any, monkeypatch: t.Any) -> CliFunc:
    class GotoEnd(BaseException):
        pass

    def cli(args: t.List[str]) -> CliOutput:
        monkeypatch.setattr(sys, "argv", args)
        output = CliOutput()

        def get_code(code: int) -> None:
            output.exit_code = code
            raise GotoEnd

        monkeypatch.setattr(sys, "exit", get_code)

        try:
            main.main()
        except GotoEnd:
            pass

        roe = capsys.readouterr()
        output.output = roe.out + roe.err
        return output

    return cli


@pytest.fixture
def temp_dir() -> pathlib.Path:
    if False:
        with tempfile.TemporaryDirectory() as td:
            return pathlib.Path(td)
    return pathlib.Path("/tmp/poo")


def _copy_fake_configs(temp_dir: pathlib.Path) -> pathlib.Path:
    """
    Copies the fake config files into a temporary directory.
    The config files specify the location of actual retroarch configs, which
    will be overwritten.

    Because this is a unit test we can't hard code that path and need to
    rewrite it so the overwriting happens in a temporary directory the unit
    tests control.

    So this function loads the settings files, changes some paths to match the
    temporary directory, and then saves the file.

    The end result is the temporary directory has the settings and remap files.
    The game list file still lifes in __file__ / configs.
    """
    # For this test, we pretend that retroarch lives here:
    fake_retroarch_home = temp_dir / "retroarch"
    # This is where we expect RetroArcher to write files:
    play_list_dir = fake_retroarch_home / "playlists"
    remaps = fake_retroarch_home / "config" / "remaps"

    os.makedirs(play_list_dir, exist_ok=True)
    os.makedirs(remaps, exist_ok=True)

    # The static test file has {retroarch_home} in place of where a hard coded
    # directory would be (for example, on Linux this would typically be
    # `~/.config/retroarch`).
    # We're going to change it to the temporary directory created by the tests.
    with open(TEST_CONFIGS / "mycomputer-settings.json", "r") as rf:
        settings_contents = json.loads(rf.read())
    for key in ["playlists_path", "remaps_path"]:
        settings_contents[key] = settings_contents[key].format(
            retroarch_home=str(fake_retroarch_home)
        )

    with open(temp_dir / "mycomputer-settings.json", "w") as wf:
        wf.write(json.dumps(settings_contents))

    for remap_file in ["ergo.rmp", "rpg.rmp"]:
        shutil.copyfile(TEST_CONFIGS / remap_file, temp_dir / remap_file)

    return temp_dir


def _load_file(path: pathlib.Path) -> str:
    with open(path, "r") as f:
        return f.read()


def _assert_playlists_created_correctly(temp_dir: pathlib.Path) -> None:
    gameboy_lpl = _load_file(
        temp_dir / "retroarch" / "playlists" / "Gameboy.lpl"
    )
    assert (
        textwrap.dedent(
            f"""
        {TEST_CONFIGS}/GB/DryMouth.gb
        Dry Mouth
        /usr/lib/x86_64-linux-gnu/libretro/gambatte_libretro.so
        Gambatte

        {temp_dir}/retroarch/playlists/Gameboy.lpl
        """
        ).strip()
        == gameboy_lpl.strip()
    )

    NES_Games_lpl = _load_file(
        temp_dir / "retroarch" / "playlists" / "NES Games.lpl"
    )
    assert (
        textwrap.dedent(
            f"""
        {TEST_CONFIGS}/NES/streemerz-v02.nes
        Streemerz-v02
        C:/RetroArch/cores/nestopia_libretro.dll
        Nestopia

        {temp_dir}/retroarch/playlists/NES Games.lpl
        {TEST_CONFIGS}/NES/guardia.nes
        Guadia Quest
        C:/RetroArch/cores/nestopia_libretro.dll
        Nestopia

        {temp_dir}/retroarch/playlists/NES Games.lpl
        """
        ).strip()
        == NES_Games_lpl.strip()
    )


def _assert_files_match(a: pathlib.Path, b: pathlib.Path) -> None:
    with open(a, "r") as file_a:
        contents_a = file_a.read()
    with open(b, "r") as file_b:
        contents_b = file_b.read()
    assert contents_a == contents_b


def _assert_remaps_created_correctly(temp_dir: pathlib.Path) -> None:
    _assert_files_match(
        TEST_CONFIGS / "rpg.rmp",
        temp_dir
        / "retroarch"
        / "config"
        / "remaps"
        / "Gambatte"
        / "DryMouth.rmp",
    )
    _assert_files_match(
        TEST_CONFIGS / "rpg.rmp",
        temp_dir
        / "retroarch"
        / "config"
        / "remaps"
        / "Nestopia"
        / "guardia.rmp",
    )
    _assert_files_match(
        TEST_CONFIGS / "ergo.rmp",
        temp_dir
        / "retroarch"
        / "config"
        / "remaps"
        / "Nestopia"
        / "streemerz-v02.rmp",
    )


def test_create_files(temp_dir: pathlib.Path, cli: CliFunc) -> None:
    _copy_fake_configs(temp_dir)
    actual = cli(
        [
            "--settings",
            str(temp_dir / "mycomputer-settings.json"),
            "--games",
            str(TEST_CONFIGS / "gamelist.json"),
        ]
    )
    assert (
        textwrap.dedent(
            """
        Summary:
            Added 3 out of 3 entries (0 skipped)
            Added 2 out of 2 playlists (0 skipped)
            Missed 0 remap(s)
        """
        ).strip()
        == actual.output.strip()
    )
    assert 0 == actual.exit_code

    _assert_playlists_created_correctly(temp_dir)
    _assert_remaps_created_correctly(temp_dir)


class TestBadArgs:
    @staticmethod
    def test_cwith_no_args(cli: CliFunc) -> None:
        actual = cli([])
        assert 0 != actual.exit_code
        assert "usage" in actual.output
        assert "the following arguments are required" in actual.output

    @staticmethod
    def test_cwith_no_settings(cli: CliFunc) -> None:
        actual = cli(["--games", str(TEST_CONFIGS / "gamelist.json")])
        assert 0 != actual.exit_code
        assert "usage" in actual.output
        assert "the following arguments are required" in actual.output

    @staticmethod
    def test_cwith_no_games(temp_dir: pathlib.Path, cli: CliFunc) -> None:
        _copy_fake_configs(temp_dir)
        actual = cli(["--settings", str(temp_dir / "mycomputer-settings.json")])
        assert 0 != actual.exit_code
        assert "usage" in actual.output
        assert "the following arguments are required" in actual.output
