#GMV MVE


from scipy.optimize import minimize
import numpy as np
import pandas as pd
from .AST_CORE import *


class AST_GM(AST_CORE):
    def __init__(
        self,
        sub_assets,
        name = None,
        period = 30,
        no_short = True,
        optimizer_tol = 1e-15,
        optimizer_maxiter = 600,
        extent = False,
        trade_on = 'close',
        p = 0.2,
        decay = 0,
        decay_dir = 'pos'
    ):
        AST_CORE.__init__(self,name)
        self.no_short = no_short
        self.tol = optimizer_tol
        self.maxiter = optimizer_maxiter
        self.period = period
        
        self.assets = sub_assets
        self.trade_on = trade_on
        self.extent = extent
        self.p = p
        self.decay = decay
        self.decay_dir = decay_dir

        self.simple_assets = set()
        assert self.decay_dir in ['pos','neg']
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
                
    def g_var(self,w,i):
        ker = self.data.iloc[i:i+self.period]
        R = pd.DataFrame(
            [[(1+self.decay)**k for j in range(len(ker.columns))] for k in range(len(ker.index))],
            columns = ker.columns
        )
        if self.decay_dir == 'pos':
            R = R.iloc[::-1]
        R.index = ker.index
        cov = (ker*R).cov()
        return np.sqrt(np.dot(np.matmul(w,cov.values),w))
    def s_rat(self,w,i):
        ker = self.data.iloc[i:i+self.period]
        R = pd.DataFrame(
            [[(1+self.decay)**k for j in range(len(ker.columns))] for k in range(len(ker.index))],
            columns = ker.columns
        )
        if self.decay_dir == 'pos':
            R = R.iloc[::-1]
        R.index = ker.index
        mean = (ker*R).mean()
        return (np.dot(w,mean.values))/self.g_var(w,i)
    
    def GMV(self,i):
        w0 = np.array([1.0/len(self.assets)]*len(self.assets))
        params = {
            'fun':lambda x:self.g_var(x,i),
            'x0':w0,
            'method':'SLSQP',
            'constraints':{
                'type':'eq',
                'fun':(lambda x:sum(x)-1)
            },
            'tol':self.tol,
            'options':{
                'maxiter':self.maxiter
            }
        }
        if self.no_short:
            params['bounds'] = [(0,1) for i in range(len(self.assets))]
        gmv = minimize(**params)
        return gmv.x
    
    def MVE(self,i):
        w0 = np.array([1.0/len(self.assets)]*len(self.assets))
        params = {
            'fun':lambda x:-self.s_rat(x,i),
            'x0':w0,
            'method':'SLSQP',
            'constraints':{
                'type':'eq',
                'fun':(lambda x:sum(x)-1)
            },
            'tol':self.tol,
            'options':{
                'maxiter':self.maxiter
            }
        }
        if self.no_short:
            params['bounds'] = [(0,1) for i in range(len(self.assets))]
        mve = minimize(**params)
        return mve.x
        
    def __call__(self):
        res,sass,cass,rw = self.pre_call()
        for i in range(self.period,len(self.data)):
            gmv = self.GMV(i-self.period)
            mve = self.MVE(i-self.period)
            rw.iloc[i] = self.p*gmv + (1-self.p)*mve
            res.iloc[i] = np.dot(rw.iloc[i-1],self.data.iloc[i])
        return self.post_call(res,sass,cass,rw)






