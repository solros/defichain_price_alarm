import requests
import pandas as pd
import math



apiDex = "https://ocean.defichain.com/v0/mainnet/poolpairs?size=1000"
apiOracle = "https://ocean.defichain.com/v0/mainnet/prices?size=1000"



def get_token_data() -> pd.DataFrame:
    pd.options.display.float_format = '{:,.2f}'.format
    df = pd.DataFrame(columns=["Asset", "DEX", "Oracle", "Size", "APR", "Type", "DEXDFI", "OracleDFI"])
    df = df.astype({"DEX": float, "Oracle": float, "Size": int, "APR": float, "DEXDFI": float, "OracleDFI": float})
    df = df.set_index('Asset')
    
    get_dex_data(df, apiDex)
    get_oracle_data(df, apiOracle)

    dusd_data = pd.Series(data={"DEX": df.loc["DFI", "Oracle"]/df.loc["DFI", "DEX"], "Oracle": 1}, name="DUSD")
    df = df.append(dusd_data, ignore_index=False)

    df['Premium'] = (df['DEX'] - df['Oracle'])/df['Oracle'] * 100
 
    return df.sort_values(by=['APR'], ascending=False)
    


def get_dex_data(df, url, stocks=True, cryptos=True):
    rDex = requests.get(url).json()
    for p in rDex['data']:
        try:
            if p['tokenB']['symbol'] == "DUSD" and stocks:
                token = p['tokenA']['symbol']
                price = p['priceRatio']['ba']
                type = "stock"
            elif p['tokenA']['symbol'] == "DUSD" and stocks:
                token = "DFI"
                price = p['priceRatio']['ab']
                type = "stock"
            elif cryptos:
                token = p['tokenA']['symbol']
                priceDFI = p['priceRatio']['ba']
                type = "crypto"
            else:
                continue
                
            if type == "stock":
                df.loc[token, "DEX"] = float(price)
            elif type == "crypto":
                df.loc[token, "DEXDFI"] = float(priceDFI)
            apr = p['apr']['total']
            df.loc[token, "APR"] = float(apr*100) if apr is not None else 0
            size = p['totalLiquidity']['usd']
            df.loc[token, "Size"] = math.floor(float(size))
            df.loc[token, "Type"] = type
        except Exception as e:
            print(e)

    DFIprice = df.loc["DFI", "DEX"]
    df.loc[df['Type'] == "crypto", "DEX"] = DFIprice * df.loc[df['Type'] == "crypto", "DEXDFI"]


        


def get_oracle_data(df, url):
    rOracle = requests.get(url).json()
    for p in rOracle['data']:
        token = p['price']['token']
        if token in df.index:
            price = p['price']['aggregated']['amount']
            df.loc[token, "Oracle"] = float(price)

    DFIprice = df.loc["DFI", "Oracle"]
    df.loc[df['Type'] == "crypto", "OracleDFI"] = df.loc[df['Type'] == "crypto", "Oracle"] / DFIprice


if __name__ == '__main__':
    df = get_token_data()
    print(df)
