import requests
# def GetBackbone(Name,cur):
#     sql = "select Name,Length,Sequence,Ori,Marker,Species,CopyNumber,Notes,Scar from BackboneTable where Name = '"+Name+"';"
#     cur.execute(sql)
#     result = cur.fetchall()
#     if(len(result) != 0):
#         return Backbone(result[0][0],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6],result[0][7],result[0][8])
#     else:
#         return None

def GetBackbone(api_url,Name,session):
    response = session.get(f'{api_url}/WebDatabase/BackboneName?name={Name}')
    if(response.status_code == 200):
        result = response.json()[0]
        backbone = Backbone(result['name'],result['sequence'],result['ori'],result['marker'],
                 result['species'],result['copynumber'],result['notes'],result['scar'])
        return backbone
    else:
        return None


class Backbone():
    def __init__(self,Name,Sequence,Ori,Marker,Species=None,CopyNumber=None,Notes=None,Scar=None):
        self.Name = Name
        self.Length = len(Sequence)
        self.Sequence = Sequence
        self.Ori = Ori
        self.Marker = Marker
        self.Species = Species
        self.CopyNumber = CopyNumber
        self.Notes = Notes
        self.Scar = Scar

    def GetFileAddress(self,api_url,session):
        # sql = "select fileaddress from tb_backbone_userfileaddress as tbf join BackboneTable as bt where bt.Name = '"+self.Name+"' and tbf.backboneid = bt.ID;"
        # cur.execute(sql)
        # result = cur.fetchall()
        # if(len(result) != 0):
        #     return result[0][0]
        # else:
        #     return None
        response = session.get(f'{api_url}/WebDatabase/BackboneFile?name={self.Name}')
        if(response.status_code == 200):
            return response.json()
        else:
            return None