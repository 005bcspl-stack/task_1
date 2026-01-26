###############################################################################
###############################################################################
from key import api_k, api_s, access_token
import key
import pickle
###############################################################################

API_KEY = api_k #enter api_key madan
ACCESS_TOKEN =access_token  #enter madan
###############################################################################

import time
import logging
import pandas as pd
import os
import calendar

from datetime import datetime, date  # Add 'date' to the import
from datetime import timedelta
from datetime import datetime, timedelta



from dateutil.relativedelta import relativedelta, TH, WE, MO, TU, FR
from kiteconnect import KiteConnect
from zoneinfo import ZoneInfo

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
    #print(quote)
    #print(quote[tradingSymbol]['last_price'])
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0

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
    # Place an intraday market order on NSE
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
    # Place an intraday market order on NSE
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
    # Place an intraday market order on NSE
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

# Place market Order
def place_market_order(symbol,buy_sell,quantity,exchange="NSE"):
    # Place an intraday market order on NSE
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

##### FOR reference ###########################################################################################
#def track_straddle_order()
# for a given strike - get the symbol and hence the price
##### FOR reference ###########################################################################################

def find_last_tuesday_of_current_month():
    """
    Finds the date of the last Tuesday of the current month and year.
    Returns:
        datetime.date: The date of the last Tuesday.
    """
    today = datetime.today()  # Use date.today() instead of datetime.date.today()
    year = today.year
    month = today.month
    # Get the number of days in the current month.
    last_day_of_month = calendar.monthrange(year, month)[1]
    # Iterate backward from the last day of the month.
    for day in range(last_day_of_month, 0, -1):
        date_to_check = date(year, month, day)  # Use date() instead of datetime.date()
        # Tuesday corresponds to the number 1 in the weekday() method.
        if date_to_check.weekday() == 1:
            return date_to_check
    return None
instrumentsList = None
def find_last_tuesday_of_next_month():
    today = datetime.today()
    first_next_month = today.replace(day=1) + relativedelta(months=1)
    year = first_next_month.year
    month = first_next_month.month
    last_day = calendar.monthrange(year, month)[1]

    for day in range(last_day, 0, -1):
        d = date(year, month, day)
        if d.weekday() == 1:  # Tuesday
            return d

    return None

def getprice_symbol(atm_strike):
    global t_ltpce, t_ltppe, expiry_date,t_symbol_cep,t_symbol_pep,t_symbol_ce,t_symbol_pe
    today = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    year = today.year
    month = today.month
    print("---test")
    print(today)
    print(year)
    print(month)
    
    # Use last Tuesday of the month for expiry
    expiry_date = find_last_tuesday_of_current_month()
    
    if today.date() > expiry_date:    
       expiry_date = find_last_tuesday_of_next_month()
         
    if expiry_date is None:
        print("ERROR: Could not find last Tuesday of the month")
        return
    
    print(f"Using expiry date: {expiry_date}")
    
    t_symbol_ce = get_symbols(expiry_date, 'NIFTY', atm_strike, 'CE')  # Remove .date() call
    if t_symbol_ce is None:
        print(f"ERROR: Could not find CE symbol for strike {atm_strike}")
        return
        
    t_symbol_pe = get_symbols(expiry_date, 'NIFTY', atm_strike, 'PE')  # Remove .date() call
    if t_symbol_pe is None:
        print(f"ERROR: Could not find PE symbol for strike {atm_strike}")
        return
        
    print(t_symbol_ce)
    print(t_symbol_pe)
    t_symbol_cep="NFO:"+t_symbol_ce
    t_symbol_pep="NFO:"+t_symbol_pe
    t_ltpce=getCMP(t_symbol_cep)
    t_ltppe=getCMP(t_symbol_pep)
    print("ltpce=",t_ltpce)
    print("ltppe=",t_ltppe)



