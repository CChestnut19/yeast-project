import random
import numpy as np
from matplotlib import pyplot as plt
import math
# from scipy import integrate
from sympy import *
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.

class SA:
    def __init__(self,func,iter=100,T0 = 100, Tf = 0.01, alpha = 0.99):
        self.func = func
        self.iter = iter
        self.alpha = alpha
        self.T0 = T0
        self.Tf = Tf
        self.T = T0
        self.ymax = [random() ]

def picture(ymax,ymin,K,n,index):
    NorGateFunction = "ymin+(((ymax-ymin)*(K**n))/((x**n)+(K**n)))"
    fig = plt.figure(figsize=(5,5))
    # plt.title("Output Cruve")
    x = np.arange(0,10,0.001)
    y = eval(NorGateFunction)
    ax1 = plt.subplot()
    labelText = "ymin = "+str(ymin)+",ymax = "+str(ymax)+",K="+str(K)+",n="+str(n)
    plt.xscale('log')
    ax1.plot(x,y,color = 'r',label = labelText)
    ymin = 0.2
    ymax = 3.8
    K = 0.09    #K和RBS有关
    n = 1.4   #n和CDS有关
    x = np.arange(0,10,0.001)
    y = eval(NorGateFunction)
    ax1.plot(x,y,color='b',label="Demo")
    fig.show()
    plt.legend(loc = "best")
    fileName = './functionPlot'+str(index)+'.jpg'
    fig.savefig(fileName)


#如果只计算ymax，ymin，K，foldchange的相似度?
#CaculateDistance 计算整个曲线的相似度
def CaculateDistance(ymax,ymin,k,n,ObjectFunction):
    xList = np.arange(0.001,10,0.1)
    NorGateFunction = "ymin+((ymax-ymin)/(1+(x/K)**n))"
    DistanceFunction = ObjectFunction + "- ("+NorGateFunction+")"
    distance = 0
    for i in range(0,len(xList)):
        DemoY = np.sqrt((eval(DistanceFunction)) ** 2)
        distance += DemoY
    return distance


def StandFunction(ymin,ymax,K,n,x):
    Stand = ymin+(((ymax-ymin)*(K**n))/((x**n)+(K**n)))


def sigmoid(x):
    return 1/(1+np.exp(-x))

def sigmoidPrime(x):
    return x * (1-x)


def temp():
    k1 = 0.0000727
    k2 = 4.627521
    k3 = 0.693479
    kx1 = 0.65925
    kx2 = 3.65837
    L = 100
    Imax = 0.85546578
    #假设为连续的
    kd = 6.216347694
    I0 = 0.01
    I = np.logspace(-3,3,N)
    x1 = np.sqrt((k2*I+kx1+kx2*k2*I+1)*(k2*I+kx1+kx2*k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1+k1*kx1*kx1+k3*k2*k2*kx2*kx2*I*I))
    P1 = (Imax * ((L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) * kd / (1 + (L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) *kd)) + I0)
    return P1

def CaculateFunction(value,Function,x):
    # k1 = 0.0000727
    # k2 = 4.627521
    # k3 = 0.693479
    # kx1 = 0.65925
    # kx2 = 3.65837
    # L = 5
    # Imax = 0.85546578
    # #假设为连续的
    # kd = 6.216347694
    # I0 = 0.01
    # # I = np.logspace(-3,3,100)
    # # I = Symbol('I')
    # P2 = value - (Imax / (1 + exp((log(L / 2) + log(((sqrt((k2*I+1)*(k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1))) - (k2*I+1)) / ((sqrt((k2*I+1)*(k2*I+1)+ 8 * 5 * (k2*k2*k3*I*I + k1))) + (k2*I+1))) + log(kd))))) +I0
    # return P2
    result = str(value) +"-(" +Function +")"
    result = eval(result)
    return abs(result)


def CalculateDiff(value,Function,Point):
    x = Symbol('x')
    result = str(value) +"-(" +Function +")"
    ResultDiff = diff(result,x)
    df = str(ResultDiff)
    x = Point
    return eval(result)


