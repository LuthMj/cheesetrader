# cheesetrader
Scalping Perfected ~ matheauFX

NOTE: CheeseTrader only works for Windows, no other OS support, sorry.

> Make sure you watch this video first before doing stupid stuff on your pc you cnut: https://youtu.be/L7YeSmx9kcA

# Installation Steps
1. Download and Install MetaTrader 5: https://www.metatrader5.com/en/download - close the program after installation.
2. Install the latest release of CheeseTrader.
3. To make sure that MetaTrader 5 always starts up with AlgoTrading enabled, place custom.ini from the metatrader5_resources directory in the directory: "c:\Program Files\MetaTrader 5\Config"
4. Install Elgato Stream Deck software for your particular device: https://www.elgato.com/en/downloads
5. Install the CheeseTrader Elgato Stream Deck plugin.
6. Configure the Stream Deck with the help of Elgato Stream Deck.
7. Run CheeseTrader -> Start menu -> CheeseTrader.
8. Happy scalping!

# Advanced
 
## Build the Python Executable
You will need to have installed:
* Python 3.8.x or higher

Then in a PowerShell Terminal change to the src\api directory in this repo.

Install requirements:
```
pip install fastapi
pip install uvicorn[standard]
pip install pyinstaller
pip install pillow
```

Then run
```
pyinstaller cheesetrader.spec
```

## Build the Stream Deck Plugin
Change in a Command terminal to src\streamdeck in this repo and run:

```
DistributionTool.exe -b -i io.cheesetrader.api.sdPlugin -o release
```

Plugin is located in the release directory.

## Log File
When running CheeseTrader, a logfile is created and rotated after every 10 files in this location:
C:\Users<yourusername>\AppData\Local\Temp\cheesetrader
