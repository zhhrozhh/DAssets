#storage for simple assets
import quandl
import pandas as pd
try:
    from quandl_set import *
except:
    pass


def WR(data,period):
    rhmax = data.Adj_High.rolling(window = period,center = False).max()
    rmmin = data.Adj_Low.rolling(window = period,center = False).max()
    return (rhmax-data.Adj_Close)/(rhmax-rmmin)
def pitcher(ind,data):
    if ind[:2] == 'WR':
        period = int(ind[2:])
        return WR(data,period)
class SAST_STRO:
    def __init__(self):
        self.stro = pd.DataFrame()
    def __call__(self,scode,mode = 'close',indicator = None):
        assert mode in ['close','open']
        scode = scode.upper()
        if scode == '0RSK':
            return self.stro[self.stro.columns[0]]*0
        sp = scode+'_'+mode
        if not sp in self.stro.columns:
            d = quandl.get('EOD/'+scode)

            if mode == 'close':
                self.stro[sp] = d['Adj_Close']
            elif mode == 'open':
                self.stro[sp] = d['Adj_Open']
            if indicator is not None:
                self.stro[scode+'_'+indicator] = pitcher(indicator,d)

        res = ((self.stro[sp]-self.stro[sp].shift(1))/self.stro[sp].shift(1)).dropna()
        if indicator is None:
            return res
        else:
            return res,self.stro[scode+'_'+indicator]
