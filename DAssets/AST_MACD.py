import numpy as np
import pandas as pd
from .AST_CORE import *


class AST_MACD(AST_CORE):
    def __init__(
        self,
        sub_assets,
        name = None,
        no_short = True,
        period_Fast = 12,
        period_Slow = 26,
        period_Sig = 9,
        mode = 'close',
        extent = False
    ):
        AST_CORE.__init__(self,name)
        self.assets = sub_assets
        self.period = period_Fast + period_Slow + period_Sig
        self.periods = [period_Fast,period_Slow,period_Sig]
        self.trade_on = mode
        self.extent = extent
        self.no_short = no_short
        
        for asset in self.assets:
            assert type(asset) is str
        self.simple_assets = self.assets
    def feed(self):
        self.data = pd.DataFrame()
        self.weights = {}
        self.weight = pd.DataFrame(columns=self.assets)
        self.ind = pd.DataFrame()
        for asset in self.assets:
            a,i = stro(asset,mode = self.trade_on,indicator = 'MACD{},{},{}'.format(*self.periods))
            if len(a)>len(self.data):
                self.data = self.data.reindex(a.index,fill_value = np.nan)
            self.data[asset],self.ind[asset] = a,i
        if self.extent:
            self.ind = self.ind.fillna(0)
        else:
            self.ind = self.ind.dropna()
        self.ind = np.exp(-self.ind)
        self.data = self.data.loc[self.ind.index]
    def __call__(self):
        res,sass,cass,rw = self.pre_call()
        for i in range(1,len(self.data)):
            rw.iloc[i] = self.ind.iloc[i]/self.ind.iloc[i].sum()
            res.iloc[i] = np.dot(rw.iloc[i-1],self.data.iloc[i])
        return self.post_call(res,sass,cass,rw)