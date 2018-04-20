import numpy as np
import pandas as pd
from .AST_CORE import *

class AST_CC(AST_CORE):
    def __init__(
        self,
        sub_assets,
        name = None,
        method = 'max',
        no_short = True,
        period = 40,
        decay = 0,
        decay_dir = 'pos',
        p = 0.2,
        mode = 'close',
        extent = False
    ):
        AST_CORE.__init__(self,name)
        self.assets = sub_assets
        self.method = method
        assert method in ['max','min']
        self.period = period
        self.decay = decay
        self.decay_dir = decay_dir
        assert decay_dir in ['pos','neg']
        self.trade_on = mode
        self.extent = extent
        self.no_short = no_short
        self.p = p

        self.simple_assets = set()
        for asset in sub_assets:
            if type(asset) is str:
                self.simple_assets.add(asset.upper())
            else:
                self.simple_assets = self.simple_assets.union(asset.simple_assets)
    def feed(self):
        self.data = pd.DataFrame()
        self.weights = {}
        self.weight = pd.DataFrame(columns = self.simple_assets)
        for asset in self.assets:
            if type(asset) is str:
                self.data[asset] = stro(asset,mode=self.trade_on)
            else:
                asset.feed()
                self.data[asset.name],self.weights[asset.name] = asset()
        if self.extent:
            self.data = self.data.fillna(0)
        else:
            self.data = self.data.dropna()
    def __call__(self):
        res,sass,cass,rw = self.pre_call()

        for i in range(self.period,len(self.data)):
            ker = self.data.iloc[i-self.period:i]
            R = pd.DataFrame(
                [[(1+self.decay)**k for j in range(len(ker.columns))] for k in range(len(ker.index))],
                columns = ker.columns
            )
            if self.decay_dir == 'pos':
                R = R.iloc[::-1]
            R.index = ker.index

            d = ker.copy()*R

            mmap = {}
            mx = 0
            for asset in sass+cass:
                x = pd.Series(np.zeros(len(self.assets)),index = sass+cass)
                x[asset] = 1
                mmap[asset] = x
            while len(d.columns) > 1:
                corr = None
                if self.method == 'max':
                    corr = -d.corr()+2*np.identity(len(d.columns))
                else:
                    corr = d.corr()

                ass1 = corr.min().idxmin()
                ass2 = corr[ass1].idxmin()

                rho = d.corr()[ass1][ass2]

                d1 = d.pop(ass1)
                d2 = d.pop(ass2)

                s1 = d1.std(ddof = 0)
                s2 = d2.std(ddof = 0)

                r1 = d1.mean()
                r2 = d2.mean()

                a = s1**2 + s2**2 - 2*rho*s1*s2
                b = 2*rho*s1*s2 - 2*s2**2
                c = s2**2

                e = r1 - r2
                f = r2

                wgmv = -b/(2*a)
                wmve = (b*f-2*e*c)/(b*e-2*a*f)
                if self.no_short:
                    wgmv = min(max(wgmv,0),1)
                    wmve = min(max(wmve,0),1)
                w = self.p*wgmv + (1-self.p)*wmve
                mmap[mx] = mmap[ass1]*w + mmap[ass2]*(1-w)
                d[mx] = d1*w + d2*(1-w)
                mx += 1

            # gmv = self.GMV(i-self.period)
            # mve = self.MVE(i-self.period)
            rw.iloc[i] = mmap[mx-1]
            res.iloc[i] = np.dot(rw.iloc[i-1],self.data.iloc[i])
        return self.post_call(res,sass,cass,rw)
