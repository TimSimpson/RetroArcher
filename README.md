# RetroArcher

RetroArch is cool, but configuring it is basically a never ending Hell (IMO please don't send hate mail). This helps configure RetroArch for you.

## Usage

RetroArcher uses two types of JSON files for configuration:

* A file for defining RetroArch configurations on the computer you're currently using. This has info such as the path to the various playlists files, which cores you prefer to use for each system, and stuff like that.
* A list of all games which can be transformed into a RetroArch play list. If you have a shared library of games this file can also be the same between machines.

You then invoke it like this:

    poetry run retroarcher --games ~/games/games.json --settings ~/retroarcher-settings/laptop/settings.json

## Settings File

The settings file must be JSON data with a single root dictionary containing the following keys:

* "playlists_path" - path to the playlists directory to output .tpl files.
* "remaps_path" - optional path to RetroArch's config remaps directory.
* "platforms" - a list of dictionaries that look like this:

    * platform_name - a nickname for a platform, like "NES"
    * emu_name - The name of the emulator you prefer, like "Nestopia"
    * lib_path - the path to the DLL or SO file for the emulator.
    * remaps - An optional dictionary, where each key is the nickname given to the type of config remap for various games (more below)

Here's an example settings.json file:

```
{
    "playlists_path": "C:/retroarch/playlists",
    "remaps_path": "C:/retroarch/config/remaps",
    "platforms": [
        {
            "platform_name": "nes",
            "emu_name": "Nestopia",
            "lib_path": "C:/retroarch/cores/nestopia_libretro.dll",
            "remaps": {
                "ergo": {
                    "file_path": "ergo.rmp"
                },
                "rpg": {
                    "file_path": "rpg.rmp"
                }
            }
        }
    ]
}
```

The remaps "file_path" points to a file relative to the settings file (so if our file above was called `settings.json`, RetroArcher would expect to see `ergo.rmp` and `rpg.rmp` alongside it in the same directory).

RetroArch creates remap files on a per core or per game basis; RetroArcher lets you create a remap file for a single game, and then copy it to multiple games. See below for more.

## Games List File

This is another JSON file with a dictionary. There each string is a playlist name (in other words, it becomes a playlist file) with a list of dictionaries that keep the following format:

* "name" - name of the game
* "platform_name" - The platform the game is on (this must line up with the "platform_name" used in the settings file)
* "rom_path" - the path to the ROM relative to the games list file.
* "remap" - Optional. See below.

Here's an example:

```
{
    "NES Games": [
        {
            "name": "Streemerz-v02",
            "platform_name": "nes",
            "rom_path": "NES/streemerz-v02.nes",
            "remap": "ergo"
        }
    ]
}
```

## Control Remaps

If "remap" is specified in the games list file, and if the platform data in the settings file for RetroArcher also had a remap specified with the same name, RetroArcher will copy the remap file specified in settings to RetroArch's remap directory (also specified in settings) with the file name being identical to the steam of the ROM file name, with ".rmp" given as the extension.

This allows you to specify complex remapping (such as control remappings) that can be reused for a number of games at once. For example, I use a remapping called `ergo` which maps the NES, Gameboy, etc's B and A buttons to the X and A buttons on an X-Input controller (which lets the thumb lay across both the way it could on a Super NES control pad's Y and B buttons).

The .rmp file can be created inside of RetroArch, but if you want to know what the `ergo.rmp` file looks like (because honestly, anyone who doesn't want to lay their thumb across a modern control pad this way is insane) here it is:

```
input_player1_btn_b = "8"
input_player1_btn_y = "0"
input_player1_btn_x = "0"
input_libretro_device_p1 = "1"
input_player1_analog_dpad_mode = "0"
input_libretro_device_p2 = "1"
input_player2_analog_dpad_mode = "0"
input_libretro_device_p3 = "1"
input_player3_analog_dpad_mode = "0"
input_libretro_device_p4 = "1"
input_player4_analog_dpad_mode = "0"
input_libretro_device_p5 = "1"
input_player5_analog_dpad_mode = "0"
```


## Developing and running tests

This uses [poetry](https://python-poetry.org/).

Install that, then run this to execute all the tests:

    poetry run task checks

Run it with this:

    poetry run retroarcher

If you use Sublime Text there's a project file which works on both Linux and Windows.