#def getprice_symbol(atm_strike):
#    global t_ltpce,t_ltppe
#
#    #weekly expiry
#    next_wednesday_expiry = datetime.today() + relativedelta(weekday=WE(1))
#    t_symbol_ce = get_symbols(next_wednesday_expiry.date(), 'BANKNIFTY', atm_strike, 'CE')
#    t_symbol_pe = get_symbols(next_wednesday_expiry.date(), 'BANKNIFTY', atm_strike, 'PE')
#
#
#    #monthly expiry
#    #t_next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))
#    #t_symbol_ce = get_symbols(t_next_thursday_expiry.date(), 'BANKNIFTY', atm_strike, 'CE')
#    #t_symbol_pe = get_symbols(t_next_thursday_expiry.date(), 'BANKNIFTY', atm_strike, 'PE')
#
#
#    print(t_symbol_ce)
#    print(t_symbol_pe)
#    t_symbol_cep="NFO:"+t_symbol_ce
#    t_symbol_pep="NFO:"+t_symbol_pe
#
#    t_ltpce=getCMP(t_symbol_cep)
#    t_ltppe=getCMP(t_symbol_pep)
#    print("ltpce=",t_ltpce)
#    print("ltppe=",t_ltppe)
#


if __name__ == '__main__':


    print("straddle trades - waiting for 10:30AM")
    # wait till 11AM
    while (True):
        break # break test
        now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 10) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 30):
            break

    # Create the file name date and time as variable
    now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    print("now =", now)
    lfile = now.strftime("./logs/%Y%m%d_1030_n_straddle.txt")
    day= now.strftime("%Y%m%d")

    print("creating log file --> ", lfile)
    with open(f'{lfile}', 'w', encoding='utf-8') as f:
        f.write('--------------------- starting---------------------------' + '\n')
        f.write(f'{now.strftime(" %d - %m - %Y ::: %H:%M:%S ")}'+ '\n')
        f.write('---------------------------------------------------------' + '\n')

    papertrade=1
    # Find ATM Strike of Nifty
    # Error atm_strike = round(getCMP('NSE:NIFTY 50'), -2)
    atm_strike= round_to_multiple(getCMP('NSE:NIFTY 50'), 50)
    print("SPOT nearest 100:", atm_strike)

    print("----------------------------------------------------->")
       # check prices - diff between CE/PE premium, chosse the closest
    getprice_symbol(atm_strike)
    t0_ce=t_ltpce
    t0_pe=t_ltppe
    getprice_symbol(atm_strike+50)
    t1_ce=t_ltpce
    t1_pe=t_ltppe
    getprice_symbol(atm_strike-50)
    t2_ce=t_ltpce
    t2_pe=t_ltppe
    print("------------------")
    print(t0_ce)
    print(t0_pe)

    print(t1_ce)
    print(t1_pe)
    print(t2_ce)
    print(t2_pe)
    diff0=abs(t0_ce-t0_pe)
    diff1=abs(t1_ce-t1_pe)
    diff2=abs(t2_ce-t2_pe)

    if(diff0 < diff1) and (diff0 < diff2):
        f_ltpce=t0_ce
        f_ltppe=t0_pe
        atm_strike=atm_strike

    if(diff1 < diff0) and (diff1 < diff2):
        f_ltpce=t1_ce
        f_ltppe=t1_pe
        atm_strike=atm_strike+100

    if(diff2 < diff0) and (diff2 < diff1):
        f_ltpce=t2_ce
        f_ltppe=t2_pe
        atm_strike=atm_strike-100


    print("------------------")
    print(f_ltpce)
    print(f_ltppe)
    print("------------------")
    print("----------------------------------------------------->")


    #placing the real trades
    #place_order(symbol_ce, 0, 50, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
     #           KiteConnect.ORDER_TYPE_MARKET)

    #place_order(symbol_pe, 0, 50, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
     #           KiteConnect.ORDER_TYPE_MARKET)

