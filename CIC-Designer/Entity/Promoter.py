from Entity import Part
import requests
def GetPromoterList(api_url,session):
    response = session.get(f'{api_url}/WebDatabase/PartType?type=promoter')
    if(response.status_code == 200):
        result = response.json()
        PromoterList = []
        for each in result:
            promoterRPU = session.get(f'{api_url}/WebDatabase/SearchRPU?partID={each["partid"]}')
            if(promoterRPU.status_code == 200):
                promoterRPU = promoterRPU.json()
                if(len(promoterRPU) > 0):
                    print(promoterRPU)
                    for each_rpu in promoterRPU:
                        if(each_rpu['rpu'] > 0):
                            # Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note
                            PromoterList.append(Promoter(each['name'],each['level0sequence'],each_rpu['rpu'],each['alias'],each['confirmedsequence'],each['insertsequence'],
                                            each['sourceorganism'],each['reference'],each['note']))
                            break
            
        return PromoterList
    else:
        return []
#     sql = "select pt.partid,pt.Name,pt.Alias,pt.Level0Sequence,pt.SourceOrganism,pt.Reference,pt.Note,prt.RPU,pt.ConfirmedSequence,pt.InsertSequence from PartTable as pt join partrputable as prt on pt.Type = 1 and pt.partid = prt.partid and prt.rpu>0;"
#     cur.execute(sql)
#     result = cur.fetchall()
#     PromoterList = []
#     for each in result:
#         # Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note
#         promoter = Promoter(each[1],each[3],each[7],each[2],each[8],each[9],each[4],each[5],each[6])
#         PromoterList.append(promoter)
#     return PromoterList
class Promoter(Part.Part):
    def __init__(self,Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note):
        super().__init__(Name,Level0Sequence,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note)
        self.Strength = Strength
        self.Type = "Promoter"
