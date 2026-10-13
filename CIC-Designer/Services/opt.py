import numpy as np
import csv
import pandas as pd
from Entity import DBD,LBD
import requests

def foldchange1(L, kd,k1,k2,k3, Imax, I0, I,alpha,beta):
    x1 = np.sqrt((k2*I+1)*(k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1))
    x2 = np.sqrt(1 + 8 * L * k1)
    F1 = np.log(L / 2) + np.log((x1 - (k2*I+1)) / (x1 + (k2*I+1))) + np.log(kd)
    F2 = np.log(L / 2) + np.log((x2 - 1) / (x2 + 1)) + np.log(kd)
    P1 = (Imax / (1 + np.exp(-F1))) + I0
    P2 = (Imax / (1 + np.exp(-F2))) + I0
    f1 = P1 / P2
    f2 = P1 - P2
    alpha = float(alpha)
    beta = float(beta)
    return alpha*np.log10(f1)+ beta*np.log10(f2)

def foldchange2(L, kd,k1,k2,k3, Imax, I0, I):

    x1 = np.sqrt((k2*I+1)*(k2*I+1)+ 8 * L * (k2*k2*k3*I*I + k1))
    x2 = np.sqrt(1 + 8 * L * k1)
    F1 = np.log(L / 2) + np.log((x1 - (k2*I+1)) / (x1 + (k2*I+1))) + np.log(kd)
    F2 = np.log(L / 2) + np.log((x2 - 1) / (x2 + 1)) + np.log(kd)
    P1 = (Imax / (1 + np.exp(-F1))) + I0
    P2 = (Imax / (1 + np.exp(-F2))) + I0
    f1 = P1 / P2
    f2 = P1 - P2
    
    return P1

def ReadExcelKdValue(api_url,session):
    Menu = DBD.GetDBDKdList(api_url,session)
    return Menu

def ReadExcelKdLabel(api_url,session):
    # file_path = r'WebPlot\TFDatabase.xlsx'
    # df = pd.read_excel(file_path,sheet_name="DBD")
    # Menu = []
    # length = len(df['name'])
    # for i in range(0,length):
    #     Menu.append(df.iloc[i,0])
    Menu = DBD.GetDBDNameList(api_url,session)
    return Menu

def ReadExcelLBDValue(api_url,session):
    # file_path = r'WebPlot\TFDatabase.xlsx'
    # df = pd.read_excel(file_path,sheet_name="LBDDimer")
    df = LBD.GetLBDDimerMenu(api_url,session)
    Menu = []
    NameList = list(df.keys())
    length = len(NameList)
    for i in range(0,length):
        # {'LBD_name': 'acVHH', 'k1':0.01047924, 'k2':58.86021805, 'k3': 0.746785045,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 1},
        temp = {}
        temp['LBD_name'] = NameList[i]
        temp['k1'] = df[NameList[i]][0]
        temp['k2'] = df[NameList[i]][1]
        temp['k3'] = df[NameList[i]][2]
        temp['Imax'] = 35.84931505
        temp['I0'] = 0.035485714
        temp['I'] = df[NameList[i]][3]
        Menu.append(temp)
    return Menu

