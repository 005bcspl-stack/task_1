##############################################################################################################################################################
from key import api_k, api_s, access_token
import key
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
    else:
        return 0.0

# Global variables for DUAL crossover strategy
sl_hit = 0
tgt_hit = 0
crossover_price = 0
crossover_detect = 0
total_bundles = 0
sl_price = 0
target = 0
stop_pl_update = 0
loss_when_sl_hit = 0
sl_value = 0
profit_at_target = 0
log_rows_for_excel = []
ce_prev = 0
pe_prev = 0
bp_output = 0
sl_output = 0
qty_output = 0
pl_output = 0
initial_ce_price = 0
initial_pe_price = 0
log_rows_for_excel.append(["TIME", "EVENT", "BP", "SL", "QTY", "PL", "TRADE_TYPE"])  # Added TRADE_TYPE column
current_event = "NONE"
trade_type = "NONE"  # NEW: Track which type of trade (CE or PE)
AMOUNT_INVESTED = 5000
EACH_BUNDLE = 35

# NEW: DUAL CROSSOVER DETECTION FUNCTION
def dual_crossover_detect(ce_ltp, pe_ltp):
    global ce_prev, pe_prev, crossover_detect, tgt_hit, sl_hit, bp_output, sl_output, qty_output, pl_output
    global stop_pl_update, crossover_price, total_bundles, sl_price, target, loss_when_sl_hit, profit_at_target, sl_value, current_event, timestamp, trade_type
    
    AMOUNT_INVESTED = 5000
    EACH_BUNDLE = 35
    
    # DUAL CROSSOVER LOGIC: Check for BOTH CE>PE and PE>CE
    if crossover_detect == 0:  # No active trade
        
        # Case 1: CE crosses ABOVE PE (CE > PE)
        if ce_prev < pe_prev and ce_ltp > pe_ltp and crossover_detect == 0:
            crossover_detect = 1
            trade_type = "CE_TRADE"  # Trading CE option
            crossover_price = ce_ltp
            
            sl_price = round(0.9 * crossover_price, 2)
            sl_value = round(crossover_price - sl_price, 2)
            
            if sl_value <= 0:
                current_event = "SL_ERR"
            else:
                target = round(crossover_price + 2 * sl_value, 2)
                total_bundles = round(AMOUNT_INVESTED / (EACH_BUNDLE * sl_value))
                total_bundles = max(total_bundles, 1)
                loss_when_sl_hit = round((sl_price - crossover_price) * EACH_BUNDLE * total_bundles, 2)
                profit_at_target = round((target - crossover_price) * EACH_BUNDLE * total_bundles, 2)
                current_event = "CE_CROSSOVER"
                bp_output = crossover_price
                sl_output = sl_price
                qty_output = total_bundles
                pl_output = 0.0
                print(f"*** CE > PE CROSSOVER DETECTED! Buying CE at {crossover_price} ***")
        
        # Case 2: PE crosses ABOVE CE (PE > CE)
        elif ce_prev > pe_prev and ce_ltp < pe_ltp and crossover_detect == 0:
            crossover_detect = 1
            trade_type = "PE_TRADE"  # Trading PE option
            crossover_price = pe_ltp
            
            sl_price = round(0.9 * crossover_price, 2)
            sl_value = round(crossover_price - sl_price, 2)
            
            if sl_value <= 0:
                current_event = "SL_ERR"
            else:
                target = round(crossover_price + 2 * sl_value, 2)
                total_bundles = round(AMOUNT_INVESTED / (EACH_BUNDLE * sl_value))
                total_bundles = max(total_bundles, 1)
                loss_when_sl_hit = round((sl_price - crossover_price) * EACH_BUNDLE * total_bundles, 2)
                profit_at_target = round((target - crossover_price) * EACH_BUNDLE * total_bundles, 2)
                current_event = "PE_CROSSOVER"
                bp_output = crossover_price
                sl_output = sl_price
                qty_output = total_bundles
                pl_output = 0.0
                print(f"*** PE > CE CROSSOVER DETECTED! Buying PE at {crossover_price} ***")
    
    # Monitor active trades
    elif crossover_detect == 1 and tgt_hit == 0 and sl_hit == 0:
        
        if trade_type == "CE_TRADE":
            # Monitoring CE trade
            current_event = "CE_CROSSOVER"
            if stop_pl_update == 0:
                pl_output = round((ce_ltp - crossover_price) * EACH_BUNDLE * total_bundles, 2)
            if stop_pl_update == 1:
                pl_output = pl_output
                
            # Check CE price against SL and target
            if ce_ltp <= sl_price and tgt_hit == 0:
                sl_hit = 1
                current_event = "CE_SLHIT"
                stop_pl_update = 1
                print(f"*** CE STOP LOSS HIT at {ce_ltp} ***")
            elif ce_ltp >= target and sl_hit == 0:
                tgt_hit = 1
                current_event = "CE_TARGETHIT"
                stop_pl_update = 1
                print(f"*** CE TARGET HIT at {ce_ltp} ***")
                
            bp_output = ce_ltp
            
        elif trade_type == "PE_TRADE":
            # Monitoring PE trade
            current_event = "PE_CROSSOVER"
            if stop_pl_update == 0:
                pl_output = round((pe_ltp - crossover_price) * EACH_BUNDLE * total_bundles, 2)
            if stop_pl_update == 1:
                pl_output = pl_output
                
            # Check PE price against SL and target
            if pe_ltp <= sl_price and tgt_hit == 0:
                sl_hit = 1
                current_event = "PE_SLHIT"
                stop_pl_update = 1
                print(f"*** PE STOP LOSS HIT at {pe_ltp} ***")
            elif pe_ltp >= target and sl_hit == 0:
                tgt_hit = 1
                current_event = "PE_TARGETHIT"
                stop_pl_update = 1
                print(f"*** PE TARGET HIT at {pe_ltp} ***")
                
            bp_output = pe_ltp
        
        sl_output = sl_price
        qty_output = total_bundles
        
    elif crossover_detect == 1 and (tgt_hit == 1 or sl_hit == 1):
        # Trade completed - maintain last values
        current_event = current_event
        pl_output = pl_output
        bp_output = bp_output
        sl_output = sl_output
        qty_output = qty_output
    
    # Logging code
    formatted_bp = f"{bp_output:.1f}" if isinstance(bp_output, (int, float)) else str(bp_output)
    formatted_sl = f"{sl_output:.1f}" if isinstance(sl_output, (int, float)) else str(sl_output)
    formatted_pl = f"{pl_output:.1f}" if isinstance(pl_output, (int, float)) else str(pl_output)
    
    console_row = f"{timestamp} | {current_event} | {trade_type} | BP: {formatted_bp} | SL: {formatted_sl} | Qty: {str(qty_output)} | PL: {formatted_pl}"
    print(console_row)
    log_rows_for_excel.append([timestamp, current_event, bp_output, sl_output, qty_output, pl_output, trade_type])
    
    ce_prev = ce_ltp
    pe_prev = pe_ltp