#    symbol_ce = f_ltpce
#    symbol_pe = f_ltppe
#
#    print(symbol_ce)
#    print(symbol_pe)

    getprice_symbol(atm_strike)
    #SL trades
    symbol_cep=t_symbol_cep #"NFO:"+symbol_ce
    symbol_pep=t_symbol_pep #"NFO:"+symbol_pe
    symbol_ce = t_symbol_ce
    symbol_pe = t_symbol_pe
    #ltpce=getCMP('NFO:NIFTY23AUG19300CE') 
    ltpce=getCMP(symbol_cep)
    ltppe=getCMP(symbol_pep)
    print("ltpce=",ltpce)
    print("ltppe=",ltppe)
    slce=round((round(1.7*ltpce,2)*100)/10,0)/10
    slpe=round((round(1.7*ltppe,2)*100)/10,0)/10
    print("slce=",slce)
    print("slpe=",slpe)
    slce_tprice = slce + 0.5
    slpe_tprice = slpe + 0.5
    print("slce trig price=",slce_tprice)
    print("slpe trig price=",slpe_tprice)

    #SL limit orders 
    #place_order_sl_limit(symbol_ce, slce, 50, kite.TRANSACTION_TYPE_BUY, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
     #           KiteConnect.ORDER_TYPE_SL,slce_tprice)
    #place_order_sl_limit(symbol_pe, slpe, 50, kite.TRANSACTION_TYPE_BUY, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
     #           KiteConnect.ORDER_TYPE_SL,slpe_tprice)

    print("sl limit orders placed") 
       # wait till 3:10PM
    slcehit=0
    slpehit=0
    plmax=0
    plmin=10000

    while (True):
        time.sleep(30)
        time.sleep(30)
        now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        #check the orders complete and display
        #check the orders pending and display
        #check traded orders has SL ?
        #check positions matching as per the orders
        #check staddle positions every 5minutes and log to file
        pl=0
        ltpce1= getCMP(symbol_cep)
        ltppe1= getCMP(symbol_pep)

        if(ltpce1 > slce):
             slcehit=1

        if(ltppe1 > slpe):
             slpehit=1

        if(slcehit==1):
            ltpce1=slce
        if(slpehit==1):
            ltppe1=slpe

        plce = (ltpce - ltpce1)*75
        plpe = (ltppe - ltppe1)*75

        plce=round(plce,2)
        plpe=round(plpe,2)

        pl= plce + plpe


        if(pl>plmax):
            plmax=pl
        if(pl<plmin):
            plmin=pl
        hr=datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour
        min=datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute
        print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce}:{getCMP(symbol_cep)}:{plce}:{slcehit} - {symbol_pe}:{ltppe}:{getCMP(symbol_pep)}:{plpe}:{slpehit}:-- > {pl}::{plmax}::{plmin}'),file=open(f'{lfile}', 'a'))
        print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce}:{getCMP(symbol_cep)}:{plce}:{slcehit} - {symbol_pe}:{ltppe}:{getCMP(symbol_pep)}:{plpe}:{slpehit}:-- > {pl}::{plmax}::{plmin}'))

        #exit the logs post the market
        if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 15) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 30):
            break  
    if(papertrade==0):
        for i in kite.orders():
            if (i['product'] == "MIS"):
                if(i['status']== "COMPLETE"):
                    tdsymbol = i['tradingsymbol']
                    tdprice = i['average_price']
                    tdsymbol1="NFO:"+tdsymbol
                    tdltp=getCMP(tdsymbol)
                    print(tdsymbol,tdprice,tdltp, (tdprice-tdltp)*50)
                    pl=pl+(tdprice-tdltp)*50
        print("outstanding MIS PL --",pl)
        print("-----------------------------------------")

        #outstanding PL as per positions
        b=[]
        b=kite.positions()['net']
        b=pd.DataFrame(b)
        PL=sum(b['pnl'])
        print('\n')
        print(b['tradingsymbol'],b['pnl'])
        print("outstanding PL as per pos:",PL)
        print((f'{day}:{hr}:{min}::{PL}'),file=open(f'{lfile}', 'a'))
        print("-----------------------------------------")

        # waiting for exist

        if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 15) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 10):
            print("exit positions")             