def normalize_optional_name(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == '' or value.lower() in ('none', 'null', 'undefined'):
        return None
    return value

def same_name(left, right):
    return str(left).strip().lower() == str(right).strip().lower()

def HtmlReturn(alpha,beta,api_url,session,LBD=None,DBD=None):
    fixed_lbd = normalize_optional_name(LBD)
    fixed_dbd = normalize_optional_name(DBD)
    L = np.linspace(0.3, 10, 2000)
    kd_values = ReadExcelKdValue(api_url,session)
    kd_labels = ReadExcelKdLabel(api_url,session)
    LBD_parameters = ReadExcelLBDValue(api_url,session)
    if fixed_lbd:
        LBD_parameters = [params for params in LBD_parameters if same_name(params['LBD_name'], fixed_lbd)]
        if not LBD_parameters:
            raise ValueError(f'LBD not found: {fixed_lbd}')
    if fixed_dbd:
        kd_items = [(label, kd) for label, kd in zip(kd_labels, kd_values) if same_name(label, fixed_dbd)]
        if not kd_items:
            raise ValueError(f'DBD not found: {fixed_dbd}')
        kd_labels = [item[0] for item in kd_items]
        kd_values = [item[1] for item in kd_items]
    # kd_values = [6.216347694,	40.97704697,	5.374494076,	0.745553315,	1.445352554,	5.066512585	,2.956590891,	0.607055765,	1.13083303,30.08697891,0.343528478,	0.102414004]
    # kd_labels = ['CI434',         'LexAs5',       'LexAs17',      'LexA87',        'LexAs23',       'HKCI',     'RecApact', 'DeoR',           'PurR',   'CI',	   'LexAs15',       'LexAs14']


    # kd_values = [6.216347694,	40.97704697,	5.374494076,	0.745553315,	1.445352554,	5.066512585	,2.956590891,	0.607055765,	1.13083303,30.08697891,	10.36936283,	10.53282547,0.343528478,	0.102414004]
    # kd_labels = ['CI434', 'LexAs5', 'LexAs17', 'LexA87', 'LexAs23', 'HKCI', 'RecApact', 'DeoR', 'PurR', 'CI OL1',	'CI OR1',	 'CI Osym', 'LexAs15', 'LexAs14']

    # Define different LBD parameters and names
    # LBD_parameters = [
    #     {'LBD_name': 'acVHH', 'k1':0.01047924, 'k2':58.86021805, 'k3': 0.746785045,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 1},
    #     {'LBD_name': 'LasR', 'k1': 0.000170903, 'k2':0.145665169, 'k3':737.5150757,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 10},
    #     {'LBD_name': 'RpaR', 'k1': 0.000284363, 'k2':0.00611078, 'k3':0.899893641,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 1000},
    #     {'LBD_name': 'CinR', 'k1': 0.004921661, 'k2':71.69632721, 'k3':0.160939857,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 1},
    #     {'LBD_name': 'BjaR', 'k1': 0.000115959, 'k2':0.005969237, 'k3':0.015982453,'Imax': 35.84931505, 'I0': 0.035485714, 'I': 1000},
    # ]
    max_foldchange_values = np.zeros((len(LBD_parameters), len(kd_values)))
    max_L_values = np.zeros((len(LBD_parameters), len(kd_values)))
    max_RPU=np.zeros((len(LBD_parameters), len(kd_values)))

    MaxFoldChange = float('-inf')
    MaxIndex1 = -1
    MaxIndex2 = -1
    for i, params in enumerate(LBD_parameters):
        for j, kd in enumerate(kd_values):
            foldchange = (foldchange1(L, kd, params['k1'], params['k2'], params['k3'],params['Imax'], params['I0'], params['I'],alpha,beta))
            RPU=(foldchange2(L, kd, params['k1'], params['k2'], params['k3'],params['Imax'], params['I0'], params['I']))
            max_foldchange_index = np.argmax(foldchange)
            max_foldchange = foldchange[max_foldchange_index]
            max_L = L[max_foldchange_index]
            max_RPU_value = RPU[max_foldchange_index]
            if(max_foldchange > MaxFoldChange):
                MaxFoldChange = max_foldchange
                MaxIndex1 = i
                MaxIndex2 = j
            max_foldchange_values[i][j] = max_foldchange
            max_L_values[i][j] = max_L
            max_RPU[i][j] = max_RPU_value
    # 将结果输出到CSV文件
    filename_foldchange = 'new_foldchange_max_values.csv'
    filename_max_L = 'new_max_L_values.csv'
    output='new_output.csv'

    with open(filename_foldchange, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['LBD_name'] + kd_labels
        writer.writerow(header)
        for i, params in enumerate(LBD_parameters):
            row = [params['LBD_name']] + (max_foldchange_values[i]).tolist()
            writer.writerow(row)

    with open(filename_max_L, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['LBD_name'] + kd_labels
        writer.writerow(header)
        for i, params in enumerate(LBD_parameters):
            row = [params['LBD_name']] + max_L_values[i].tolist()
            writer.writerow(row)

    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['LBD_name'] + kd_labels
        writer.writerow(header)
        for i, params in enumerate(LBD_parameters):
            row = [params['LBD_name']] + max_RPU[i].tolist()
            writer.writerow(row)
    print(MaxIndex1)
    print(MaxIndex2)
    LBD = LBD_parameters[MaxIndex1]['LBD_name']
    DBD = kd_labels[MaxIndex2]
    L = max_L_values[MaxIndex1][MaxIndex2]
    RPU = max_RPU[MaxIndex1][MaxIndex2]
    return [MaxFoldChange,LBD,DBD,L,RPU]

if __name__ == "__main__":
    print(HtmlReturn(1,1))