def Calculate(value,Function,point):
    alpha = 0.01
    f_x0 = CaculateFunction(value,Function,point)
    f_x0d = CalculateDiff(value,Function,point)
    xn1 = point - alpha*(f_x0/f_x0d)
    f_x1 = CaculateFunction(value,Function,xn1)
    f_x1d = CalculateDiff(value,Function,xn1)
    x0 = xn1
    while(abs(f_x1) < abs(f_x0)):
        f_x0 = f_x1
        f_x0d = f_x1d
        xn1 = x0 - alpha*(f_x1/f_x1d)
        f_x1 = CaculateFunction(value,Function,xn1)
        f_x1d = CalculateDiff(value,Function,xn1)
        x0 = xn1
        # print(f_x0)
        print(xn1)
    print("===================result==============================")
    print(CaculateFunction(value,Function,x0))
    print(x0)
    return x0


def CaculateYminYmax(LBD,DBD,L):
    Imax = 35.84932
    k1 = LBD[0]
    k2 = LBD[1]
    k3 = LBD[2]
    kx1 = LBD[3]
    kx2 = LBD[4]
    I0 = DBD[0]
    kd = 0.7
    I = np.logspace(-3,3,100)
    x1 = np.sqrt((k2*I+kx1+kx2*k2*I+1)*(k2*I+kx1+kx2*k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1+k1*kx1*kx1+k3*k2*k2*kx2*kx2*I*I))
    P2 = (Imax * ((L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) * kd / (1 + (L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) *kd)) + I0)
    Pmax = np.max(P2)
    Pmin = np.min(P2)
    return [Pmax,Pmin]

    
