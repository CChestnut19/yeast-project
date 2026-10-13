from Entity import Part
import requests
#导入所有表明强度的终止子
def GetTerminatorList(api_url,session):
    response = session.get(f'{api_url}/WebDatabase/PartType?type=terminator')
    if(response.status_code == 200):
        result = response.json()
        terminatorList = []
        for each in result:
            terminatorRPU = session.get(f'{api_url}/WebDatabase/SearchRPU?partID={each["partid"]}')
            # for each_rpu in terminatorRPU:
            #     if(each_rpu['rpu'] > 0):
            #         # Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note
            #         terminatorList.append(Terminator(each['name'],each['level0sequence'],each_rpu['rpu'],each['alias'],each['confirmedsequence'],each['insertsequence'],
            #                                      each['sourceorganism'],each['reference'],each['note']))
            #         break
            if(terminatorRPU.status_code == 200):
                terminatorRPU = terminatorRPU.json()
                if(len(terminatorRPU) > 0):
                    print(terminatorRPU)
                    for each_rpu in terminatorRPU:
                        if(each_rpu['rpu'] > 0):
                            # Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note
                            terminatorList.append(Terminator(each['name'],each['level0sequence'],each_rpu['rpu'],each['alias'],each['confirmedsequence'],each['insertsequence'],
                                                each['sourceorganism'],each['reference'],each['note']))
                        break
        return terminatorList
    else:
        return []
    # sql = "select pt.partid,pt.Name,pt.Alias,pt.Level0Sequence,pt.SourceOrganism,pt.Reference,pt.Note,prt.RPU,pt.ConfirmedSequence,pt.InsertSequence from PartTable as pt join partrputable as prt on pt.Type=3 and pt.partid = prt.partid and prt.rpu>0;"
    # cur.execute(sql)
    # result = cur.fetchall()
    # TerminatorList = []
    # for each in result:
    #     # Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note
    #     terminator = Terminator(each[1],each[3],each[7],each[2],each[8],each[9],each[4],each[5],each[6])
    #     TerminatorList.append(terminator)
    # return TerminatorList
class Terminator(Part.Part):
    def __init__(self,Name,Level0Sequence,Strength,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note):
        super().__init__(Name,Level0Sequence,Alias,ConfirmedSequence,InsertSequence,SourceOrganism,Reference,Note)
        self.Strength = Strength
        self.Type = "Terminator"