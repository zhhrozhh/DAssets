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
        extent = False
    ):
        AST_CORE.__init__(self,name)
        self.assets = sub_assets
        self.period = period
        self.trade_on = mode
        self.extent = extent
        self.no_short = no_short

        for asset in self.assets:
            assert type(asset) is str
    def feed(self):
        self.data = pd.DataFrame()
        self.weights = {}
        self.weight = pd.DataFrame(columns = self.assets)
        self.ind = pd.DataFrame()
        for asset in self.assets:
            self.data[asset],self.ind[asset] = stro(asset,mode=self.trade_on,indicator = 'WR'+str(int(period)))
        if self.extent:
            self.ind = self.ind.fillna(0)
        else:
            self.ind = self.ind.dropna()
        self.data = self.data.loc[self.ind.index]

    def __call__(self):
        res,sass,cass,rw = self.pre_call()
        for i in range(self.period,len(self.data)):

            rw.iloc[i] = self.p*gmv + (1-self.p)*mve
            res.iloc[i] = np.dot(rw.iloc[i-1],self.data.iloc[i])
        return self.post_call(res,sass,cass,rw)




