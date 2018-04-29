
from .SAST_STRO import SAST_STRO
import pandas as pd
n_count = 0
stro = SAST_STRO()
reg_table = {}


class AST_CORE:
    def __init__(self,name):
        global n_count
        self.name = name
        if name is None:
            self.name = '!DEF'+str(n_count)
            n_count += 1
        reg_table[self.name] = self

    def __call__(self,**args):
        #simulate return (return,weights)
        return None,None
    def otd(self,**args):
        #one decision return weights
        return None
    def feed(self):
        return None
    def pre_call(self):
        res = pd.Series(index=self.data.index)
        cols = []
        sass = []
        cass = []
        for x in self.assets:
            if type(x) is str:
                cols.append(x)
                sass.append(x)
            else:
                cols.append(x.name)
                cass.append(x.name)
        rw = pd.DataFrame(index = self.data.index,columns = cols)
        return res,sass,cass,rw
    def post_call(self,res,sass,cass,rw):
        W = pd.DataFrame(columns = self.simple_assets)
        W[sass] = rw[sass]
        W = W.fillna(0)
        for asset in cass:
            w = pd.DataFrame(columns = self.simple_assets)
            v = self.weights[asset]
            w[v.columns] = v[v.columns]
            w = w.loc[W.index]
            w = w.fillna(0)
            z = pd.DataFrame({col:rw[asset] for col in self.simple_assets})
            W = W + w*z

        return res,W


