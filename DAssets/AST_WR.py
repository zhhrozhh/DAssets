import numpy as np
import pandas as pd
from .AST_CORE import *

class AST_WR(AST_CORE):
    def __init__(
        self,
        sub_assets,
        name = None,
        no_short = True,
        period = 7,
        mode = 'close',
        extend = False
    ):
        AST_CORE.__init__(self,name)
        self.assets = sub_assets
        self.period = period
        self.trade_on = mode
        self.extend = extend
        self.no_short = no_short

        for asset in self.assets:
            assert type(asset) is str
        self.simple_assets = self.assets
    def feed(self):
        self.data = pd.DataFrame()
        self.weights = {}
        self.weight = pd.DataFrame(columns = self.assets)
        self.ind = pd.DataFrame()
        for asset in self.assets:
            a,i = stro(asset,mode=self.trade_on,indicator = 'WR'+str(int(self.period)))
            if len(a) > len(self.data):
                self.data = self.data.reindex(a.index,fill_value = np.nan)
                self.ind = self.ind.reindex(i.index,fill_value = np.nan)
            self.data[asset],self.ind[asset] = a,i
        if self.extend:
            self.ind = self.ind.fillna(0)
        else:
            self.ind = self.ind.dropna()
        self.data = self.data.loc[self.ind.index]

    def __call__(self):
        res,sass,cass,rw = self.pre_call()
        q = 1-self.ind
        for i in range(self.period,len(self.data)):
            rw.iloc[i] = q.iloc[i]/q.iloc[i].sum()
            res.iloc[i] = np.dot(rw.iloc[i-1],self.data.iloc[i])
        return self.post_call(res,sass,cass,rw)




