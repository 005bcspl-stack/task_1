from key import api_k, api_s, access_token
###############################################################################
API_KEY = api_k #enter api_key madan
ACCESS_TOKEN =access_token  #enter madan
###############################################################################
import os
import time
import calendar
import logging
import pandas as pd
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta, TH, WE, MO, TU, FR
from kiteconnect import KiteConnect
import matplotlib.dates as mdates
from zoneinfo import ZoneInfo

import time
import requests

# Add these imports at the top
import pickle
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs_Nifty/kite_api_errors.log'),
        logging.StreamHandler()
    ]
)

# Add these functions after imports
def get_instruments_with_retry(kite, exchange, max_retries=3, initial_delay=1):
    for attempt in range(max_retries):
        try:
            return kite.instruments(exchange)
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to fetch instruments after {max_retries} attempts: {e}")
                raise
            delay = initial_delay * (2 ** attempt)
            logging.warning(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)

def get_cached_instruments(kite, exchange, cache_file='./logs_Nifty/instruments_cache.pkl', cache_hours=24):
    # Ensure directory exists
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
    # Check if cache file exists and is recent
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=cache_hours):
                    logging.info("Using cached instruments list")
                    return cached_data['instruments']
        except Exception as e:
            logging.error(f"Error reading cache: {e}")

    # Fetch with retry
    logging.info("Fetching instruments from API")
    instruments = get_instruments_with_retry(kite, exchange)

    # Save to cache
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'timestamp': datetime.now(),
                'instruments': instruments
            }, f)
        logging.info("Instruments list cached")
    except Exception as e:
        logging.error(f"Error saving cache: {e}")

    return instruments

# Modify get_kite function
def get_kite():
    kiteObj = KiteConnect(api_key=API_KEY)
    kiteObj.set_access_token(ACCESS_TOKEN)
    
    # Increase timeout
    import requests
    kiteObj.reqsession.request = lambda *args, **kwargs: requests.Session().request(
        *args, **kwargs, timeout=30
    )
    
    return kiteObj

# Modify get_symbols function
def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList
    print(expiry)
    print(name)
    print(strike)
    print(ins_type)
    if instrumentsList is None:
        instrumentsList = get_cached_instruments(kite, 'NFO')
    lst_b = [num for num in instrumentsList if num['expiry'] == expiry and num['strike'] == strike
             and num['instrument_type'] == ins_type and num['name'] == name]
    if not lst_b:
        raise ValueError(f"No instrument found for expiry={expiry}, name={name}, strike={strike}, type={ins_type}")
    return lst_b[0]['tradingsymbol']

# Modify getCMP function
def getCMP(tradingSymbol):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            quote = kite.quote(tradingSymbol)
            if quote:
                return quote[tradingSymbol]['last_price']
            else:
                return 0
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to get quote for {tradingSymbol} after {max_retries} attempts: {e}")
                return 0
            delay = 1 * (2 ** attempt)
            logging.warning(f"Quote attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)






def getCMPBatch(symbols, delay=2):
    """
    Keep trying to fetch LTP for multiple symbols until success.
    Returns dict {symbol: ltp}.
    """
    while True:
        try:
            quotes = kite.quote(symbols)
            return {sym: quotes[sym]["last_price"] for sym in symbols}

        except requests.exceptions.ReadTimeout:
            print(f"⚠️ Timeout fetching {symbols}, retrying in {delay}s...")
            time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Error fetching {symbols}: {e}, retrying in {delay}s...")
            time.sleep(delay)

def get_kite():
    kiteObj = KiteConnect(api_key=API_KEY)
    kiteObj.set_access_token(ACCESS_TOKEN)
    return kiteObj

kite = get_kite()
instrumentsList = None

def round_to_multiple(number, multiple):
    return multiple * round(number / multiple)

def getCMP(tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0

def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList
    print(expiry)
    print(name)
    print(strike)
    print(ins_type)
    if instrumentsList is None:
        instrumentsList = kite.instruments('BFO')
    lst_b = [num for num in instrumentsList if num['expiry'] == expiry and num['strike'] == strike
             and num['instrument_type'] == ins_type and num['name'] == name]
    return lst_b[0]['tradingsymbol']

def place_order(tradingSymbol, price, qty, direction, exchangeType, product, orderType):
    try:
        orderId = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchangeType,
            tradingsymbol=tradingSymbol,
            transaction_type=direction,
            quantity=qty,
            price=price,
            product=product,
            order_type=orderType)
        logging.info('Order placed successfully, orderId = %s', orderId)
        return orderId
    except Exception as e:
        logging.info('Order placement failed: %s', e)

def place_order_sl_limit(tradingSymbol, price, qty, direction, exchangeType, product, orderType,tprice):
    try:
        orderId = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchangeType,
            tradingsymbol=tradingSymbol,
            transaction_type=direction,
            quantity=qty,
            price=price,
            product=product,
            order_type=orderType,
            trigger_price=tprice)
        logging.info('Order placed successfully, orderId = %s', orderId)
        return orderId
    except Exception as e:
        logging.info('Order placement failed: %s', e)

