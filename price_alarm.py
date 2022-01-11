#!/usr/local/bin/python

import requests
import re
import operator
import sys
import json
import os
import logging

from tokens import get_token_data
import price_alarm_secrets

telegram_token = price_alarm_secrets.telegram_token
telegram_chatid = price_alarm_secrets.my_chat_id


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
DATAFILE = f"{__location__}/alarm_bot.json"


# Enable logging
logger = logging.getLogger('price_alarm_bot')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('price_alarm_bot.log')
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(fh)


# for testing
TESTALARMS = [
    "DUSD < 1.1",
    "DUSD > 1",
    "DFI.DEX < 2.5",
    "QQQ.Oracle < 300",
    "arbitrage > 45",
    "DUSD/USDT < 2",
    "BTC.Oracle > 40000",
    "BTC/DFI > 10000",
    "BTC/QQQ > 1",
    "BTC.Oracle/QQQ > 1",
    "USDT/USDC < 1",
    "USDT/USDC > 1",
    "DUSD/DUSD > 1",
    "QQQ/DUSD > 1",
]



def check_conditions(alarms, chatid="", t=None) -> None:
    if not t:
        t = get_token_data()
        print(t)

    for a in alarms:
        try:
            result = parse_condition(a)(t)
            if result:
                print(result)
                telegram_send(result, chatid)
        except Exception as e:
            logger.warning(e)

def send_price_alarms() -> None:
    t = get_token_data()

    d = read_data()
    for chatid, l in d.items():
        check_conditions(l, chatid, t)


senses = {'<': operator.le, '>': operator.ge}

def parse_condition(a):
    pattern = "(?P<token>\w+)(:?\.(?P<column>\w+))?\s?(:?.\s?(?P<token2>\w+)(:?\.(?P<column2>\w+))?)?\s?(?P<sense><|>)=?\s?(?P<value>[\d.]+)"
    result = re.match(pattern, a).groupdict()
    t = result['token'].upper()
    s = result['sense']
    v = float(result['value'])
    c = result['column'] if result['column'] else "DEX"
    t2 = result['token2'].upper() if result['token2'] else None
    c2 = result['column2'] if result['column2'] else c
    return lambda df: get_price(df, s, v, t, c, t2, c2)

def get_price(df, s, v, t, c, t2, c2) -> str:
    # if we query for DUSD, return DUSD price in USD
    # computed as DFI.Oracle/DFI.DEX
    # otherwise return prices in DUSD (hence set DUSD to 1)
    if t == "DUSD" and t2 is not None:  
        num = 1
    else:
        num = df.loc[t, c]

    if t2 is None or t2 == "DUSD":
        denom = 1
    else:
        denom = df.loc[t2, c2]
    denom_str = "" if t2 is None else f"/{t2}"
    
    quot = num / denom

    if t2 == "BTC":
        price_format = '{:,.8f}'
    elif c == "Premium" or c == "APR":
        price_format = '{:,.2f}'
    else:
        price_format = '{:,.6f}'

    if senses[s](quot, v):
        return f"{t}{denom_str} ({c}): {price_format.format(quot)} ({s}= {v})"
    else:
        return ""




def telegram_send(message: str, chatid: str) -> None:
    if telegram_token and chatid:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chatid}&text={message}"
        requests.get(url).json()



def get_bot_data(args=[]) -> str:
    print(args)
    extra_cols = []
    sort = ""
    for arg in args:
        pv = arg.split("=")
        if len(pv) == 1:
            extra_cols.append(arg)
        else:
            if pv[0] == "sort":
                sort = pv[1]
    df = get_token_data()
    cols = ["DEX", "Oracle", "Premium", "APR"] + extra_cols
    if sort:
        return repr(df[cols].sort_values(by=[sort], ascending=False))
    return repr(df[cols])


def get_alarm_data(alarms=[]) -> str:
    t = get_token_data()
    r = ""
    for a in alarms:
        result = parse_condition(a)(t)
        if result:
            r += result
    return r


def read_data() -> dict:
    try:
        with open(DATAFILE, 'r') as file:
            return json.load(file)["subscribers"]
    except FileNotFoundError:
        j = {"subscribers": {}}
        write_data(j)
        return j["subscribers"]

def write_data(data: dict) -> None:
    with open(DATAFILE, 'w') as file:
        j = {"subscribers": data}
        json.dump(j, file)



if __name__ == '__main__':
    if len(sys.argv) >= 2:
        check_conditions(TESTALARMS, "")
    else:
        send_price_alarms()
    