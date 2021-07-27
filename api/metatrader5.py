import MetaTrader5 as mt5


def connect():
    if mt5.initialize():
        print("Connected to MetaTrader 5!")
    elif not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()


def open_position(symbol, order_type, size):

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()
    
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            mt5.shutdown()
            quit()

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
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("Order Send Successfully!")
    else:
        print("mt5.order_send() failed, error code =", mt5.last_error())
        quit()


def close_all_positions():
    positions = mt5.positions_get()
    for position in positions:

        if(position.type == mt5.ORDER_TYPE_BUY):
            ticket = position.ticket
            symbol = position.symbol
            type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        elif(position.type == mt5.ORDER_TYPE_SELL):
            ticket = position.ticket
            symbol = position.symbol
            type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask

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
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print("Order Send Successfully!")
        else:
            print("mt5.order_send() failed, error code =", mt5.last_error())
            quit()
