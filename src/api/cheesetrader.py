# Standard Library Imports
import os
import subprocess
import logging
import tempfile
from logging.handlers import RotatingFileHandler
from multiprocessing import Process, freeze_support
import msvcrt
import ctypes

# Third Party Imports
import uvicorn
from fastapi import FastAPI
import MetaTrader5 as mt5


# General Configuration
temp_dir_path = f"{tempfile.gettempdir()}\\cheesetrader"
if not os.path.exists(temp_dir_path):
    os.makedirs(temp_dir_path)


logging.basicConfig(
    handlers=[RotatingFileHandler(f"{temp_dir_path}\\cheesetrader.log", maxBytes=100000, backupCount=10)],
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s",
    level=logging.DEBUG)


# Generic Functions
def disable_quickedit():
    '''
    Disable quickedit mode on Windows terminal. quickedit prevents script to
    run without user pressing keys..'''
    if not os.name == 'posix':
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            device = r'\\.\CONIN$'
            with open(device, 'r') as con:
                hCon = msvcrt.get_osfhandle(con.fileno())
                kernel32.SetConsoleMode(hCon, 0x0080)
        except Exception as e:
            logging.info('Cannot disable QuickEdit mode! ' + str(e))
            logging.info('.. As a consequence the script might be automatically paused on Windows terminal')


# MetaTrader 5 Functions
def start_metatrader():
    mt5_config_file = "C:\\Program Files\\MetaTrader 5\\Config\\custom.ini"
    if(os.path.exists(mt5_config_file)):
        logging.info("Opening MetaTrader 5 with custom INI file")
        subprocess.Popen(["C:\\Program Files\\MetaTrader 5\\terminal64.exe", "/config:", mt5_config_file])
    else:
        logging.info("Opening MetaTrader 5 without custom INI file")
        subprocess.Popen(["C:\\Program Files\\MetaTrader 5\\terminal64.exe"])


def connect():
    start_metatrader()
    if mt5.initialize():
        logging.info("Connected to MetaTrader 5!")
    elif not mt5.initialize():
        logging.info(f"initialize() failed, error code = {mt5.last_error()}")


# FastAPI Configuration
description = """
🧀 CheeseTrader is the 🚀fastest🚀 Scalping Framework in the 🌍 created for the 🧀 Community.

## Orders

You can **send buy and sell orders**.

## Positions

You can **close all positions**.
"""


# MetaTrader 5 API
def create_app() -> FastAPI:
    app = FastAPI(
                title="CheeseTrader",
                description=description,
                version="0.2.0",
                contact={
                    "name": "Richard Diphoorn",
                    "github": "rdtechie"
                },
                reload=True,
                debug=True)
    return app
    
app = create_app()


@app.get("/")
def root():
    return {"message": "Hello CheeseTrader"}


@app.put("/orders/open_order")
def open_order(symbol: str, order_type: str, size: float):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logging.warning(f"{symbol}not found, can not call order_check()")
    if not symbol_info.visible:
        logging.warning(f"{symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            logging.warning(f"symbol_select({symbol}) failed, exit")
    symbol_filling_mode_num = mt5.symbol_info(symbol).filling_mode
    if symbol_filling_mode_num == 1:
        symbol_filling_mode = mt5.ORDER_FILLING_FOK
    elif symbol_filling_mode_num == 2:
        symbol_filling_mode = mt5.ORDER_FILLING_IOC
    elif symbol_filling_mode_num == 3:
        symbol_filling_mode = mt5.ORDER_FILLING_FOK
    if(order_type == "buy"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    if(order_type == "sell"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(size),
        "type": order,
        "price": price,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": symbol_filling_mode,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"Order {result.order} succesfully send!")
    else:
        logging.warning(f"mt5.order_send() failed for order {result.order}, error code ={mt5.last_error()}")


@app.put("/positions/close_all_positions")
def close_all_positions():
    positions = mt5.positions_get()
    for position in positions:
        if(position.type == mt5.ORDER_TYPE_BUY):
            ticket = position.ticket
            symbol = position.symbol
            type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            symbol_filling_mode_num = mt5.symbol_info(symbol).filling_mode
            if symbol_filling_mode_num == 1:
                symbol_filling_mode = mt5.ORDER_FILLING_FOK
            elif symbol_filling_mode_num == 2:
                symbol_filling_mode = mt5.ORDER_FILLING_IOC
            elif symbol_filling_mode_num == 3:
                symbol_filling_mode = mt5.ORDER_FILLING_FOK
        elif(position.type == mt5.ORDER_TYPE_SELL):
            ticket = position.ticket
            symbol = position.symbol
            type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            symbol_filling_mode_num = mt5.symbol_info(symbol).filling_mode
            if symbol_filling_mode_num == 1:
                symbol_filling_mode = mt5.ORDER_FILLING_FOK
            elif symbol_filling_mode_num == 2:
                symbol_filling_mode = mt5.ORDER_FILLING_IOC
            elif symbol_filling_mode_num == 3:
                symbol_filling_mode = mt5.ORDER_FILLING_FOK
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position.volume,
            "type": type,
            "position": ticket,
            "price": price,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": symbol_filling_mode,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info("Closing All Positions Action Send Successfully!")
        else:
            logging.warning(f"Closing All Positions Action Send Failed!, error code ={mt5.last_error()}")

if __name__ == "__main__":
    freeze_support()
    disable_quickedit()
    logging.info("======== CheeseTrader Started ========")
    connect()
    uvicorn.run("cheesetrader:app",
                host="127.0.0.1",
                port=8000,
                reload=False
                )