# Star Wars Battlefront - Lua Decompiler

This repository contains 2 programs:
1. `unmunge.py`: Unmunges *.lvl files and extracts the script chunks (scr_). The result is stored in a pickled Lua 4.0 Chunk structure containing the bytecode.
2. `luadec.py`: Decompiles a pickled Lua 4.0 Chunk structure and produces a Lua 4.0 script file.

# References
- [https://www.lua.org/manual/4.0/manual.html](https://www.lua.org/manual/4.0/manual.html)
- [https://www.lua.org/source/4.0/](https://www.lua.org/source/4.0/)