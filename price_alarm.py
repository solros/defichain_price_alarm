import requests
import re
import operator
import sys
import json

from tokens import get_token_data
import price_alarm_secrets

telegram_token = price_alarm_secrets.telegram_token
telegram_chatid = price_alarm_secrets.my_chat_id

INTERVAL = 1800

DATAFILE = "alarm_bot.json"


# for testing
TESTALARMS = [
    "DUSD < 1.1",
    "DFI.DEX < 2.5",
    "QQQ.Oracle < 300"
]



def check_conditions(alarms, chatid="", t=get_token_data()) -> None:
    for a in alarms:
        print(a)
        try:
            result = parse_condition(a)(t)
            if result:
                print(result)
                telegram_send(result, chatid)
        except:
            pass

def send_price_alarms() -> None:
    t = get_token_data()
    print(t)

    d = read_data()
    for chatid, l in d.items():
        check_conditions(l, chatid, t)


senses = {'<': operator.le, '>': operator.ge}

def parse_condition(a):
    pattern = "(?P<token>\w+)(:?.(?P<column>\w+))?\s?(?P<sense><|>)=?\s?(?P<value>[\d.]+)"
    result = re.match(pattern, a).groupdict()
    t = result['token']
    s = result['sense']
    v = float(result['value'])
    c = result['column'] if result['column'] else "DEX"
    print(t,s,v,c)
    return lambda df: f"{t} ({c}): {df.loc[t, c]} ({s}= {v})" if senses[s](df.loc[t, c], v) else ""



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
        send_price_alarms()
    else:
        check_conditions(TESTALARMS, "")