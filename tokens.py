import requests
import pandas as pd
import math



apiDex = "https://ocean.defichain.com/v0/mainnet/poolpairs?size=1000"
apiOracle = "https://ocean.defichain.com/v0/mainnet/prices?size=1000"



def get_token_data() -> pd.DataFrame:
    pd.options.display.float_format = '{:,.2f}'.format
    df = pd.DataFrame(columns=["Asset", "DEX", "Oracle", "Size", "APR"])
    df = df.astype({"DEX": float, "Oracle": float, "Size": int, "APR": float})
    df = df.set_index('Asset')
    
    get_dex_data(df, apiDex)
    get_oracle_data(df, apiOracle)

    dusd_data = pd.Series(data={"DEX": df.loc["DFI", "Oracle"]/df.loc["DFI", "DEX"], "Oracle": 1}, name="DUSD")
    df = df.append(dusd_data, ignore_index=False)

    df['Premium'] = (df['DEX'] - df['Oracle'])/df['Oracle'] * 100
 
    return df.sort_values(by=['APR'], ascending=False)
    


def get_dex_data(df, url):
    rDex = requests.get(url).json()
    for p in rDex['data']:
        if p['tokenB']['symbol'] == "DUSD":
            token = p['tokenA']['symbol']
            price = p['priceRatio']['ba']
        elif p['tokenA']['symbol'] == "DUSD":
            token = "DFI"
            price = p['priceRatio']['ab']
        else:
            continue
        df.loc[token, "DEX"] = float(price)
        apr = p['apr']['total']
        df.loc[token, "APR"] = float(apr*100)
        size = p['totalLiquidity']['usd']
        df.loc[token, "Size"] = math.floor(float(size))
        


def get_oracle_data(df, url):
    rOracle = requests.get(url).json()
    for p in rOracle['data']:
        token = p['price']['token']
        if token in df.index:
            price = p['price']['aggregated']['amount']
            df.loc[token, "Oracle"] = float(price)


if __name__ == '__main__':
    df = get_token_data()
    print(df)
