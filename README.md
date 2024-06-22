nu-EAN | An attempt at an EA Nation 1.0 master server emulator
=================================================

Based on [Battlefield: Bad Company 2 Master Server Emulator](https://github.com/Tratos/BFBC2_MasterServer) by [Tratos / B1naryKill3r](https://github.com/Tratos)

I really want to play Burnout Revenge on Xbox 360 with my friends. However despite EA still selling the game and advertising on the box art to "Take your revenge online", the servers are shut down. (This should be criminal in my opinion!)

-----------
HELP WANTED
-----------

I have no clue what the hell i'm doing, if you guys have any points I gladly appreciate it!

!!! CURRENTLY PORTING TO PYTHON 3 !!!

Module           | Version | Download
----------------:|:-------:|:------------
Python           | 3.12.3     | [Python Download](https://www.python.org/)
colorama         | latest  | pip install colorama
passlib          | latest  | pip install passlib
Twisted          | latest  | pip install Twisted
pyOpenSSL        | latest  | pip install pyOpenSSL
cffi             | latest  | pip install cffi
cryptography     | latest   | pip install cryptography
service_identity | latest   | pip install service_identity

*...or just install everything via `pip install -r requirements.txt`*

Also you have to open these ports:

Port   | Type
------:|:-------
18210  | TCP/UDP
18215  | TCP/UDP
13505  | TCP
80     | TCP


Setting up the emulator
-----------------------

- Make sure that all required ports (see above) are open
- Write the IP of the PC where the emulator will be hosted in the config.ini to the key 'emulator_ip' (overwrite "localhost") and save it
- Run `Init.py`

Setting up Client and Server
----------------------------


TODO LIST
-----------
- GDAT currently crashes
- PlayNow / pnow (PlasmaClient) - this needs a lot of research to make matchmaking functional
- More EA Messenger backend code
- lots and lots of testing
- Python3 conversion or even a rewrite entirely? //currently being worked on!!!
- Support for multiple lobbies?
