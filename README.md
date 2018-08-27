# RetroArcher

RetroArch is cool, but configuring it is basically a never ending Hell (IMO please don't send hate mail). This helps configure RetroArch for you.

## Usage

RetroArcher uses two types of JSON files for configuration:

* A file for RetroArch configs, ie which core to use for which system, and stuff like that.
* A game lists file which is turned into a play list.

Example:

    pipenv run retroarcher --games ~/games/games.json --settings retro-arch-for-gameboy-settings.json

## Settings File

The settings file must be JSON data with a single root dictionary containing the following keys:

* "playlists_path" - path to the playlists directory to output .tpl files.
* "platforms" - a list of dictionaries that look like this:

    * platform_name - a nickname for a platform, like "NES"
    * emu_name - The name of the emulator you prefer, like "Nestopia"
    * lib_path - the path to the DLL or SO file for the emulator.

Here's an example settings.json file:

```
{
    "playlists_path": "C:/retroarch/playlists",
    "platforms": [
        {
            "platform_name": "nes",
            "emu_name": "Nestopia",
            "lib_path": "C:/retroarch/cores/nestopia_libretro.dll"
        }
    ]
}
```

## Games List File

This is another JSON file with a dictionary. There each string is a playlist name (in other words, it becomes a playlist file) with a list of dictionaries that keep the following format:

* "name" - name of the game
* "platform_name" - The platform the game is on (this must line up with the "platform_name" used in the settings file)
* "rom_path" the path to the ROM relative to the games list file.

Here's an example:

```
{
    "NES Games": [
        {
            "name": "Streemerz-v02",
            "platform_name": "nes",
            "rom_path": "NES/streemerz-v02.nes"
        }
    ]
}
```

## Devin'

This uses pipenv.

Install that, then run this:

    pipenv install --dev
    pipenv run retroarcher <args>

Test it with:

    pipenv run retroarcher-tests