if __name__ == '__main__':
    paper_trade=1
    plot=1
    debug = 1
    offline=0
    time_val = []
    plce_val = []
    plpe_val = []
    runpl_val = []
    chart_saved = False
    i = 0
    log_header_format = "{:<8} {:<15} {:<10} {:<8} {:<8} {:<6} {:<10}"
    log_row_format_num = "{:<8} {:<15} {:<10} {:<8.1f} {:<8.1f} {:<6} {:<10.1f}"
    log_row_format_str = "{:<8} {:<15} {:<10} {:<8} {:<8} {:<6} {:<10}"
    start_time1 = datetime.strptime("09:45", "%H:%M")
    end_time1 = datetime.strptime("15:30", "%H:%M")
    
    print("DUAL CROSSOVER Strategy - CE>PE & PE>CE - waiting for 9:45AM")
    print("*** Will automatically detect both CE>PE and PE>CE crossovers ***")
    
    # wait till 9:45AM
    while (True):
        break
        if debug == 1:
          break # break test
        now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 9) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 45):
            break
    
    # Create the file name date and time as variable
    now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if offline == 0:
        OUTPUT_FILE = now.strftime("./logs_Sensex/Excel_File/%Y%m%d_%H%M_dual_crossover_sensex100_straddle_online.xlsx")
    else:
        OUTPUT_FILE = now.strftime("./logs_Sensex/Excel_File/%Y%m%d_%H%M_dual_crossover_sensex100_straddle_offline.xlsx")

    if offline == 0:
        lfile = now.strftime("./logs_Sensex/lfile/%Y%m%d_%H%M_dual_crossover_sensex100_straddle_online.txt")
    else:
        lfile = now.strftime("./logs_Sensex/lfile/%Y%m%d_%H%M_dual_crossover_sensex100_straddle_offline.txt")
    day = now.strftime("%Y%m%d")
    print("creating log file --> ", lfile)
    
    os.makedirs('./logs_Sensex/Charts', exist_ok=True)
    os.makedirs('./logs_Sensex/Excel_File', exist_ok=True)
    os.makedirs('./logs_Sensex/lfile', exist_ok=True)


    with open(f'{lfile}', 'w', encoding='utf-8') as f:
        f.write('--------------------- DUAL CROSSOVER Strategy Starting (CE>PE & PE>CE) ---------------------------' + '\n')
        f.write(f'{now.strftime(" %d - %m - %Y ::: %H:%M:%S ")}'+ '\n')
        f.write('---------------------------------------------------------' + '\n')
    
    filename = lfile #'./logs/dual_crossover_0945_bn_straddle.txt'
    # Append-adds at last
    file1 = open("./logs_Sensex/dual_straddle_945am", "a")
    papertrade=0
    
    # Find ATM Strike of Bank Nifty
    atm_strike= round_to_multiple(getCMP('BSE:SENSEX'), 100) 
    print("SPOT nearest 100:", atm_strike)
    print("----------------------------------------------------->")
    
    # check prices - diff between CE/PE premium, choose the closest
    getprice_symbol(atm_strike)
    t0_ce=t_ltpce
    t0_pe=t_ltppe
    getprice_symbol(atm_strike+100)
    t1_ce=t_ltpce
    t1_pe=t_ltppe
    getprice_symbol(atm_strike-100)
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
    print("Selected ATM Strike:", atm_strike)
    print("CE Premium:", f_ltpce)
    print("PE Premium:", f_ltppe)
    print("------------------")
    print("----------------------------------------------------->")

    initial_ce_price = f_ltpce
    initial_pe_price = f_ltppe
    
    #get expiry symbols
    symbol_ce = get_symbols(expiry_date, 'SENSEX', atm_strike, 'CE')
    symbol_pe = get_symbols(expiry_date, 'SENSEX', atm_strike, 'PE')
    
    print(f"Trading Symbols:")
    print(f"CE: {symbol_ce}")
    print(f"PE: {symbol_pe}")
    
    # we got the PE and CE ATM strike price & their symbol and values
    # wait for the cross over // select the leg which crosses other leg
    
    #SL trades
    symbol_cep="BFO:"+symbol_ce
    symbol_pep="BFO:"+symbol_pe
    ltpce=getCMP(symbol_cep)
    ltppe=getCMP(symbol_pep)
    print("ltpce=",ltpce)
    print("ltppe=",ltppe)
    
    slce=round((round(1.4*ltpce,2)*100)/10,0)/10
    slpe=round((round(1.4*ltppe,2)*100)/10,0)/10
    print("slce=",slce)
    print("slpe=",slpe)
    
    slce_tprice = slce + 0.5
    slpe_tprice = slpe + 0.5
    print("slce trig price=",slce_tprice)
    print("slpe trig price=",slpe_tprice)
    
    slcehit=0
    slpehit=0
    plmax=0
    plmin=10000
    print("debug")

    # chart declarations ---
    # declaration for the plot
    if offline==1:
        INPUT_FILE ="edata_b.xlsx"
        df = pd.read_excel(INPUT_FILE, dtype={"DATE": str, "TIME": str})
        df["DATETIME"] = pd.to_datetime(df["DATE"] + " " + df["TIME"], format="%Y%m%d %H:%M:%S")
        start_time = datetime.strptime("09:30", "%H:%M").time()
        end_time = datetime.strptime("15:30", "%H:%M").time()
        df = df[(df["DATETIME"].dt.time >= start_time) & (df["DATETIME"].dt.time <= end_time)].reset_index(drop=True)
        df["LTPCE"] = df["LTPCE"].astype(float)
        df["LTPPE"] = df["LTPPE"].astype(float)
    
    print("\n" + "="*80)
    print("DUAL CROSSOVER STRATEGY ACTIVE")
    print("Monitoring for BOTH CE>PE and PE>CE crossovers...")
    print("="*80 + "\n")
    fig = None
    ax = None
    line1 = None
    line2 = None
    line3 = None
    try:
        while (True):
            #offline - time scale kept 0.01 sec for faster debug of code with test data
            #online (offline=0) - timescale = real, in this case = 30min
            if offline==1:
                time.sleep(0.001)
            else:
                time.sleep(30)
                time.sleep(30)

            print("-->");
            now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))

            pl = 0
            ltpce1 = getCMP(symbol_cep)
            ltppe1 = getCMP(symbol_pep)

            if(ltpce1 > slce):
                slcehit = 1
            if(ltppe1 > slpe):
                slpehit = 1
            if(slcehit == 1):
                ltpce1 = slce
            if(slpehit == 1):
                ltppe1 = slpe

            plce = (ltpce - ltpce1)*30
            plpe = (ltppe - ltppe1)*30
            pl = plce + plpe

            if(pl > plmax):
                plmax = pl
            if(pl < plmin):
                plmin = pl

            hr = datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour
            min = datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute
            ltpce = round(ltpce,2)
            plce = round(plce,2)
            ltppe = round(ltppe,2)
            plpe = round(plpe,2)

            if offline == 1:
                if i >= len(df):
                    i = 0
                    output_df = pd.DataFrame(log_rows_for_excel[1:], columns=log_rows_for_excel[0])
                    # Dynamic summary for Excel
                    summary_data_for_excel = [
                        ["", "", "", "", "", "",""],
                        ["--- Crossover Summary ---", "", "", "", "", "",""],
                        ["Cross Over", crossover_price, "", "", "", "",""],
                        ["SL", sl_price, "", "", "", "",""],
                        ["Target", target, "", "", "", "",""],
                        ["Amount Invested", AMOUNT_INVESTED, "", "", "", "",""],
                        ["Each Bundle", EACH_BUNDLE, "", "", "", "",""],
                        ["Total Bundles", total_bundles, "", "", "", "",""],
                        ["Loss When SL Hit", loss_when_sl_hit, "", "", "", "",""],
                        ["SL Value", sl_value, "", "", "", "",""],
                        ["PL When Target Hit", profit_at_target, "", "", "", "",""],
                        ["profit at the end of trade", pl_output, "", "", "", "",""],
                        ["Target Hit", "Yes" if tgt_hit == 1 else "No", "", "", "", "",""],
                        ["SL Hit", "Yes" if sl_hit == 1 else "No", "", "", "", "",""],
                        ["Trade Type", trade_type, "", "", "", "",""],
                    ]
                    # Print readable summary in terminal
                    print("\n--- Crossover Summary ---")
                    print(f"Cross Over: {crossover_price}")
                    print(f"SL: {sl_price}")
                    print(f"Target: {target}")
                    print(f"Amount Invested: {AMOUNT_INVESTED}")
                    print(f"Each Bundle: {EACH_BUNDLE}")
                    print(f"Total Bundles: {total_bundles}")
                    print(f"Loss When SL Hit: {loss_when_sl_hit}")
                    print(f"SL Value: {sl_value}")
                    print(f"PL When Target Hit: {profit_at_target}")
                    print(f"Profit at the end of trade: {pl_output}")
                    print(f"Target Hit: {'Yes' if tgt_hit == 1 else 'No'}")
                    print(f"SL Hit: {'Yes' if sl_hit == 1 else 'No'}")
                    print(f"Trade Type: {trade_type}")
                    summary_df = pd.DataFrame(summary_data_for_excel, columns=log_rows_for_excel[0])
                    output_df = pd.concat([output_df, summary_df], ignore_index=True)
                    output_df.to_excel(OUTPUT_FILE, index=False)
                    # Save chart before breaking
                    if offline == 0: 
                        chart_filename = now.strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_online.png")
                    else:
                        chart_filename = now.strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_offline.png")
                    fig.savefig(chart_filename, dpi=300)
                    print(f"Chart saved as: {chart_filename}")
                    chart_saved = True
                    break
                timestamp = df.loc[i, "TIME"]
                ltpce1 = df.loc[i, "LTPCE"]
                ltppe1 = df.loc[i, "LTPPE"]
                i = i+1
            if offline == 1:
                hr, min = timestamp.split(":")[:2]
            if offline == 0:
                timestamp = f"{hr}:{min}"
            if debug == 1:
                if offline == 1:
                    print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce1}:{symbol_pe}:{ltppe1}'))
                    print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce1}:{symbol_pe}:{ltppe1}'),file=open(f'{lfile}', 'a'))
                else:
                    print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce1}:{symbol_pe}:{ltppe1}'))
                    print((f'{day}:{hr}:{min}::{symbol_ce}:{ltpce1}:{symbol_pe}:{ltppe1}'),file=open(f'{lfile}', 'a'))
            print("last line read:", read_last_line_efficient(filename))
            rline = read_last_line_efficient(filename)
            separator = ':'
            plce_new = get_seventh_field(rline, separator)
            plpe_new = get_twelfth_field(rline, separator)
            print(plce_new)
            print(plpe_new)
            try:
                plce_new_float = float(plce_new) if plce_new is not None else 0.0
            except (ValueError, TypeError):
                plce_new_float = 0.0
                print(f"Warning: Could not convert '{plce_new}' to float, using 0.0")
            try:
                plpe_new_float = float(plpe_new) if plpe_new is not None else 0.0
            except (ValueError, TypeError):
                plpe_new_float = 0.0
                print(f"Warning: Could not convert '{plpe_new}' to float, using 0.0")
            dual_crossover_detect(plce_new_float, plpe_new_float)
            if pl_output != 0:
                norm_pl_output = pl_output / (EACH_BUNDLE * total_bundles)
            else:
                norm_pl_output = pl_output
            try:
                runpl_new_float = float(norm_pl_output) if norm_pl_output is not None else 0.0
            except (ValueError, TypeError):
                runpl_new_float = 0.0
                print(f"Warning: Could not convert '{norm_pl_output}' to float, using 0.0")
            time_str = str(f'{hr}:{min}')
            format = "%H:%M"
            temp_time = datetime.strptime(time_str, format)
            time_val.append(temp_time)
            plce_val.append(plce_new_float)
            plpe_val.append(plpe_new_float)
            runpl_val.append(runpl_new_float)
            if plot == 1:
                try:
                    if line1 is None or line2 is None or line3 is None:
                        fig, ax = plt.subplots(figsize=(16, 8))
                        line1, = ax.plot(time_val, plce_val, '-', linewidth=2, marker='o', markersize=3, label='CE Price')
                        line2, = ax.plot(time_val, plpe_val, '-', linewidth=2, marker='s', markersize=3, label='PE Price')
                        line3, = ax.plot(time_val, runpl_val, '-', linewidth=2, marker='x', markersize=3, label='run PL')
                        ax.set_xlabel('Time', fontsize=12)
                        ax.set_ylabel('Option Price', fontsize=12)
                        ax.set_title(f'DUAL CROSSOVER Strategy - {symbol_ce}', fontsize=14)
                        ax.grid(True, alpha=0.3)
                        ax.legend(loc='upper right')
                        
                        # Summary box on left side of chart
                        summary_text = (
                            f"Initial CE: {initial_ce_price:.2f}\n"
                            f"Initial PE: {initial_pe_price:.2f}\n"
                            f"Trade Type: {trade_type}\n"
                            f"Current CE: {plce_val[-1]:.2f}\n"
                            f"Current PE: {plpe_val[-1]:.2f}\n"
                            f"Entry Price: {crossover_price:.2f}\n"
                            f"SL: {sl_value:.2f}\n"
                            f"Stop Loss: {sl_price:.2f}\n"
                            f"Target: {target:.2f}\n"
                            f"PL: {pl_output:.2f}\n"
                            f"Running PL: {runpl_val[-1]:.2f}\n"
                            f"Target Hit: {'Yes' if tgt_hit == 1 else 'No'}\n"
                            f"Projected Profit when target hit: {profit_at_target:.2f}\n"
                            f"SL Hit: {'Yes' if sl_hit == 1 else 'No'}\n"
                            f"Projected Loss when sl hit: {loss_when_sl_hit :.2f}"
                        )
                        ax.text(0.02, 0.98, summary_text, transform=ax.transAxes,
                                fontsize=12, verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                        
                        plt.ion()
                        plt.show()
                    else:
                        line1.set_xdata(time_val)
                        line1.set_ydata(plce_val)
                        line2.set_xdata(time_val)
                        line2.set_ydata(plpe_val)
                        line3.set_xdata(time_val)
                        line3.set_ydata(runpl_val)
                        
                        # Update summary box
                        for txt in ax.texts:
                            if 'Initial CE:' in txt.get_text():
                                summary_text = (
                                    f"Initial CE: {initial_ce_price:.2f}\n"
                                    f"Initial PE: {initial_pe_price:.2f}\n"
                                    f"Trade Type: {trade_type}\n"
                                    f"Current CE: {plce_val[-1]:.2f}\n"
                                    f"Current PE: {plpe_val[-1]:.2f}\n"
                                    f"Entry Price: {crossover_price:.2f}\n"
                                    f"SL: {sl_value:.2f}\n"
                                    f"Stop Loss: {sl_price:.2f}\n"
                                    f"Target: {target:.2f}\n"
                                    f"PL: {pl_output:.2f}\n"
                                    f"Running PL: {runpl_val[-1]:.2f}\n"
                                    f"Target Hit: {'Yes' if tgt_hit == 1 else 'No'}\n"
                                    f"Projected Profit when Target Hit: {profit_at_target:.2f}\n"
                                    f"SL Hit: {'Yes' if sl_hit == 1 else 'No'}\n"
                                    f"Projected Loss when Sl Hit: {loss_when_sl_hit :.2f}"
                                )
                                txt.set_text(summary_text)
                                break
                    
                    ax.relim()
                    ax.autoscale_view()
                    if len(time_val) > 5:
                        step = max(1, len(time_val) // 10)
                        tick_times = time_val[::step]
                        ax.set_xticks(tick_times)
                        labels = [t.strftime('%H:%M') for t in tick_times]
                        ax.set_xticklabels(labels, rotation=45, ha='right')
                    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
                    
                    # Add horizontal lines for entry prices, SL, and target
                    if crossover_detect == 1:
                        if trade_type == "CE_TRADE":
                            ax.axhline(y=initial_ce_price, color='blue', linestyle=':', alpha=0.7, label=f'Initial CE: {initial_ce_price:.2f}')
                            ax.axhline(y=sl_price, color='red', linestyle=':', alpha=0.7, label=f'SL: {sl_price:.2f}')
                            ax.axhline(y=target, color='green', linestyle=':', alpha=0.7, label=f'Target: {target:.2f}')
                        elif trade_type == "PE_TRADE":
                            ax.axhline(y=initial_pe_price, color='red', linestyle=':', alpha=0.7, label=f'Initial PE: {initial_pe_price:.2f}')
                            ax.axhline(y=sl_price, color='orange', linestyle=':', alpha=0.7, label=f'SL: {sl_price:.2f}')
                            ax.axhline(y=target, color='green', linestyle=':', alpha=0.7, label=f'Target: {target:.2f}')
                    
                    plt.tight_layout()
                    plt.subplots_adjust(bottom=0.15)
                    plt.draw()
                    plt.pause(0.1)
                except Exception as plot_error:
                    print(f"Plotting error: {plot_error}")
                    pass
            
            if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 15) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 30):
                print("EOD update writing to file")
                output_df = pd.DataFrame(log_rows_for_excel[1:], columns=log_rows_for_excel[0])
                
                # Add end-of-day summary to Excel
                eod_summary_data = [
                    ["", "", "", "", "", "", ""],
                    ["DUAL CROSSOVER STRATEGY - END OF DAY SUMMARY", "", "", "", "", "", ""],
                    ["Initial CE Price", initial_ce_price, "", "", "", "", ""],
                    ["Initial PE Price", initial_pe_price, "", "", "", "", ""],
                    ["Trade Type Executed", trade_type, "", "", "", "", ""],
                    ["Crossover Detected", "Yes" if crossover_detect == 1 else "No", "", "", "", "", ""],
                    ["Entry Price", crossover_price, "", "", "", "", ""],
                    ["SL", sl_value, "", "", "", "", ""],
                    ["Stop Loss", sl_price, "", "", "", "", ""],
                    ["Target", target, "", "", "", "", ""],
                    ["Quantity", total_bundles, "", "", "", "", ""],
                    ["Final P&L", pl_output, "", "", "", "", ""],
                    ["Target Hit", "Yes" if tgt_hit == 1 else "No", "", "", "", "", ""],
                    ["Projected Profit when Target Hit", profit_at_target, "", "", "", "", ""],
                    ["Stop Loss Hit", "Yes" if sl_hit == 1 else "No", "", "", "", "", ""],
                    ["Projected Loss when Sl Hit", loss_when_sl_hit, "", "", "", "", ""],
                ]
                eod_summary_df = pd.DataFrame(eod_summary_data, columns=log_rows_for_excel[0])
                output_df = pd.concat([output_df, eod_summary_df], ignore_index=True)
                
                output_df.to_excel(OUTPUT_FILE, index=False)
                print(f"Final data exported to {OUTPUT_FILE}")
                
                now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
                if offline == 0:
                    chart_filename = now.strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_online.png")
                else:
                    chart_filename = now.strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_offline.png")
                fig.savefig(chart_filename, dpi=300)
                print(f"Chart saved as: {chart_filename}")
                chart_saved = True
                p_apl = 0
                import subprocess
                import random
                print(pl)
                try:
                    p_apl = subprocess.check_output("cat ./logs_Sensex/dual_straddle_945am|awk 'END{print}'|awk -F \":\" '{print $19;}'",shell=True)
                    p_apl = p_apl.decode("utf-8")
                    print(p_apl)
                    p_apl = float(p_apl)
                except:
                    p_apl = 0.0
                apl = p_apl + pl
                print("Previous P&L:", p_apl)
                print("Today's P&L:", pl)
                print("Total P&L:", apl)
                eod_summary = f'{day}:{hr}:{min}::{symbol_ce}:{ltpce}:{getCMP(symbol_cep)}:{plce}:{slcehit} - {symbol_pe}:{ltppe}:{getCMP(symbol_pep)}:{plpe}:{slpehit}:-- > {pl}::{plmax}::{plmin} -->: {apl}::TRADE_TYPE:{trade_type}'
                file1.write(eod_summary + '\n')
                file1.close()
                print("\n" + "="*80)
                print("DUAL CROSSOVER STRATEGY - END OF DAY SUMMARY")
                print("="*80)
                print(f"Initial CE Price: {initial_ce_price}")
                print(f"Initial PE Price: {initial_pe_price}")
                print(f"Trade Type Executed: {trade_type}")
                print(f"Crossover Detected: {'Yes' if crossover_detect == 1 else 'No'}")
                if crossover_detect == 1:
                    print(f"Entry Price: {crossover_price}")
                    print(f"Stop Loss: {sl_price}")
                    print(f"Target: {target}")
                    print(f"Quantity: {total_bundles}")
                    print(f"Final P&L: {pl_output}")
                    print(f"Target Hit: {'Yes' if tgt_hit == 1 else 'No'}")
                    print(f"Stop Loss Hit: {'Yes' if sl_hit == 1 else 'No'}")
                break
                
        if(papertrade == 0):
            print("\nLive Trading Summary:")
            for i in kite.orders():
                if (i['product'] == "MIS"):
                    if(i['status'] == "COMPLETE"):
                        tdsymbol = i['tradingsymbol']
                        tdprice = i['average_price']
                        tdsymbol1 = "NFO:" + tdsymbol
                        tdltp = getCMP(tdsymbol)
                        trade_pl = (tdprice-tdltp)*50
                        print(f"Symbol: {tdsymbol}, Entry: {tdprice}, Current: {tdltp}, P&L: {trade_pl}")
                        pl = pl + trade_pl
            b = []
            b = kite.positions()['net']
            b = pd.DataFrame(b)
            PL = sum(b['pnl'])
            for idx, row in b.iterrows():
                if row['quantity'] != 0:
                    print(f"Symbol: {row['tradingsymbol']}, P&L: {row['pnl']}")
            print((f'{day}:{hr}:{min}::{PL}'),file=open(f'{lfile}', 'a'))
            print("-" * 40)
            if(datetime.now(tz=ZoneInfo('Asia/Kolkata')).hour == 14) and (datetime.now(tz=ZoneInfo('Asia/Kolkata')).minute == 55):
                print("Exiting all positions at 2:55 PM...")
                try:
                    positions = kite.positions()['net']
                    for position in positions:
                        if position['quantity'] != 0:
                            symbol = position['tradingsymbol']
                            qty = abs(position['quantity'])
                            if position['quantity'] > 0:
                                place_market_order(symbol, "sell", qty, "NFO")
                                print(f"Sold {qty} of {symbol}")
                            else:
                                place_market_order(symbol, "buy", qty, "NFO")
                                print(f"Bought {qty} of {symbol}")
                except Exception as e:
                    print(f"Error exiting positions: {e}")
                    
        print("\n" + "="*80)
        print("DUAL CROSSOVER STRATEGY COMPLETED")
        print("Check log files for detailed analysis:")
        print(f"- Main log: {lfile}")
        print(f"- Summary log: ./logs_Sensex/dual_straddle_945am")
        if offline == 1:
            print(f"- Excel_offline output: {OUTPUT_FILE}")
        else:
            print(f"- Excel_online output: {OUTPUT_FILE}")
        print("="*80)
    finally:
        if 'fig' in locals() and fig is not None and not chart_saved:
            if offline ==1:
                chart_filename = datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_offline.png")
            else:
                chart_filename = datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime("./logs_Sensex/Charts/%Y%m%d_%H%M%S_dual_crossover_sensex100_straddle_online.png")
            fig.savefig(chart_filename, dpi=300)
            print(f"Chart saved as: {chart_filename}")

