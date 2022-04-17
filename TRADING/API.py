import requests,json,time
from binance.client import Client
from binance.enums import *
import numpy as np 
import datetime


class BApi:
# config methods 
    def __init__(self,api_config='binance_api.json'):
        print("i am binance api brrrrrrr \n\n")
        self.api_config_json=api_config # json with binance api keys
        self.read_config()
        self.client= Client(self.api_key, self.api_secret)
        self.close_residue=1 # dollar close residue 
        self.order=None

        self.system_status=self.check_status()
        #ticker - used for trading -> market_order( ticker  ) 
        # symbolg - used for getting info about balance  -> get_balance(symbol)
        self.crypto_d={
            'CARDANO':{'SYMBOL':'ADA','TICKER':'ADAUSDT'},
            'RIPPLE':{'SYMBOL':'XRP','TICKER':'XRPUSDT'},
            'TETHER':{'SYMBOL':'USDT','TICKER':'USDT'},
        }
        self.ticker_d={'XRP':'RIPPLE','ADA':'CARDANO'}
        self.ignore_tickers=['BTCDOWN','USDT','BTCUP']
        
        self.response=None
# read config file 
    def read_config(self):  
        api_config_d=json.load(open(self.api_config_json))
        self.api_key=api_config_d['api_key']
        self.api_secret=api_config_d['api_secret']
# check status 
    def check_status(self): 
        system_status = self.client.get_system_status()['status']
        return system_status 
# list available tickers 
    def get_all_tickers(self):  
        data = self.client.get_all_tickers()
        symbols = sorted([ d['symbol'] for d in data ])
        return symbols
# get price of asset 
    def get_price(self,asset): # gets a candle from a minute ago 
        symbol=self.crypto_d[asset]['TICKER']
        data=self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 minutes ago UTC")
        parse_d={'open_epoch':'','open':'','close':'','high':'','low':'','volume':'','close_epoch':''}
        d = dict(zip([k for k,v in parse_d.items()],[float(i) for i in data[0][:6] ] ))
        return d #{'open_epoch': 1643484360000, 'open': '1.06100000', 'close': '1.06100000', 'high': '1.06000000', 'low': '1.06100000', 'volume': '2649.70000000'}
# get current position
    def get_position(self,asset=''):
        """ RETURNS list of dictionaries with either all positions in a wallet or position for a symbol specified """
        if isinstance(asset,list): # when symbol is a list 
            out=[]
            for s in asset:
                out.append(self.client.get_asset_balance(asset=self.crypto_d[s]['SYMBOL']))
        if asset=='': # when no symbol was passed - get all > 0 balances 
            data= self.client.get_account()
            out=[d for d in data['balances'] if float(d['free'])>0] # 

        if isinstance(asset,str) and len(asset)>1: # if symbol was a proper string 
            out=[self.client.get_asset_balance(asset=self.crypto_d[asset]['SYMBOL'] )]
        return out # [{'asset': 'ADA', 'free': '1.26260000', 'locked': '0.00000000'}, {...},...]
