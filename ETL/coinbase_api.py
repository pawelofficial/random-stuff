from logging import exception
from os import curdir
from requests.api import request
import os 

import requests
import time
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
import datetime

#from trainingdata import TrainingData
#-- 
class CoinbaseExchangeAuth(AuthBase):
    """
    returns request object with appropriate authorization for coinbase api
    """
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key=api_key
        self.secret_key=secret_key
        self.passphrase=passphrase # this should be put in context variable

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request
#--
class coinbase_api():
    """ class for getting stuff from coinbase api """
    def __init__(self,auth):
        self.base_url_ama='https://api.coinbase.com/v2'
        self.base_url_pro='https://api.pro.coinbase.com'
        self.time_format='%Y-%m-%dT%H:%M:%S.%fZ'
        self.auth=auth

    def send_request(self,url):
        """ returns get request from api """
 #       url='https://api.pro.coinbase.com/products/BTC-USD/candles?&granularity=60&start=2021-09-05T13:01:00.000000Z&end=2021-09-05T13:02:00.000000Z'
        try:
            r = requests.get(url, auth=self.auth)
        except:
            print(f"bad request trying again")
            time.sleep(3)
            r = requests.get(url, auth=self.auth)
            if r.status_code !=200:
                raise 
  #      print(f" \n your url: {url}")
        return r

    def build_candle_url(self,start_dt,end_dt,granularity=60,asset_id='BTC-USD'):
        """returns url string for  historical data aka candles with specified granularity and time frame"""
        start=start_dt.strftime(format=self.time_format)
        end=end_dt.strftime(format=self.time_format)
        candle_url=self.base_url_pro+f"/products/{asset_id}/candles?&granularity={granularity}&start={start}&end={end}"       
        return candle_url

    def get_server_time(self):
        """returns server time and server datetime object truncated to 1 minute """
        r=self.send_request(self.base_url_pro+'/time') # call to api 
        server_time=json.loads(r.text)['iso'] # server timestamp 
        server_dt=datetime.datetime.strptime(server_time,self.time_format) # server datetime object
        # truncated to 1 minute 
        server_dt=server_dt-datetime.timedelta(seconds=server_dt.second,microseconds=server_dt.microsecond)
        server_time=server_dt.strftime(format=self.time_format)
        # truncating server_dt according to trunc value 
        return server_time,server_dt
    
    def clock_gen(self,start_dt,end_dt,granularity=60):
        """returns a generator yielding start_dt and later_dt up until end_dt
        later_dt is moved forward in time with respippect to granularity to retrieve max no of data
        which is 300 candles, so for granularity = 60 which is 1m later_dt is shifted 1m*300=5h"""
        while start_dt<end_dt:
            later_dt=start_dt+datetime.timedelta(seconds=granularity*300) # so much math
            yield start_dt,later_dt
            start_dt=later_dt

    def parse_raw_data(self,raw_data,single_candle=False):
        """ parses raw data returned by api into a very nice json """
        parsed_data=json.loads(raw_data)
        
        if single_candle:
            parsed_data=[parsed_data[0]] # sometimes api returns more than one candle
        parsed_data.sort(key=lambda x:x[0]) # sorting by epoch
        f=lambda x: [float(i[x]) for i in parsed_data] # api returns list of lists
        d={}
        d['epoch']=f(0) # epoch time 
        d['timestamp']=[datetime.datetime.utcfromtimestamp(i[0]).strftime(self.time_format) for i in parsed_data]
        d['low']=f(1)  # low 
        d['high']=f(2)  # high 
        d['open']=f(3)  # open 
        d['close']=f(4) # close 
        d['volume']=f(5) # volume 
        return d

    def fetch_candles(self,start_dt,end_dt,granularity=60,asset_id='BTC-USD'):
        """ returns dictionary with raw data of candles and request metadata """
        metadata={}
        metadata['comment']=""
        metadata['start_dt']=start_dt.strftime(format=self.time_format)
        metadata['end_dt']=end_dt.strftime(format=self.time_format)
        metadata['granularity']=granularity
        metadata['asset_id']=asset_id
        candle_url=self.build_candle_url(start_dt,end_dt,granularity,asset_id)
        metadata['candle_url']=candle_url
        request=self.send_request(candle_url) # would be cool to write to metadata initially failed requests
        metadata['request_status_code']=request.status_code
        raw_data=request.text # getting raw data 
        try:
            if metadata['request_status_code']!=200:
                print(f"request status code {metadata['request_status_code']}")
                parsed_data={}
            else:
                parsed_data=self.parse_raw_data(raw_data)
            metadata['no_of_candles']=len(parsed_data['epoch'])
        except Exception as err:
            print(err)
            print(candle_url)
            print(raw_data)

        return {'request_metadata':metadata,'raw_data':raw_data, 'parsed_data':parsed_data}

    def fetch_last_candle(self,granularity=60,asset_id='BTC-USD'):
        """ 
        returns last candle based on granularity and asset_id
        """
        # get timestamps 
        server_time,server_dt=self.get_server_time()
        # truncating start time to start of a timebucket
        start_dt=server_dt-datetime.timedelta(seconds=granularity) # start time in past according to granularity 
        end_dt=server_dt # the end is now 
        # build candle url 
        candle_url=self.build_candle_url(start_dt,end_dt,granularity=granularity,asset_id=asset_id)
        # get data from api 
        request_data=self.fetch_candles(start_dt,end_dt,granularity,asset_id)
        #coinbase api sometimes returns more than one candle if you're unlucky with time of your request
        #this if handles that with single_candle flag
        if request_data['request_metadata']['no_of_candles']!=1:
            request_data['parsed_data']=self.parse_raw_data(request_data['raw_data'],single_candle=True)
            request_data['request_metadata']['comment']=f"request returned {request_data['request_metadata']['no_of_candles']} candles instead of expected 1, truncating parsed values and ,no_of_candles to 1 candle"
            request_data['request_metadata']['no_of_candles']=len(request_data['parsed_data']['epoch'])
        return request_data


    def fetch_historical_candles(self,start_dt,end_dt,granularity=60,asset_id='BTC-USD'):
        """returns generator of historical candles of specific granularity
        granularity= {60, 300, 900, 3600, 21600, 86400} 1m 5m 15m 1h
        note that coinbase api max no of candles is 300 but sometimes it does not return all the data
        """
        gen=self.clock_gen(start_dt,end_dt,granularity=granularity) # get datetimes generator 
        previous_left_dt,previous_right_dt=None,None
        while True:
            try:
                left_dt,right_dt=gen.__next__() # getting left and right datetimes 
            except StopIteration:
                print( f"clock generator finished \n start_dt: {start_dt} \n end_dt: {end_dt} \n left_dt: {previous_left_dt} \n right_dt={previous_right_dt}")
                return

            candle_url=self.build_candle_url(left_dt,right_dt) # building candle url 
            request_data=self.fetch_candles(left_dt,right_dt,granularity=granularity,asset_id=asset_id)
            yield request_data
            previous_left_dt,previous_right_dt=left_dt,right_dt

    def write_dictionary_to_file(self,filename,dic,path="", mode='w',ext='csv',write_header=True,eol=';',truncate=True):
        """ writes dic to a flatfile"""
        #write as csv 
        if truncate:
            with open(path+filename,'w') as f:
                print(f"truncating {filename}")
                f.truncate()
        if ext=='csv':
            print("writing")
            with open (path+filename,mode) as f:
                keys_list=list(dic.keys())
                if write_header: # writes keys as header
                    print("writing header")
                    f.write(','.join(keys_list))
                    f.write(eol)
                for no,val in enumerate(dic[keys_list[0]]):
                    line=[str(dic[key][no]) for key in keys_list]
                    f.write('\n')
                    f.write(','.join(line)+eol)
                    
        if ext=='json':
            raise "dupa, not implemented"
        #      with open(path+filename+'.json','w') as f:
