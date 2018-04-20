#storage for simple assets
import quandl
import pandas as pd
try:
    from quandl_set import *
except:
    pass

class SAST_STRO:
    def __init__(self):
        self.stro = pd.DataFrame()
    def __call__(self,scode,mode = 'close',indicator = None):
        assert mode in ['close','open']
        scode = scode.upper()
        sp = scode+'_'+mode
        if not sp in self.stro.columns:
            d = quandl.get('EOD/'+scode)
            if mode == 'close':
                self.stro[sp] = d['Adj_Close']
            elif mode == 'open':
                self.stro[sp] = d['Adj_Open']
        return ((self.stro[sp]-self.stro[sp].shift(1))/self.stro[sp].shift(1)).dropna()