if __name__ == '__main__':



    ObjectFunction = "0.4+((3.9-0.4)/(1+(x/0.11)**1.4))"


  

    NorGateFunction = "ymin+(((ymax-ymin)*(K**n))/((x**n)+(K**n)))"
    x = np.logspace(3,-3,100)
    result = eval(ObjectFunction)

    Objectymax = np.max(result)
    Objectymin = np.min(result)
    Objecthalf = (Objectymax+Objectymin) / 2

    # x = np.arange(0,10,0.1)
    ymax = np.arange(0.1,0.6,0.001)
    ymin = np.arange(0.001,0.1,0.0001)
    K = np.arange(0.05,0.1,0.001)
    ############
    #定积分为损失函数(失败，没办法计算积分)
    # LossFunctionStr = StandFunction + '- ('+ObjectFunction +')' 
    # x = np.logspace(-3,3,100)
    # distance = CaculateDistance(ObjectFunction=ObjectFunction)
    # ymin = symbols("ymin")
    # ymax = symbols("ymax")
    # K = symbols("K")
    # lossFunction = Integral(eval(LossFunctionStr),x)
    # lossFunction = integrate(eval(LossFunctionStr),x)
    # lossFunction = (0.04+((0.5-0.04)/(1+(x/5) ** 3))) - (0.01+((0.4-0.01)/(1+(x/4) ** 3)))
    # print(Eq(lossFunction,lossFunction.doit()))
    # print(lossFunction)
    
    

    LBDNRMenu =  {"ER":[0.0000727,4.627521,0.693479,0.65925,3.65837],
              "DHBR":[0.0000344,0.074576,2.119521,0.029883,0.000303],
              "PR":[0.0000169,0.527704,0.074942,0.199491,1.014695],
              "GR":[0.0000053,0.172413,0.0000334,4.959807,1.005826],
              "MR":[0.00000549,2.00561142,0.001243206,1.937182665,1.619613647]}

    DBDMenu =  {"CI434":[0.01,6.216347694],"LexAs5":[0.035486,40.97705],
            "LexA87":[0.0159301,0.7455533],
            "LexAs23":[0.011798,1.445353],
            "HKCI":[0.008956896,5.066512585],
            "RecApact":[0.016946,2.956591],
            "DeoR":[0.024572,0.607056],
            "PurR":[0.006969,1.130833],
            "LexAs15":[0.045317,0.607056],
            "LexAs14":[0.111188,0.102414],
            "CI OL1":[0.135762,30.08698],
            "CI OR1":[0.135906,10.36936],
            "CI Osym":[0.272292,10.53283]}


    L = 0.01
    MaxMinlistL1 = []
    for i in LBDNRMenu.keys():
        for j in DBDMenu.keys():
            result = CaculateYminYmax(LBDNRMenu[i],DBDMenu[j],L)
            MaxMinlistL1.append(result)
    
    L = 0.6
    MaxMinlistL2 = []
    for i in LBDNRMenu.keys():
        for j in DBDMenu.keys():
            result = CaculateYminYmax(LBDNRMenu[i],DBDMenu[j],L)
            MaxMinlistL2.append(result)
    L = 1
    MaxMinlistL3 = []
    for i in LBDNRMenu.keys():
        for j in DBDMenu.keys():
            result = CaculateYminYmax(LBDNRMenu[i],DBDMenu[j],L)
            MaxMinlistL3.append(result)
    
    L = 10
    MaxMinlistL4 = []
    for i in LBDNRMenu.keys():
        for j in DBDMenu.keys():
            result = CaculateYminYmax(LBDNRMenu[i],DBDMenu[j],L)
            MaxMinlistL4.append(result)

    
    ############
    #在n个点上的差值的平方的和
    # for i in range(0,len(x)):
    #     difference = (eval(StandFunction) - eval(ObjectFunction)) ** 2
    #     loss += difference
    # #Cello 数据
    # # A1_AmtRymax = 3.8, ymin = 0.06, K = 0.07, n = 1.6 promoter = pAmtR，RBS = A1, CDS = AmtR, Terminator = L3S2P55
    # # B1_BM3R1   ymax = 0.5, ymin = 0.004,K = 0.04,n = 3.4  promtoer = pBM3R1,RBS = B1, CDS = BM3R1,Terminator = L3S2P11
    # # B2_BM3R1   ymax = 0.5, ymin = 0.005,K = 0.15,n = 2.9  promoter = pBM3R1,RBS = B2, CDS = BM3R1,Terminator = L3S2P11
    # # B3_BM3R1   ymax = 0.8, ymin = 0.01, K = 0.26,n = 3.4  promoter = pBM3R1,RBS = B3, CDS = BM3R1,Terminator = L3S2P11
    
    k1 = 0.0000727
    k2 = 4.627521
    k3 = 0.693479
    kx1 = 0.65925
    kx2 = 3.65837
    L = 100
    Imax = 35.84932
    #假设为连续的
    kd = 6.216347694
    I0 = 0.01
    I = np.logspace(-3,3,100)
    x1 = np.sqrt((k2*I+kx1+kx2*k2*I+1)*(k2*I+kx1+kx2*k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1+k1*kx1*kx1+k3*k2*k2*kx2*kx2*I*I))
    P2 = (Imax * ((L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) * kd / (1 + (L / 2) * ((x1 - (k2*I+kx1+kx2*k2*I+1)) / (x1 + (k2*I+kx1+kx2*k2*I+1))) *kd)) + I0)
    #以p2为输入
    fig = plt.figure(figsize=(10,10))
    # plt.tick_params(axis='both',which='major',labelsize=14)
    plt.xscale('log')
    plt.yscale('log')
    # plt.ylim(0.05,1)
    plt.xlabel("input",fontsize=20)
    plt.ylabel("output",fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    ax1 = plt.subplot(1,1,1)
    # y = 0.205-(0.01+((0.4-0.01)/(1+(x/4)**1.6)))
    y = eval(ObjectFunction)
    plt.plot(x,y,color='r')
    # plt.plot(x,result,color = "b")
    # ax1 = plt.subplot(1,1,1)
    # plt.plot(I,P2,color='y')
    
    Kstd = Calculate(Objecthalf,ObjectFunction,0.1)
    
    # fig = plt.figure(figsize=(5,5))
    # ax1 = plt.subplot(2,2,1)

    # ymin = Objectymin
    # ymax = Objectymax
    # x = P2
    # n = 1.4
    # K = Kstd
    # ax1 = plt.subplot(111)
    # y = eval(NorGateFunction)
    # plt.plot(x,y,color = 'b')
    
    
    # ymin = Objectymin
    # ymax = Objectymax
    # x = P2
    # n = 1.4
    # K = Kstd*2
    # ax1 = plt.subplot(111)
    # y = eval(NorGateFunction)
    # plt.plot(x,y,color = 'b')


    ymin = 0.3725852919425381
    ymax = 3.8927013401763233
    x = np.logspace(-3,3,100)
    n = 1.4
    K = Kstd
    ax1 = plt.subplot(111)
    y = eval(NorGateFunction)
    plt.plot(x,y,color = 'b')



    # ymin = 0.06
    # ymax = 3.8
    # K = 0.08
    # n = 1.6
    # y = eval(NorGateFunction)
    # plt.plot(x,y,color = 'b')
    # ymin = 0.06
    # ymax = 3.8
    # K = 0.06
    # n = 1.6
    # y = eval(NorGateFunction)
    # plt.plot(x,y,color = 'r')
    # ymin = 0.06
    # ymax = 3.8
    # K=0.04
    # n = 1.6
    # y = eval(NorGateFunction)
    # plt.plot(x,y,color = 'g')
    # fig.show()
    # ymin = 0.004
    # ymax = 0.5
    # K = 0.04
    # n = 3.4
    # # y = eval(NorGateFunction)
    # # plt.plot(x,y,color = 'y')
    # ymin = 0.005
    # ymax = 0.5
    # K = 0.15
    # n = 2.9
    # # y = eval(NorGateFunction)
    # # plt.plot(x,y,color = 'b')
    # ymin = 0.01
    # ymax = 0.8
    # K = 0.26
    # n = 3.4
    # # y = eval(NorGateFunction)
    # # plt.plot(x,y,color = 'g')
    # # plt.legend(["A1_AmtR","B1_BM3R1","B2_BM3R1","B3_BM3R1"])
    # # plt.show()
    # #模拟
    # PromoterList = []
    # RBSList = []
    # CDSList = []
    # for i in range(0,10):
    #     RBS_Data = round(random.uniform(0,1),1)
    #     if(RBS_Data == 0):
    #         RBS_Data = 0.01
    #     RBSList.append(RBS_Data)
    #     FakePromoterYminData = round(random.uniform(0,1),1)
    #     if(FakePromoterYminData == 0):
    #         FakePromoterYminData = 0.01
    #     FakePromoterYmaxData = round(random.uniform(1,6),1)
    #     PromoterList.append([FakePromoterYmaxData,FakePromoterYminData])
    #     n_Data = round(random.uniform(2,4),1)
    #     CDSList.append(n_Data)
    # # print(RBS_Data)
    # # print(FakePromoterYminData)
    # # print(FakePromoterYmaxData)
    # # print(n_Data)
    # Demo = [3.8,0.2,0.09,1.4]
    # SampleList = []
    # maxDistance = 1000000000
    # maxDistanceIndex = 0
    # for i in range(0,10):
    #     SampleList.append([PromoterList[i][0],PromoterList[i][1],RBSList[i],CDSList[i]])
    # for i in range(0,10):
    #     # ymax,ymin,K,n,index
    #     picture(PromoterList[i][0],PromoterList[i][1],RBSList[i],CDSList[i],i)
    #     dis = CaculateDistance(Demo,SampleList[i])
    #     if(dis < maxDistance):
    #         maxDistance = dis
    #         maxDistanceIndex = i
    # print(SampleList)
    # print(SampleList[maxDistanceIndex])
    # print(maxDistance)
    fig.savefig('temp.jpg')