##### FOR reference ###########################################################################################
def place_limit_order(symbol, buy_sell,quantity,limit_price, exchange="NSE"):
    if buy_sell == "buy":
        t_type=kite.TRANSACTION_TYPE_BUY
    elif buy_sell == "sell":
        t_type=kite.TRANSACTION_TYPE_SELL
    kite.place_order(tradingsymbol=symbol,
                    exchange=exchange,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_LIMIT,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR,
                    price=limit_price)

def place_sl_limit_order(symbol,buy_sell,quantity, price, trigger_price, exchange="NSE"):
    if buy_sell == "buy":
        t_type=kite.TRANSACTION_TYPE_BUY
    elif buy_sell == "sell":
        t_type=kite.TRANSACTION_TYPE_SELL
    kite.place_order(tradingsymbol=symbol,
                    exchange=exchange,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_SL,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR,
                    price=price,
                    trigger_price=trigger_price)

def place_sl_market_order(symbol,buy_sell,quantity, trigger_price, exchange="NSE"):
    if buy_sell == "buy":
        t_type=kite.TRANSACTION_TYPE_BUY
    elif buy_sell == "sell":
        t_type=kite.TRANSACTION_TYPE_SELL
    kite.place_order(tradingsymbol=symbol,
                    exchange=exchange,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_SLM,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR,
                    trigger_price=trigger_price)

def place_market_order(symbol,buy_sell,quantity,exchange="NSE"):
    if buy_sell == "buy":
        t_type=kite.TRANSACTION_TYPE_BUY
    elif buy_sell == "sell":
        t_type=kite.TRANSACTION_TYPE_SELL
    kite.place_order(tradingsymbol=symbol,
                    exchange=exchange,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_MARKET,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR)

def getprice_symbol(atm_strike):
    global t_ltpce,t_ltppe
    global expiry_date
    
    #today = date.today()
    #days_to_add = (3 - today.weekday() + 7) % 7
    #next_tuesday = today + timedelta(days=days_to_add)
    #expiry_date = next_tuesday

    # Find the next Thursday
    # In Python's weekday(): Monday=0, Tuesday=1, Wednesday=2, Thursday=3
    target_day_code = 3 

    today = date.today()

    # The logic calculates the number of days until the target_day_code (Thursday=3)
    # The '+ 7) % 7' ensures the result is always positive and correct for wrapping around the week.
    days_to_add = (target_day_code - today.weekday() + 7) % 7

    # Add the calculated days to today's date
    expiry_date = today + timedelta(days=days_to_add)

    print(f"Today is: {today}")
    print(f"Next (Expiry Date) is: {expiry_date}")


    t_symbol_ce = get_symbols(expiry_date, 'SENSEX', atm_strike, 'CE')
    t_symbol_pe = get_symbols(expiry_date, 'SENSEX', atm_strike, 'PE')
    print(f"Today's date is: {today}")
    print(f"The date of the next Thursday (Nifty 50 weekly expiry) is: {expiry_date}")
    print(t_symbol_ce)
    print(t_symbol_pe)
    t_symbol_cep="BFO:"+t_symbol_ce
    t_symbol_pep="BFO:"+t_symbol_pe
    t_ltpce=getCMP(t_symbol_cep)
    t_ltppe=getCMP(t_symbol_pep)
    print("ltpce=",t_ltpce)
    print("ltppe=",t_ltppe)

def read_last_line_efficient(filename):
    with open(filename, 'rb') as file:
        file.seek(0, 2)
        file_size = file.tell()
        if file_size == 0:
            return None
        file.seek(-1, 2)
        while file.tell() > 0:
            char = file.read(1)
            if char != b'\n':
                file.seek(-1, 1)
                break
            file.seek(-2, 1)
        while file.tell() > 0:
            file.seek(-1, 1)
            char = file.read(1)
            if char == b'\n':
                break
            file.seek(-1, 1)
        last_line = file.readline().decode('utf-8').strip()
        return last_line

def get_seventh_field(line, separator=':'):
    if not line:
        return None
    fields = line.split(separator)
    if len(fields) >= 3:
        try:
            return float(fields[5])
        except (ValueError, TypeError):
            return 0.0
    else:
        return 0.0

def get_twelfth_field(line, separator=':'):
    if not line:
        return None
    fields = line.split(separator)
    if len(fields) >= 3:
        try:
            return float(fields[7])
        except (ValueError, TypeError):
            return 0.0