from Entity import Part
import requests
#导入所有DBD(包括Part表信息及DBD数据)
# def GetDBDList(cur):
#     sql = "select pt.partid,pt.Name,pt.Alias,pt.Level0Sequence,pt.SourceOrganism,pt.Reference,pt.Note,pt.ConfirmedSequence,pt.InsertSequence,dbdt.I0,dbdt.kd from PartTable as pt join DBDTable as dbdt where dbdt.Name = pt.Name;"
#     cur.execute(sql)
#     result = cur.fetchall()
#     DBDList = []
#     for each in result:
#         dbd = DBD(each[1],each[3],each[2],each[7],each[8],each[4],each[5],each[6],each[9])
#         DBDList.append(dbd)
#     return DBDList

def GetDBDList(api_url,session):
    response = session.get(f'{api_url}/WebDatabase/GerDBDList')
    DBDList = []
    if(response.status_code == 200):
        result = response.json()
        for each in result:
            # Name,Level0Sequence,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note,I0,kd
            dbd = DBD(each['Name'],each['Level0Sequence'],each['Alias'],each['ConfirmedSequence'],each['InsertSequence'],each['SourceOrganism'],each['Reference'],each['Note'],each['I0'],each['kd'])
            DBDList.append(dbd)
    return DBDList



#导入一个
def GetDBD(api_url,Name,session):
    # sql = "select pt.partid,pt.Name,pt.Alias,pt.Level0Sequence,pt.SourceOrganism,pt.Reference,pt.Note,pt.ConfirmedSequence,pt.InsertSequence,dbdt.I0,dbdt.kd from PartTable as pt join DBDTable as dbdt where dbdt.Name = pt.Name and pt.Name = '"+Name+"';"
    # cur.execute(sql)
    # result = cur.fetchall()
    # for each in result:
    #     dbd = DBD(each[1],each[3],each[2],each[7],each[8],each[4],each[5],each[6],each[9])
    # return dbd
    response = session.get(f'{api_url}/WebDatabase/GetDBDAllByName?name={Name}')
    if(response.status_code == 200):
        result = response.json()[0]
        dbd = DBD(result['Name'],result['Level0Sequence'],result['Alias'],result['ConfirmedSequence'],result['InsertSequence'],result['SourceOrganism'],result['Reference'],result['Note'],result['I0'],result['kd'])
        return dbd
    return None

def GetDBDKdI0(api_url, name, session):
    response = session.get(f"{api_url}/WebDatabase/GetDBDKdI0/{name}")
    if(response.status_code == 200):
        result = response.json()
        print(result)
        return result
    return None

def GetDBDMenu(api_url,session):
    # sql = "select Name,I0,kd from dbdtable;"
    # DBDMenu = {}
    # cur.execute(sql)
    # result = cur.fetchall()
    # for each in result:
    #     DBDMenu[each[0]] = [float(each[1]),float(each[2])]
    # return DBDMenu
    response = session.get(f'{api_url}/WebDatabase/GetDBDMenu')
    print(f'{api_url}/WebDatabase/GetDBDMenu')
    print(response.json())
    if(response.status_code == 200):
        result = response.json()
        DBDMenu = {}
        for each in result:
            DBDMenu[each['name']] = [float(each['i0']),float(each['kd'])]
        return DBDMenu


def GetDBDNameList(api_url,session):
    # sql = "select Name from dbdtable;"
    # DBDNameList = []
    # cur.execute(sql)
    # result = cur.fetchall()
    # for each in result:
    #     DBDNameList.append(each[0])
    # return DBDNameList
    response = session.get(f'{api_url}/WebDatabase/GetDBDNameList')
    if(response.status_code == 200):
        print(response.json())
        return response.json()


def GetDBDKdList(api_url,session):
    # sql = "select kd from dbdtable;"
    # DBDList = []
    # cur.execute(sql)
    # result = cur.fetchall()
    # for each in result:
    #     DBDList.append(each[0])
    # return DBDList
    response = session.get(f'{api_url}/WebDatabase/GetDBDKdList')
    if(response.status_code == 200):
        return response.json()

def GetDBDKd(api_url,Name,session):
    # sql = "select kd from DBDTable where Name = '"+Name+"';"
    # cur.execute(sql)
    # result = cur.fetchall()
    # return result[0][0]
    response = session.get(f'{api_url}/WebDatabase/GetDBDKd?name={Name}')
    if(response.status_code == 200):
        return response.json()['Kd']


class DBD(Part.Part):
    def __init__(self,Name,Level0Sequence,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note,I0,kd):
        super().__init__(Name,Level0Sequence,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note)
        self.Type = "DBD"
        self.I0 = I0
        self.kd = kd
    def save(self,api_url,session):
        # sql = "insert into DBDTable (Name,I0,kd) values ('"+self.Name+"',"+str(self.I0)+","+str(self.kd)+");"
        # cur.execute(sql)
        # conn.commit()
        payload = {
            'name': self.Name,
            'i0': self.I0,
            'kd': self.kd,
        }
        endpoint = f'{api_url.rstrip("/")}/WebDatabase/AddDBD'
        csrf_token = session.cookies.get('csrftoken')
        headers = {
            'Referer': f'{api_url.rstrip("/")}/WebDatabase/',
        }
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        # AddDBD reads request.POST, so this must be form data rather than JSON.
        response = session.post(endpoint, data=payload, headers=headers)
        if not (response.status_code == 200):
            raise ValueError(
                f'AddDBD returned HTTP {response.status_code}: '
                f'{response.text or "empty response"}'
            )

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text