#            json.dump(request_data,f,indent=4)

    def bulk_download_data(self,start_dt,end_dt,path,mode,ext,write_header,truncate,granularity,filename):
        """downloads data from start_dt to end_dt into a csv"""
        gen=self.fetch_historical_candles(
            start_dt=start_dt,
            end_dt=end_dt,
            granularity=granularity)
        while True:
            try:
                request_data=gen.__next__()
            except StopIteration as err:
                print("end of iteration ")
                return 
            self.write_dictionary_to_file(
                filename=filename,
                dic=request_data['parsed_data'],
                path=path,
                mode=mode,
                ext=ext,
                write_header=write_header,
                truncate=truncate)
            write_header=False
            truncate=False
            time.sleep(0.1)


def init(relpath=''):
    # setup instance
    api_config=json.load(open('./configs/api_config.json'))
    auth=CoinbaseExchangeAuth(
        api_config['api_key'],
        api_config['secret_key'],
        api_config['passphrase'])
    api=coinbase_api(auth)
    return api

def fetch_all_data(api,
        start_dt,
        end_dt,
        path):
    """fetches all the data and puts it into a csv """
    api.bulk_download_data(
        start_dt=start_dt,
        end_dt=end_dt,
        path=path,#r"C:\\Users\\pawel.zdunek\\Documents\\vscode\\buy_rsi\\historical_data3\\",
        mode='a',
        ext='csv',
        write_header=True,
        truncate=True,
        granularity=60,
        filename='all_data.csv')
        

# check if this old shit works 
if __name__=="__main__x":
    api=init()
    r=api.fetch_last_candle(granularity=60*60, asset_id='BTC-USD') #1h 
    print(r['parsed_data'])
    r=api.fetch_last_candle(granularity=60*60*24, asset_id='BTC-USD') # 1d
    print(r['parsed_data'])



if __name__=="__main__":

    api=init()
    _,server_dt=api.get_server_time()
    start_dt=server_dt-datetime.timedelta(days=1)


    api.bulk_download_data(
        start_dt=start_dt,
        end_dt=server_dt,
        path=os.path.abspath(os.getcwd())+"\\ETL\\rawdata\\",
        mode='a',
        ext='csv',
        write_header=True,
        truncate=True,
        granularity=60,
        filename=f"BTC{start_dt.isoformat()[:10]}_{server_dt.isoformat()[:10]}"+'.csv' )