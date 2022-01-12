# DeFiChain Price Alarm

A Telegram bot to send out price alarms for the DeFiChain DEX.
It gets the data from the Ocean API. Currently only DFI, DUSD and the stock tokens are supported.

Please let me know if you have questions or comments!

## Using the Bot

The bot is deployed on an AWS machine.
You can find (und use) it [here](https://t.me/defichain_price_alarm_bot).
Please be aware that this is a very early prototype and there are no guarantees. So use it at your own risk. (The main risk is getting annoyed, but you can always `/unsubscribe`...)

It checks conditions every 5 minutes and sends out a notification *every time* the condition is satisfied.

* Use `/show` to get a list of current token prices (DEX and Oracle) -- warning: still looking very ugly ;-)...
* Use `/subscribe {token} </> {price}` to subscribe to price notifications. For example, 

        /subscribe DFI < 2.5
        
    gets you notified whenever the DFI (on the DEX) falls below 2.5 DUSD. You can subscribe to Oracle prices by specifying `{token}.Oracle` (or the current premium using `{token}.Premium` -- note that the premium is given in percent). For example 
    
        /subscribe TSLA.Oracle > 1500
    
    gets you notified if the Oracle price for Tesla rises above 1500 USD. Use

        /subscribe DUDS.Premium < 10
    
    to get notified if the DUSD premium is below 10% (i.e., if the price of DUSD does not exceed 1.1).

    By default, DEX prices are always considered *in DUSD*, except for the price of DUSD itself, which is computed as DFI.Oracle/DFI.DEX.

    You can subscribe to quotients of prices, i.e., prices in specified *in another asset*: For example, use `BTC/DFI` to get the price of BTC in DFI or `USDC/USDT` for the quotient of USDC and USDT.

* Use `/unsubscribe` to unsubscribe from all notifications.
* Use `/list` to get a list of your active subscriptions.


## TODOs and Known Issues

* The AWS machine is very small (t2.micro because of free tier). Not sure how much load it can handle... 
* Use a real database (currently: data is dumped to a json file)
* Allow muting, editing of alarms and configuring how often the notification is sent (e.g. once, always, once per day?)
* Error handling:
    * When subscribing, check that the token exists
* The messages could look much nicer...


## Buy me a drink

If this is useful for you, you can support me and the project with DFI donations:

dDw3VfUmhEdUd5FqP1Cko2FAbheEWmXif1
