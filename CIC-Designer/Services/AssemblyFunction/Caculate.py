import sys
sys.path.append('/T18/weiboyan/WebPlot')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import spatial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import log
# from Entity.Part import GetPromoterList,GetTerminatorList
from Entity.Promoter import GetPromoterList
from Entity.Terminator import GetTerminatorList



class Caculate:
    def __init__(self,api_url,session,result):
        self.api_url = api_url
        self.promoter = GetPromoterList(self.api_url,session)
        self.terminator = GetTerminatorList(self.api_url,session)
        self.result = result

    # def GetPromoter(self):
    #     sql = "select Name, RPU from PartTable where RPU != 0.0 and isPromoter = 1 and isCDS = 0 and isTerminator = 0;"
    #     self.c.execute(sql)
    #     result = self.c.fetchall()
    #     return result

    # def GetTerminator(self):
    #     sql = "select Name, RPU from PartTable where RPU != 0.0 and isPromoter = 0 and isCDS = 0 and isTerminator = 1;"
    #     self.c.execute(sql)
    #     result = self.c.fetchall()
    #     return result

    def fun(self, x, result):
        x1,x2=x
        x1 = log(x1,10)
        x2 = log(x2,10)
        return log(float(result),10) - x1 - x2
    

    def CaculateFunction(self):
    # WriteString = ""
        MIN = 2222222222
        for i in range(0,len(self.promoter)):
            for j in range(0,len(self.terminator)):
                x = np.array([self.promoter[i].Strength,self.terminator[j].Strength])
                ToReturn = self.fun(x,self.result)
                if(abs(ToReturn)<MIN):
                    MIN = abs(ToReturn)
                    resultPromoter = self.promoter[i]
                    resultTerminator = self.terminator[j]
        return [resultPromoter,resultTerminator]
    





    
