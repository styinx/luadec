# Star Wars Battlefront - Lua Decompiler

This repository contains 2 programs:
1. `unmunge.py`: Unmunges *.lvl files and extracts the script chunks (scr_). The result is stored in a pickled Lua 4.0 Chunk structure containing the bytecode.
2. `luadec.py`: Decompiles a pickled Lua 4.0 Chunk structure and produces a Lua 4.0 script file.

# References
- [https://www.lua.org/manual/4.0/manual.html](https://www.lua.org/manual/4.0/manual.html)
- [https://www.lua.org/source/4.0/](https://www.lua.org/source/4.0/)

# Usage

## Unmunge munged files

The only *.lvl files that contain lua scripts are the mission.lvl and the shell.lvl (at least to my knowledge).
Use SleepKillers swbf-unmunge tool (https://github.com/PrismaticFlower/swbf-unmunge)[https://github.com/PrismaticFlower/swbf-unmunge] to unpack a munged *.lvl file.
Use the *.script files (in the munged folder) as input for the unmunge.py program.

The following script unpacks the lua byte code from the script file.
```shell
python unmunge.py bes1a.script
> bes1a (5947 bytes)
```

The output `bes1a (5947 bytes)` tells you that one lua script was found. 
The script will create a folder called `bes1a/` into the execution directory.
In this folder a `bes1a.dat` file will be created that contains a pickled Python structure used for the decompilation step.
Have a look in `shared.py` to see how the structure looks like. 

## Decompile the lua byte code

The following script creates a lua script from the dat file.
```shell
python luadec.py bes1a/bes1a.dat
> bes1a/bes1a.lua
```

The output `bes1a/bes1a.lua` tells you that one lua script file was created from the `*.dat` file.
The script will create one lua file for each dat file.

Batch processing is possible by giving a file wildcard and a folder:
```shell
python luadec.py *.dat shell
> shell\ifelem_mappreview.lua
> shell\ifelem_titlebar_large.lua
> shell\ifs_attract.lua
> shell\ifs_boot.lua
> shell\ifs_credits.lua
> shell\ifs_difficulty.lua
> shell\ifs_instant_side.lua
> shell\ifs_instant_top.lua
> shell\ifs_legal.lua
> shell\ifs_login.lua
> shell\ifs_main.lua
> shell\ifs_meta_battle.lua
> shell\ifs_meta_configs.lua
> shell\ifs_meta_deathstar.lua
> shell\ifs_meta_load.lua
> shell\ifs_meta_main.lua
> shell\ifs_meta_main_display.lua
> shell\ifs_meta_main_input.lua
> shell\ifs_meta_main_logic.lua
> shell\ifs_meta_movie.lua
> shell\ifs_meta_new_load.lua
> shell\ifs_meta_opts.lua
> shell\ifs_meta_top.lua
> shell\ifs_meta_tutorial.lua
> shell\ifs_missionselect.lua
> shell\ifs_missionselect_pcmulti.lua
> shell\ifs_movietrans.lua
> shell\ifs_mp.lua
> shell\ifs_mpgs_login.lua
> shell\ifs_mpgs_pclogin.lua
> shell\ifs_mp_autonet.lua
> shell\ifs_mp_gameopts.lua
> shell\ifs_mp_joinds.lua
> shell\ifs_mp_leaderboard.lua
> shell\ifs_mp_leaderboarddetails.lua
> shell\ifs_mp_lobbyds.lua
> shell\ifs_mp_lobby_quick.lua
> shell\ifs_mp_main.lua
> shell\ifs_mp_maptype.lua
> shell\ifs_mp_sessionlist.lua
> shell\ifs_pckeyboard.lua
> shell\ifs_sp.lua
> shell\ifs_split_map.lua
> shell\ifs_split_profile.lua
> shell\ifs_sp_briefing.lua
> shell\ifs_sp_era.lua
> shell\ifs_sp_yoda.lua
> shell\ifs_start.lua
> shell\ifs_tutorials.lua
> shell\ifs_unlockables.lua
> shell\ifs_vkeyboard.lua
> shell\metagame_ai.lua
> shell\metagame_state.lua
> shell\metagame_util.lua
> shell\missionlist.lua
> shell\popups_meta_main.lua
> shell\popup_ok_large.lua
> shell\shell_interface.lua
```