# check portfolio 
    def check_positions(self):  
        positions=self.get_position(asset='')                           # get all my positions 
        filtered_positions=[]
        for d in positions:                                              # filtering non relevant positions like usdt 
            if d['asset'] in self.ignore_tickers:
                continue 
            usd_price=self.get_price(self.ticker_d[d['asset']])         # checking price of asset that i have 
            usd_position=usd_price['close']*float(d['free'])            # calculating current usd position
            if usd_position>1:                                          # if usd position > 1 dollar add to relevant positions 
                filtered_positions.append(d)
        filtered_positions.append (self.get_position(asset='TETHER')[0] ) # adding tether 
        s=sum([float(i['free']) for i in filtered_positions]) # total dollar position 
        return filtered_positions,s #[{'asset': 'ADA', 'free': '17.67600000', 'locked': '0.00000000'}, [{'asset': 'USDT', 'free': '0.04235316', 'locked': '0.00000000'}]]

    def calculate_percentage(self,base,percentage):
        # calculates amount of base that corresponds to percentage taking into account tether handling
        position=float(self.get_position(base)[0]['free'])
        current_price=1
        if base!='TETHER': # tether has no current price as it should have :) :) :) 
            current_price=self.get_price(base)['close'] 
        trade_amo=position*current_price*percentage/100
        return trade_amo
    
    # makes any order based on kwargs sent 
    def make_any_order(self,**kw):
        if kw['order_type']=='market': # market order 
            if 'base' in kw.keys():    # percentage based order  
                self.market_order_p(base=kw['base'],asset=kw['asset'],percentage=kw['percentage'],side=kw['side'],test_order=kw['test_order'])
            else: # dollar based order 
                self.market_order(asset=kw['asset'],quantity=kw['quantity'],side=kw['side'],test_order=kw['test_order'],in_dollars=kw['in_dollars'])
        elif kw['order_type']=='limit': # limit order 
            if 'base' in kw.keys():     # percenetage based order 
                self.order_limit_buy_p(asset=kw['asset'],base=kw['base'],percentage=kw['percentage'],side=kw['side'],price=kw['price'],test_order=kw['test_order'])
            else: # dollar_based order 
                self.order_limit_buy(asset=kw['asset'],quantity=kw['quantity'],side=kw['side'],price=kw['price'],test_order=kw['test_order'] )
                
            

    def order_limit_buy_p(self,asset,base,percentage,side,price,test_order):
        position=float(self.get_position(base)[0]['free'])
        trade_amo=round(position/price*percentage/100,1)
        self.make_order(kind='limit',asset=asset,quantity=trade_amo,side=side,in_dollars=False,price=price,test_order=test_order)

    def order_limit_buy(self,asset,quantity,side,price,test_order): 
        self.make_order(kind='limit',asset=asset,quantity=quantity,side=side,in_dollars=False,price=price,test_order=test_order)

    def market_order_p(self,base='CARDANO',asset='CARDANO',percentage=100,side='BUY',test_order=1):
        trade_amo=self.calculate_percentage(base=base,percentage=percentage)
        self.market_order(asset=asset,quantity=trade_amo,side=side,test_order=test_order,in_dollars=True)

    def market_order(self,asset,quantity=10,side='BUY',test_order=1,in_dollars=True):
        self.make_order(kind='market',asset=asset,quantity=quantity,side=side,test_order=test_order,in_dollars=in_dollars)

    def make_order(self,kind,asset,quantity=10,side='BUY',test_order=1,in_dollars=True,**kwargs): # places buy/sell market order  
        """ market_order(asset='CARDANO',quantity=10,type='SELL',test_order=1)"""
        if side=='BUY':
            side=SIDE_BUY
        elif side=='SELL':
            side=SIDE_SELL
        if in_dollars:
            current_price=float(self.get_price(asset)['close'])
            quantity=round(quantity/current_price,1)
        order_d={'symbol':self.crypto_d[asset]['TICKER'],'side':side,'quantity':quantity}
# test order 
        if test_order:
            print('making test order ')
            self.order=self.client.create_test_order(
                symbol=order_d['symbol'],
                side=order_d['side'],
                type=ORDER_TYPE_MARKET,
                quantity=order_d['quantity'])
            return
        
# market order 
        if kind=='market':
            print('making market order...')
            try:
                self.order=self.client.create_order(
                symbol=order_d['symbol'],
                side=order_d['side'],
                type=ORDER_TYPE_MARKET, 
                quantity=order_d['quantity'])
            except Exception as err:
                print("dupa!")
                print(err) 
#limit order 
        if kind=='limit':
            try:
                self.order=self.client.create_order(
                symbol=order_d['symbol'],
                quantity=order_d['quantity'],
                price=kwargs['price'],
                timeInForce ='GTC',
                side=order_d['side'],
                type=ORDER_TYPE_LIMIT)
                pass 
            except Exception as err:
                print('dupa!')
                print(err)
#not used 
    def close_position(self,asset=''): # sells 4 times 99% of current position 
        def close(asset,sell_qty):
            self.market_order(asset=asset,quantity=sell_qty,side='SELL',test_order=0)
        symbol_info=self.get_symbol_info(asset) # asset info 
        current_position=float(self.get_position(asset)[0]['free'])
        sell_qty=round(current_position*0.95,1)
        count=1
        while current_position>float(symbol_info['filters'][2]['minQty']) and count<5:
            close(asset=asset,sell_qty=sell_qty)
            current_position=float(self.get_position(asset)[0]['free'])
            sell_qty=round(current_position*0.99,1)
            count+=1
            time.sleep(2)
        return
 
    def get_symbol_info(self,asset):
        return self.client.get_symbol_info(self.crypto_d[asset]['TICKER'])

    def check_order_status(self): # checks if last order was filled or not 
        order_status=self.client.get_order(
        symbol=self.order['symbol'],
        orderId=self.order['orderId'])
        if order_status['status'] != 'FILLED': 
            print("dupa, order not filled!")
            print(order_status)
            raise

        
# work methods 

if __name__=="__main__":
    pass
    

