# WebDatabase 源码校验 API 文档

> 本文档由 Django URL 配置与对应视图源码生成并人工约束：只记录仓库中可验证的行为。
> 请求/响应示例为源码推导示例，并非线上抓包结果；部署域名、权限策略和实际数据以运行环境为准。

## 快速开始

- 基础路径：`{BASE_URL}/WebDatabase/`
- 示例部署地址（来自项目既有文档）：`http://10.30.76.2:8080`
- 认证方式：Django Session/Cookie。先登录并保留 `sessionid`；源码中的具体权限检查并不完全一致。
- CSRF：启用 Django CSRF 中间件。对未标记 `csrf_exempt` 的状态变更请求，应同时发送 CSRF Cookie 与 `X-CSRFToken`。
- API 版本：URL 未包含版本号，仓库中未发现统一的版本协商机制。
- 限流：源码中未发现统一限流配置。
- 内容类型：依端点使用 query、表单、multipart、JSON 或页面渲染；详见各条目。

```bash
export BASE_URL=http://10.30.76.2:8080
export SESSION_ID=replace-with-session-id
export CSRF_TOKEN=replace-with-csrf-token
```

## 通用响应与错误约定

- `JsonResponse` 端点返回 JSON；`render`/`redirect` 端点返回 HTML 或 3xx；文件端点返回二进制响应。
- 视图大量使用自定义 JSON 字段表达成功/失败，不能仅依赖 HTTP 状态码判断业务结果。
- 可能出现的框架级错误包括 `403 CSRF verification failed`、未登录跳转、`404` 以及未捕获异常导致的 `500`。
- 下列“显式状态码”只列出源码直接写出的 `status=` 数值；未列出不代表只会返回 200。

## 端点索引

| # | 方法 | 路径 | 类型 | 视图 |
|---:|---|---|---|---|
| 1 | `GET` | `/WebDatabase/StrainName` | JSON API | `views.SearchByStrainName` |
| 2 | `GET` | `/WebDatabase/Part` | JSON API | `views.PartDataALL` |
| 3 | `GET` | `/WebDatabase/partcount` | JSON API | `views.PartCount` |
| 4 | `GET` | `/WebDatabase/PartByID` | JSON API | `views.SearchByPartID` |
| 5 | `GET` | `/WebDatabase/PartName` | JSON API | `views.SearchByPartName` |
| 6 | `GET` | `/WebDatabase/PartAlias` | JSON API | `views.SearchByPartAlterName` |
| 7 | `GET` | `/WebDatabase/PartType` | JSON API | `views.SearchByPartType` |
| 8 | `GET` | `/WebDatabase/TypeByName` | JSON API | `views.SearchPartTypeByName` |
| 9 | `GET` | `/WebDatabase/TypeByID` | JSON API | `views.SearchPartTypeByID` |
| 10 | `GET` | `/WebDatabase/PartRPU` | JSON API | `views.SearchByRPU` |
| 11 | `GET` | `/WebDatabase/PartSeq` | JSON API | `views.SearchBySeq` |
| 12 | `GET` | `/WebDatabase/PartFile` | JSON API | `views.SearchPartFile` |
| 13 | `GET` | `/WebDatabase/SearchRPU` | JSON API | `views.GetPartRPU` |
| 14 | `GET` | `/WebDatabase/PartID` | JSON API | `views.GetPartIDByName` |
| 15 | `GET` | `/WebDatabase/PartNameByID` | JSON API | `views.GetPartNameByID` |
| 16 | `GET` | `/WebDatabase/GetPartSeqByID` | JSON API | `views.GetPartSeqByID` |
| 17 | `GET` | `/WebDatabase/PartAliasByID` | JSON API | `views.GetPartAliasByID` |
| 18 | `POST` | `/WebDatabase/AddPartRPU` | JSON API | `views.AddPartRPU` |
| 19 | `POST` | `/WebDatabase/AddPartData` | JSON API | `views.AddPartData` |
| 20 | `POST` | `/WebDatabase/AddPartFile` | JSON API | `views.AddPartFileAddress` |
| 21 | `POST` | `/WebDatabase/UpdatePart` | JSON API | `views.UpdatePart` |
| 22 | `POST` | `/WebDatabase/UpdatePartFile` | JSON API | `views.UpdatePartFileAddress` |
| 23 | `POST` | `/WebDatabase/UpdatePartRPU` | JSON API | `views.UpdatePartRPU` |
| 24 | `GET` | `/WebDatabase/deletePart` | JSON API | `views.deletePartData` |
| 25 | `GET` | `/WebDatabase/deletePartFile` | JSON API | `views.deletePartFile` |
| 26 | `POST` | `/WebDatabase/PartFilter` | JSON API | `views.PartFilter` |
| 27 | `POST` | `/WebDatabase/UpdatePartSequence` | JSON API | `views.UpdatePartSequence` |
| 28 | `GET` | `/WebDatabase/partlistbyuser/<str:username>` | JSON API | `views.PartListByUser` |
| 29 | `GET/POST` | `/WebDatabase/partfields` | JSON API | `views.PartFields` |
| 30 | `GET` | `/WebDatabase/partSource/<int:partID>` | JSON API | `views.GetPartSource` |
| 31 | `GET/POST` | `/WebDatabase/deletePartFeature` | HTTP 接口 | `views.deletePartFeature` |
| 32 | `GET/POST` | `/WebDatabase/AddPartFeature/<str:PartName>` | HTTP 接口 | `views.AddPartFeature` |
| 33 | `GET/POST` | `/WebDatabase/UpdatePartFeature` | HTTP 接口 | `views.UpdatePartFeature` |
| 34 | `GET/POST` | `/WebDatabase/GetPartFeature/<int:PartID>` | HTTP 接口 | `views.GetPartFeature` |
| 35 | `GET` | `/WebDatabase/plasmidcount` | JSON API | `views.PlasmidCount` |
| 36 | `GET` | `/WebDatabase/Plasmid` | JSON API | `views.PlasmidDataALL` |
| 37 | `GET` | `/WebDatabase/PlasmidName` | JSON API | `views.SearchByPlasmidName` |
| 38 | `GET` | `/WebDatabase/PlasmidByID` | JSON API | `views.SearchByPlasmidID` |
| 39 | `GET` | `/WebDatabase/PlasmidAlterName` | JSON API | `views.SearchByPlasmidAlterName` |
| 40 | `GET` | `/WebDatabase/PlasmidSeqByName` | JSON API | `views.SearchPlasmidSequenceByName` |
| 41 | `GET` | `/WebDatabase/PlasmidSeqByID` | JSON API | `views.SearchPlasmidSequenceByID` |
| 42 | `GET` | `/WebDatabase/PlasmidSeq` | JSON API | `views.SearchByPlasmidSeq` |
| 43 | `GET` | `/WebDatabase/PlasmidOri` | JSON API | `views.SearchByOri` |
| 44 | `GET` | `/WebDatabase/PlasmidMarker` | JSON API | `views.SearchByMarker` |
| 45 | `GET` | `/WebDatabase/PlasmidLevel` | JSON API | `views.SearchByLevel` |
| 46 | `GET` | `/WebDatabase/PlasmidPlate` | JSON API | `views.SearchByPlate` |
| 47 | `GET` | `/WebDatabase/PlasmidParent` | JSON API | `views.SearchPlasmidParent` |
| 48 | `GET` | `/WebDatabase/PlasmidParentByID` | JSON API | `views.SearchPlasmidParentByID` |
| 49 | `GET` | `/WebDatabase/GetParentID` | JSON API | `views.GetParentID` |
| 50 | `GET` | `/WebDatabase/PlasmidID` | JSON API | `views.GetPlasmidIDByName` |
| 51 | `GET` | `/WebDatabase/PlasmidNameByID` | JSON API | `views.GetPlasmidNameByID` |
| 52 | `GET` | `/WebDatabase/PlasmidAliasByID` | JSON API | `views.GetPlasmidAliasByID` |
| 53 | `GET` | `/WebDatabase/PlasmidFile` | JSON API | `views.SearchPlasmidFileAddress` |
| 54 | `POST` | `/WebDatabase/AddPlasmidFile` | JSON API | `views.AddPlasmidFileAddress` |
| 55 | `POST` | `/WebDatabase/AddPlasmidData` | JSON API | `views.AddPlasmidData` |
| 56 | `POST` | `/WebDatabase/UpdatePlasmid` | JSON API | `views.UpdatePlasmidData` |
| 57 | `POST` | `/WebDatabase/UpdatePlasmidFile` | JSON API | `views.UpdatePlasmidFileAddress` |
| 58 | `GET` | `/WebDatabase/deletePlasmid` | JSON API | `views.deletePlasmidData` |
| 59 | `GET` | `/WebDatabase/deletePlasmidFile` | JSON API | `views.deletePlasmidFileAddress` |
| 60 | `GET` | `/WebDatabase/deletePlasmidParent` | JSON API | `views.DeleteParentPlasmid` |
| 61 | `POST` | `/WebDatabase/PlasmidFilter` | JSON API | `views.PlasmidFilter` |
| 62 | `POST` | `/WebDatabase/UpdateParentInfo` | JSON API | `views.AddPlasmidParentInfo` |
| 63 | `POST` | `/WebDatabase/setPlasmidCulture` | JSON API | `views.setPlasmidCulture` |
| 64 | `GET` | `/WebDatabase/getPlasmidCulture` | JSON API | `views.getPlasmidCulture` |
| 65 | `POST` | `/WebDatabase/UpdatePlasmidSequence` | JSON API | `views.UpdatePlasmidSequence` |
| 66 | `GET` | `/WebDatabase/plasmidlistbyuser/<str:username>` | JSON API | `views.PlasmidListByUser` |
| 67 | `GET/POST` | `/WebDatabase/plasmidfields` | JSON API | `views.PlasmidFields` |
| 68 | `GET/POST` | `/WebDatabase/deletePlasmidFeature` | HTTP 接口 | `views.deletePlasmidFeature` |
| 69 | `GET/POST` | `/WebDatabase/AddPlasmidFeature/<str:PlasmidName>` | HTTP 接口 | `views.AddPlasmidFeature` |
| 70 | `GET/POST` | `/WebDatabase/UpdatePlasmidFeature` | HTTP 接口 | `views.UpdatePlasmidFeature` |
| 71 | `GET/POST` | `/WebDatabase/GetPlasmidFeature/<int:PlasmidID>` | HTTP 接口 | `views.GetPlasmidFeature` |
| 72 | `GET` | `/WebDatabase/backbonecount` | JSON API | `views.BackboneCount` |
| 73 | `GET` | `/WebDatabase/Backbone` | JSON API | `views.BackboneDataALL` |
| 74 | `GET` | `/WebDatabase/BackboneName` | JSON API | `views.SearchByBackboneName` |
| 75 | `GET` | `/WebDatabase/BackboneByID` | JSON API | `views.SearchByBackboneID` |
| 76 | `GET` | `/WebDatabase/BackboneSeq` | JSON API | `views.SearchByBackboneSeq` |
| 77 | `GET` | `/WebDatabase/GetBackboneSeqByID` | JSON API | `views.GetBackboneSeqByID` |
| 78 | `GET` | `/WebDatabase/BackboneSpecies` | JSON API | `views.SearchByBackboneSpecies` |
| 79 | `GET` | `/WebDatabase/BackboneOri` | JSON API | `views.SearchByBackboneOri` |
| 80 | `GET` | `/WebDatabase/BackboneMarker` | JSON API | `views.SearchByBackboneMarker` |
| 81 | `GET` | `/WebDatabase/BackboneCopyNumber` | JSON API | `views.SearchByCopyNumber` |
| 82 | `GET` | `/WebDatabase/BackboneFile` | JSON API | `views.SearchBackboneFileAddress` |
| 83 | `GET` | `/WebDatabase/BackboneID` | JSON API | `views.GetBackboneIDByName` |
| 84 | `GET` | `/WebDatabase/BackboneNameByID` | JSON API | `views.GetBackboneNameByID` |
| 85 | `GET` | `/WebDatabase/BackboneAliasByID` | JSON API | `views.GetBackboneAliasByID` |
| 86 | `POST` | `/WebDatabase/AddBackbone` | JSON API | `views.AddBackboneData` |
| 87 | `POST` | `/WebDatabase/AddBackboneFile` | JSON API | `views.AddBackboneFileAddress` |
| 88 | `POST` | `/WebDatabase/UpdateBackbone` | JSON API | `views.UpdateBackboneData` |
| 89 | `POST` | `/WebDatabase/UpdateBackboneFile` | JSON API | `views.UpdateBackboneFileAddress` |
| 90 | `GET` | `/WebDatabase/deleteBackbone` | JSON API | `views.DeleteBackboneData` |
| 91 | `GET` | `/WebDatabase/deleteBackboneFile` | JSON API | `views.DeleteBackboneFileAddress` |
| 92 | `POST` | `/WebDatabase/BackboneFilter` | JSON API | `views.BackboneFilter` |
| 93 | `POST` | `/WebDatabase/UpdateBackboneSequence` | JSON API | `views.UpdateBackboneSequence` |
| 94 | `POST` | `/WebDatabase/setBackboneCulture` | JSON API | `views.setBackboneCulture` |
| 95 | `GET` | `/WebDatabase/backbonelistbyuser/<str:username>` | JSON API | `views.BackboneListByUser` |
| 96 | `GET/POST` | `/WebDatabase/backbonefields` | JSON API | `views.BackboneFields` |
| 97 | `GET` | `/WebDatabase/deleteBackboneFeature` | JSON API | `views.deleteBackboneFeature` |
| 98 | `POST` | `/WebDatabase/AddBackboneFeature/<str:BackboneName>` | JSON API | `views.AddBackboneFeature` |
| 99 | `GET` | `/WebDatabase/GetBackboneFeature/<int:BackboneID>` | JSON API | `views.GetBackboneFeature` |
| 100 | `GET` | `/WebDatabase/TestDataName` | JSON API | `views.SearchByTestdataName` |
| 101 | `GET` | `/WebDatabase/GetDBDList` | JSON API | `views.GetDBDList` |
| 102 | `GET` | `/WebDatabase/GetDBDNameList` | JSON API | `views.GetDBDNameList` |
| 103 | `GET` | `/WebDatabase/GetDBDKdList` | JSON API | `views.GetDBDKdList` |
| 104 | `GET` | `/WebDatabase/GetDBD` | JSON API | `views.GetDBD` |
| 105 | `GET` | `/WebDatabase/GetDBDAllByName` | JSON API | `views.GetDBDAllByName` |
| 106 | `GET` | `/WebDatabase/GetDBDMenu` | JSON API | `views.GetDBDMenu` |
| 107 | `GET` | `/WebDatabase/GetDBDKd` | JSON API | `views.GetDBDKd` |
| 108 | `POST` | `/WebDatabase/AddDBD` | JSON API | `views.AddDBD` |
| 109 | `POST` | `/WebDatabase/UpdateDBD` | JSON API | `views.UpdateDBD` |
| 110 | `GET` | `/WebDatabase/GetLBDDimer` | JSON API | `views.GetLBDDimer` |
| 111 | `GET` | `/WebDatabase/GetLBDDimerMenu` | JSON API | `views.GetLBDDimerMenu` |
| 112 | `GET` | `/WebDatabase/GetLBDDimerNameList` | JSON API | `views.GetLBDDimerNameList` |
| 113 | `GET` | `/WebDatabase/GetLBDDimerAllByName` | JSON API | `views.GetLBDDimerAllByName` |
| 114 | `POST` | `/WebDatabase/ADDLBDDimer` | JSON API | `views.AddLBDDimer` |
| 115 | `POST` | `/WebDatabase/UpdateLbdDimer` | JSON API | `views.UpdateLbdDimer` |
| 116 | `GET` | `/WebDatabase/GetLBDNr` | JSON API | `views.GetLBDNr` |
| 117 | `GET` | `/WebDatabase/GetLBDNRMenu` | JSON API | `views.GetLBDNRMenu` |
| 118 | `GET` | `/WebDatabase/GetLBDAllByName` | JSON API | `views.GetLBDNRAllByName` |
| 119 | `GET` | `/WebDatabase/GetLBDNRNameList` | JSON API | `views.GetLBDNRNameList` |
| 120 | `POST` | `/WebDatabase/AddLbdnr` | JSON API | `views.AddLbdnr` |
| 121 | `POST` | `/WebDatabase/UpdateLBDnr` | JSON API | `views.UpdateLBDnr` |
| 122 | `POST` | `/WebDatabase/login` | 页面/跳转 | `account.login_view` |
| 123 | `GET/POST` | `/WebDatabase/logout` | 页面/跳转 | `account.logout` |
| 124 | `POST` | `/WebDatabase/register` | 页面/跳转 | `account.register` |
| 125 | `POST` | `/WebDatabase/AdminRegister` | 页面/跳转 | `account.admin_register` |
| 126 | `GET` | `/WebDatabase/reset` | 页面/跳转 | `account.reset_password` |
| 127 | `GET` | `/WebDatabase/PartNameFilter` | JSON API | `views.SearchByPartNameFilter` |
| 128 | `GET` | `/WebDatabase/BackboneNameFilter` | JSON API | `views.SearchByBackboneNameFilter` |
| 129 | `GET` | `/WebDatabase/PlasmidNameFilter` | JSON API | `views.SearchByPlasmidNameFilter` |
| 130 | `POST` | `/WebDatabase/AddPartParent` | JSON API | `views.AddParentPart` |
| 131 | `POST` | `/WebDatabase/AddPartParentByID` | JSON API | `views.AddParentPartByID` |
| 132 | `POST` | `/WebDatabase/AddBackboneParent` | JSON API | `views.AddParentBackbone` |
| 133 | `POST` | `/WebDatabase/AddBackboneParentByID` | JSON API | `views.AddBackboneParentByID` |
| 134 | `POST` | `/WebDatabase/AddPlasmidParent` | JSON API | `views.AddParentPlasmid` |
| 135 | `POST` | `/WebDatabase/AddPlasmidParentByID` | JSON API | `views.AddPlasmidParentByID` |
| 136 | `GET` | `/WebDatabase/GetPartParent` | JSON API | `views.GetParentPart` |
| 137 | `GET` | `/WebDatabase/GetBackboneParent` | JSON API | `views.GetParentBackbone` |
| 138 | `GET` | `/WebDatabase/GetPlasmidParent` | JSON API | `views.GetParentPlasmid` |
| 139 | `GET` | `/WebDatabase/GetPlasmidSon` | JSON API | `views.GetSonPlasmid` |
| 140 | `GET` | `/WebDatabase/GetPlasmidRelations` | JSON API | `views.GetPlasmidRelations` |
| 141 | `GET` | `/WebDatabase/GetUploadRecords` | JSON API | `views.GetUploadRecords` |
| 142 | `GET` | `/WebDatabase/DeletePlasmidParent` | JSON API | `views.DeletePlasmidParent` |
| 143 | `GET` | `/WebDatabase/getPartValueList/<str:column>` | JSON API | `views.getPartValueList` |
| 144 | `GET` | `/WebDatabase/getBackboneValueList/<str:column>` | JSON API | `views.getBackboneValueList` |
| 145 | `GET` | `/WebDatabase/getPlasmidValueList/<str:column>` | JSON API | `views.getPlasmidValueList` |
| 146 | `GET` | `/WebDatabase/getPartScarList` | JSON API | `views.getPartScarList` |
| 147 | `GET` | `/WebDatabase/getBackboneScarList` | JSON API | `views.getBackboneScarList` |
| 148 | `GET` | `/WebDatabase/getPlasmidScarList` | JSON API | `views.getPlasmidScarList` |
| 149 | `GET` | `/WebDatabase/getPartScar` | JSON API | `views.getPartScar` |
| 150 | `POST` | `/WebDatabase/setPartScar` | JSON API | `views.setPartScar` |
| 151 | `GET` | `/WebDatabase/getBackboneScar` | JSON API | `views.getBackboneScar` |
| 152 | `POST` | `/WebDatabase/setBackboneScar` | JSON API | `views.setBackboneScar` |
| 153 | `GET` | `/WebDatabase/getPlasmidScar` | JSON API | `views.getPlasmidScar` |
| 154 | `POST` | `/WebDatabase/setPlasmidScar` | JSON API | `views.setPlasmidScar` |
| 155 | `GET` | `/WebDatabase/getuserlist` | JSON API | `views.getuserlist` |
| 156 | `GET` | `/WebDatabase/getalluseruploadlist` | JSON API | `views.getAllUserUploadList` |
| 157 | `GET` | `/WebDatabase/getuserpartcount/<str:uname>` | JSON API | `views.getUserPartCount` |
| 158 | `GET` | `/WebDatabase/getuserbackbonecount/<str:uname>` | JSON API | `views.getUserBackboneCount` |
| 159 | `GET` | `/WebDatabase/getuserplasmidcount/<str:uname>` | JSON API | `views.getUserPlasmidCount` |
| 160 | `GET` | `/WebDatabase/getrepocountbyuser/<str:uid>` | JSON API | `views.getUserrepositoryCount` |
| 161 | `POST` | `/WebDatabase/createRepo` | JSON API | `views.create_repository` |
| 162 | `GET` | `/WebDatabase/getrepos` | JSON API | `views.get_repositories` |
| 163 | `POST` | `/WebDatabase/getrepo` | JSON API | `views.get_repository` |
| 164 | `POST` | `/WebDatabase/addparts` | JSON API | `views.add_part_to_repository` |
| 165 | `POST` | `/WebDatabase/addbackbones` | JSON API | `views.add_backbone_to_repository` |
| 166 | `POST` | `/WebDatabase/addplasmids` | JSON API | `views.add_plasmid_to_repository` |
| 167 | `POST` | `/WebDatabase/removeparts` | JSON API | `views.remove_part_from_repository` |
| 168 | `GET` | `/WebDatabase/getparts` | JSON API | `views.get_repository_parts` |
| 169 | `POST` | `/WebDatabase/createVisitorProfile` | JSON API | `views.createVisitorProfile` |
| 170 | `GET` | `/WebDatabase/getVisitorProfile` | JSON API | `views.getVisitorProfile` |
| 171 | `GET` | `/WebDatabase/listVisitorProfiles` | JSON API | `views.listVisitorProfiles` |
| 172 | `POST` | `/WebDatabase/updateVisitorProfile` | JSON API | `views.updateVisitorProfile` |
| 173 | `POST` | `/WebDatabase/deleteVisitorProfile` | JSON API | `views.deleteVisitorProfile` |
| 174 | `POST` | `/WebDatabase/createVisitorFeedback` | JSON API | `views.createVisitorFeedback` |
| 175 | `POST` | `/WebDatabase/createVisitorAccessLog` | JSON API | `views.createVisitorAccessLog` |
| 176 | `GET` | `/WebDatabase/getVisitorAccessLog` | JSON API | `views.getVisitorAccessLog` |
| 177 | `GET` | `/WebDatabase/listVisitorAccessLogs` | JSON API | `views.listVisitorAccessLogs` |
| 178 | `POST` | `/WebDatabase/updateVisitorAccessLog` | JSON API | `views.updateVisitorAccessLog` |
| 179 | `POST` | `/WebDatabase/deleteVisitorAccessLog` | JSON API | `views.deleteVisitorAccessLog` |

## 端点详情

### 1. `GET /WebDatabase/StrainName`

**用途：** Strain Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:176`（`views.SearchByStrainName`）
**源码说明：** 閫氳繃鑿屾牚鍚嶇О锛圢ame锛夎幏鍙栨暣浣撴€т俊鎭? Args: request: django request GET Args: name: 鑿屾牚鍚嶇О Returns: JsonResponse: 1. status_code = 200 list data if search successfully, 2. status_code = 400/404 string data, if search unsuccessfully
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/StrainName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/StrainName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 2. `GET /WebDatabase/Part`

**用途：** Part。接口类型：JSON API。

**源码：** `WebDatabase/views.py:246`（`views.PartDataALL`）
**源码说明：** 鑾峰彇part table鐨勬墍鏈夋暟鎹潯鐩紝浠ame鎺掑簭 Args: request: django request Returns: JsonResponse: 1.JsonResponse.json()[0] = a data dict, JsonResponse.status_code = 200, if search successfully and Page = 0 2.JsonResponse.json() = "No such part", if search successfully 3.JsonResponse.json()["success"] = True, JsonResponse.json()['data'] = a part data dict in one page, JsonResponse.json()["pagination"] = page information, if search successfully and Page != 0
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `page` | query | string | 由视图逻辑决定 |
| `page_size` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/Part?page=example&page_size=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/Part"
response = session.get(url, params={"page": "example", "page_size": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 3. `GET /WebDatabase/partcount`

**用途：** Part Count。接口类型：JSON API。

**源码：** `WebDatabase/views.py:227`（`views.PartCount`）
**源码说明：** 鑾峰彇Part table鐨勬暟鎹潯鏁? Args: request: django request Returns: JsonResponse: 1.JsonResponse.json()["success"]=True, JsonResponse.json()["data"]=integer(鏁版嵁鏉℃暟),JsonResponse.status_code=200 if search successfully, 2.JsonResponse.json()['success'] = False,JsonResponse.json()["message"] = Error Information, JsonResponse.status_code=400/200 if search unsuccessfully.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/partcount" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/partcount"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 4. `GET /WebDatabase/PartByID`

**用途：** Part By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:572`（`views.SearchByPartID`）
**源码说明：** SearchByPartID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 5. `GET /WebDatabase/PartName`

**用途：** Part Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:411`（`views.SearchByPartName`）
**源码说明：** Args: request: django request Returns: JsonResponse: 1.JsonResponse.json()["success"] = True, JsonResponse.json()["data"] = A dict of data, JsonResponse.status = 200, if search successfully, 2. JsonResponse.json() = error information, JsonResponse.status_code = 400/404, if search unsuccessfully
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 6. `GET /WebDatabase/PartAlias`

**用途：** Part Alias。接口类型：JSON API。

**源码：** `WebDatabase/views.py:601`（`views.SearchByPartAlterName`）
**源码说明：** SearchByPartAlterName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `AlterName` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartAlias?AlterName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartAlias"
response = session.get(url, params={"AlterName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 7. `GET /WebDatabase/PartType`

**用途：** Part Type。接口类型：JSON API。

**源码：** `WebDatabase/views.py:629`（`views.SearchByPartType`）
**源码说明：** SearchByPartType API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `type` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartType?type=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartType"
response = session.get(url, params={"type": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 8. `GET /WebDatabase/TypeByName`

**用途：** Type By Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:667`（`views.SearchPartTypeByName`）
**源码说明：** SearchPartTypeByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/TypeByName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/TypeByName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 9. `GET /WebDatabase/TypeByID`

**用途：** Type By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:711`（`views.SearchPartTypeByID`）
**源码说明：** SearchPartTypeByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/TypeByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/TypeByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 10. `GET /WebDatabase/PartRPU`

**用途：** Part R P U。接口类型：JSON API。

**源码：** `WebDatabase/views.py:763`（`views.SearchByRPU`）
**源码说明：** SearchByRPU API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `rpu` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartRPU?rpu=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartRPU"
response = session.get(url, params={"rpu": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 11. `GET /WebDatabase/PartSeq`

**用途：** Part Seq。接口类型：JSON API。

**源码：** `WebDatabase/views.py:816`（`views.SearchBySeq`）
**源码说明：** SearchBySeq API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `seq` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartSeq?seq=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartSeq"
response = session.get(url, params={"seq": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 12. `GET /WebDatabase/PartFile`

**用途：** Part File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:843`（`views.SearchPartFile`）
**源码说明：** SearchPartFile API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartFile?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartFile"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 13. `GET /WebDatabase/SearchRPU`

**用途：** Search R P U。接口类型：JSON API。

**源码：** `WebDatabase/views.py:793`（`views.GetPartRPU`）
**源码说明：** GetPartRPU API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/SearchRPU?partID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/SearchRPU"
response = session.get(url, params={"partID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 14. `GET /WebDatabase/PartID`

**用途：** Part I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4419`（`views.GetPartIDByName`）
**源码说明：** GetPartIDByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartID?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartID"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 15. `GET /WebDatabase/PartNameByID`

**用途：** Part Name By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4443`（`views.GetPartNameByID`）
**源码说明：** GetPartNameByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartNameByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartNameByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 16. `GET /WebDatabase/GetPartSeqByID`

**用途：** Get Part Seq By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4481`（`views.GetPartSeqByID`）
**源码说明：** GetPartSeqByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPartSeqByID?partid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPartSeqByID"
response = session.get(url, params={"partid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 17. `GET /WebDatabase/PartAliasByID`

**用途：** Part Alias By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4466`（`views.GetPartAliasByID`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartAliasByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartAliasByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 18. `POST /WebDatabase/AddPartRPU`

**用途：** Add Part R P U。接口类型：JSON API。

**源码：** `WebDatabase/views.py:879`（`views.AddPartRPU`）
**源码说明：** AddPartRPU API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Name` | form | string | 由视图逻辑决定 |
| `Note` | form | string | 由视图逻辑决定 |
| `rpu` | form | string | 由视图逻辑决定 |
| `testStrain` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPartRPU" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "Name=example" \
  --data-urlencode "Note=example" \
  --data-urlencode "rpu=example" \
  --data-urlencode "testStrain=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartRPU"
response = session.post(url, data={"Name": "example", "Note": "example", "rpu": "example", "testStrain": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 19. `POST /WebDatabase/AddPartData`

**用途：** Add Part Data。接口类型：JSON API。

**源码：** `WebDatabase/views.py:907`（`views.AddPartData`）
**源码说明：** AddPartData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ConfirmedSequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `InsertSequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Level0Sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `reference` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `source` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPartData" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ConfirmedSequence\": \"example\", \"InsertSequence\": \"example\", \"Level0Sequence\": \"example\", \"alias\": \"example\", \"name\": \"example\", \"note\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartData"
response = session.post(url, json={"ConfirmedSequence": "example", "InsertSequence": "example", "Level0Sequence": "example", "alias": "example", "name": "example", "note": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 20. `POST /WebDatabase/AddPartFile`

**用途：** Add Part File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:985`（`views.AddPartFileAddress`）
**源码说明：** AddPartFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PartName` | form | string | 由视图逻辑决定 |
| `fileAddress` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPartFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "PartName=example" \
  --data-urlencode "fileAddress=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartFile"
response = session.post(url, data={"PartName": "example", "fileAddress": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 21. `POST /WebDatabase/UpdatePart`

**用途：** Update Part。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1022`（`views.UpdatePart`）
**源码说明：** UpdatePart API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ConfirmedSequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `InsertSequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Level0Sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `OriginalName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `PartID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `reference` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `source` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePart" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Alias\": \"example\", \"ConfirmedSequence\": \"example\", \"InsertSequence\": \"example\", \"Level0Sequence\": \"example\", \"Name\": \"example\", \"OriginalName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePart"
response = session.post(url, json={"Alias": "example", "ConfirmedSequence": "example", "InsertSequence": "example", "Level0Sequence": "example", "Name": "example", "OriginalName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 22. `POST /WebDatabase/UpdatePartFile`

**用途：** Update Part File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1107`（`views.UpdatePartFileAddress`）
**源码说明：** UpdatePartFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Address` | form | string | 由视图逻辑决定 |
| `PartName` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePartFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "Address=example" \
  --data-urlencode "PartName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePartFile"
response = session.post(url, data={"Address": "example", "PartName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 23. `POST /WebDatabase/UpdatePartRPU`

**用途：** Update Part R P U。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1073`（`views.UpdatePartRPU`）
**源码说明：** UpdatePartRPU API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Name` | form | string | 由视图逻辑决定 |
| `note` | form | string | 由视图逻辑决定 |
| `rpu` | form | string | 由视图逻辑决定 |
| `testStrain` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePartRPU" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "Name=example" \
  --data-urlencode "note=example" \
  --data-urlencode "rpu=example" \
  --data-urlencode "testStrain=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePartRPU"
response = session.post(url, data={"Name": "example", "note": "example", "rpu": "example", "testStrain": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 24. `GET /WebDatabase/deletePart`

**用途：** delete Part。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1138`（`views.deletePartData`）
**源码说明：** deletePartData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePart?partid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePart"
response = session.get(url, params={"partid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 25. `GET /WebDatabase/deletePartFile`

**用途：** delete Part File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1171`（`views.deletePartFile`）
**源码说明：** deletePartFile API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePartFile?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePartFile"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 26. `POST /WebDatabase/PartFilter`

**用途：** Part Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:294`（`views.PartFilter`）
**源码说明：** Part Table Filter Function, Filter selections are type, Enzyme, Scar, name Args: request: django request Returns: JsonResponse: 1.JsonResponse.json()["success"] = True, JsonResponse.json()["data"] = a list of data dict, JsonResponse.json()["pagination"] = a dict of page information, JsonResponse.status_code = 200, if search successfully 2.JsonResponse.json()["success"] = False, JsonResponse.json()["error"] = error information, if search unsuccessfully
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Enzyme` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page_size` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/PartFilter" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Enzyme\": \"example\", \"Scar\": \"example\", \"name\": \"example\", \"page\": \"example\", \"page_size\": \"example\", \"type\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartFilter"
response = session.post(url, json={"Enzyme": "example", "Scar": "example", "name": "example", "page": "example", "page_size": "example", "type": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 27. `POST /WebDatabase/UpdatePartSequence`

**用途：** Update Part Sequence。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5368`（`views.UpdatePartSequence`）
**源码说明：** UpdatePartSequence API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Level0Sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePartSequence" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Level0Sequence\": \"example\", \"name\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePartSequence"
response = session.post(url, json={"Level0Sequence": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 28. `GET /WebDatabase/partlistbyuser/<str:username>`

**用途：** partlistbyuser。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1199`（`views.PartListByUser`）
**源码说明：** PartListByUser API view. Args: request: Django HttpRequest object. username: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `username` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/partlistbyuser/example-username" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/partlistbyuser/example-username"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 29. `GET/POST /WebDatabase/partfields`

**用途：** partfields。接口类型：JSON API。

**源码：** `WebDatabase/views.py:207`（`views.PartFields`）
**源码说明：** 鑾峰彇Parttable鎵€鏈夌浉鍏崇瓫閫変俊鎭」锛屼笉鍖呮嫭arentparttable锛宲artrputable锛宲artscartable锛宼bpartuserfileaddress Args: request: django request Returns: JsonResponse: 1. JsonResponse.json()["success"] = True, JsonResponse.json()['data'] = data, JsonResponse.status_code=200 list if successfully search, 2. JsonResponse.json()["success"] = False, JsonResponse.json()["message"] = Error Information, JsonResponse.status_code = 400, if search unsuccessfully.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/partfields" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/partfields"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 30. `GET /WebDatabase/partSource/<int:partID>`

**用途：** part Source。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1222`（`views.GetPartSource`）
**源码说明：** GetPartSource API view. Args: request: Django HttpRequest object. partID: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partID` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/partSource/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/partSource/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 31. `GET/POST /WebDatabase/deletePartFeature`

**用途：** deletepartfeature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3857`（`views.deletePartFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePartFeature" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePartFeature"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 32. `GET/POST /WebDatabase/AddPartFeature/<str:PartName>`

**用途：** Add Part Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3845`（`views.AddPartFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PartName` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/AddPartFeature/example-PartName" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartFeature/example-PartName"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 33. `GET/POST /WebDatabase/UpdatePartFeature`

**用途：** Update Part Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3853`（`views.UpdatePartFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/UpdatePartFeature" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePartFeature"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 34. `GET/POST /WebDatabase/GetPartFeature/<int:PartID>`

**用途：** Get Part Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3849`（`views.GetPartFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PartID` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPartFeature/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPartFeature/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 35. `GET /WebDatabase/plasmidcount`

**用途：** Plasmidcount。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1246`（`views.PlasmidCount`）
**源码说明：** PlasmidCount API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/plasmidcount" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/plasmidcount"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 36. `GET /WebDatabase/Plasmid`

**用途：** Plasmid。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1301`（`views.PlasmidDataALL`）
**源码说明：** PlasmidDataALL API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `page` | query | string | 由视图逻辑决定 |
| `page_size` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/Plasmid?page=example&page_size=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/Plasmid"
response = session.get(url, params={"page": "example", "page_size": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 37. `GET /WebDatabase/PlasmidName`

**用途：** Plamsid Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1539`（`views.SearchByPlasmidName`）
**源码说明：** SearchByPlasmidName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 38. `GET /WebDatabase/PlasmidByID`

**用途：** Plasmid By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1570`（`views.SearchByPlasmidID`）
**源码说明：** SearchByPlasmidID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 39. `GET /WebDatabase/PlasmidAlterName`

**用途：** Plasmid Alter Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1601`（`views.SearchByPlasmidAlterName`）
**源码说明：** SearchByPlasmidAlterName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `altername` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidAlterName?altername=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidAlterName"
response = session.get(url, params={"altername": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 40. `GET /WebDatabase/PlasmidSeqByName`

**用途：** Plasmid Seq。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1663`（`views.SearchPlasmidSequenceByName`）
**源码说明：** SearchPlasmidSequenceByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidSeqByName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidSeqByName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 41. `GET /WebDatabase/PlasmidSeqByID`

**用途：** Plasmid Seq By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1702`（`views.SearchPlasmidSequenceByID`）
**源码说明：** SearchPlasmidSequenceByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidSeqByID?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidSeqByID"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 42. `GET /WebDatabase/PlasmidSeq`

**用途：** Plasmid Seq。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1632`（`views.SearchByPlasmidSeq`）
**源码说明：** SearchByPlasmidSeq API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `seq` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidSeq?seq=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidSeq"
response = session.get(url, params={"seq": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 43. `GET /WebDatabase/PlasmidOri`

**用途：** Plasmid Ori。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1731`（`views.SearchByOri`）
**源码说明：** SearchByOri API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `oriClone` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidOri?oriClone=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidOri"
response = session.get(url, params={"oriClone": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 44. `GET /WebDatabase/PlasmidMarker`

**用途：** Plasmid Marker。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1766`（`views.SearchByMarker`）
**源码说明：** SearchByMarker API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `markerHost` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidMarker?markerHost=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidMarker"
response = session.get(url, params={"markerHost": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 45. `GET /WebDatabase/PlasmidLevel`

**用途：** Plasmid Level。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1801`（`views.SearchByLevel`）
**源码说明：** SearchByLevel API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `level` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidLevel?level=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidLevel"
response = session.get(url, params={"level": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 46. `GET /WebDatabase/PlasmidPlate`

**用途：** Plasmid Plate。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1833`（`views.SearchByPlate`）
**源码说明：** SearchByPlate API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plate` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidPlate?plate=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidPlate"
response = session.get(url, params={"plate": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 47. `GET /WebDatabase/PlasmidParent`

**用途：** Plasmid Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1865`（`views.SearchPlasmidParent`）
**源码说明：** SearchPlasmidParent API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidName` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidParent?plasmidName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidParent"
response = session.get(url, params={"plasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 48. `GET /WebDatabase/PlasmidParentByID`

**用途：** Plasmid Parent By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1901`（`views.SearchPlasmidParentByID`）
**源码说明：** SearchPlasmidParentByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidParentByID?plasmidID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidParentByID"
response = session.get(url, params={"plasmidID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 49. `GET /WebDatabase/GetParentID`

**用途：** Get Parent I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1932`（`views.GetParentID`）
**源码说明：** GetParentID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetParentID?plasmidID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetParentID"
response = session.get(url, params={"plasmidID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 50. `GET /WebDatabase/PlasmidID`

**用途：** Plasmid I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4573`（`views.GetPlasmidIDByName`）
**源码说明：** GetPlasmidIDByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidID?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidID"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 51. `GET /WebDatabase/PlasmidNameByID`

**用途：** Plasmid Name By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4597`（`views.GetPlasmidNameByID`）
**源码说明：** GetPlasmidNameByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidNameByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidNameByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 52. `GET /WebDatabase/PlasmidAliasByID`

**用途：** Plasmid Alias By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4621`（`views.GetPlasmidAliasByID`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidAliasByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidAliasByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 53. `GET /WebDatabase/PlasmidFile`

**用途：** Plasmid File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1964`（`views.SearchPlasmidFileAddress`）
**源码说明：** SearchPlasmidFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidFile?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidFile"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 54. `POST /WebDatabase/AddPlasmidFile`

**用途：** Add Plasmid File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2000`（`views.AddPlasmidFileAddress`）
**源码说明：** AddPlasmidFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `address` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPlasmidFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "address=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPlasmidFile"
response = session.post(url, data={"address": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 55. `POST /WebDatabase/AddPlasmidData`

**用途：** Add Plasmid Data。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2032`（`views.AddPlasmidData`）
**源码说明：** AddPlasmidData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentInfo` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `level` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plate` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `state` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `tag` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPlasmidData" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentInfo\": \"example\", \"alias\": \"example\", \"level\": \"example\", \"name\": \"example\", \"note\": \"example\", \"plate\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPlasmidData"
response = session.post(url, json={"ParentInfo": "example", "alias": "example", "level": "example", "name": "example", "note": "example", "plate": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 56. `POST /WebDatabase/UpdatePlasmid`

**用途：** Update Plasmid。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2395`（`views.UpdatePlasmidData`）
**源码说明：** UpdatePlasmidData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `OriginName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newAlias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newLevel` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newMarker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newNote` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newOri` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newPlate` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newSequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newState` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePlasmid" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"OriginName\": \"example\", \"id\": \"example\", \"newAlias\": \"example\", \"newLevel\": \"example\", \"newMarker\": \"example\", \"newName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePlasmid"
response = session.post(url, json={"OriginName": "example", "id": "example", "newAlias": "example", "newLevel": "example", "newMarker": "example", "newName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 57. `POST /WebDatabase/UpdatePlasmidFile`

**用途：** Update Plasmid File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2467`（`views.UpdatePlasmidFileAddress`）
**源码说明：** UpdatePlasmidFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `address` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePlasmidFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "address=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePlasmidFile"
response = session.post(url, data={"address": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 58. `GET /WebDatabase/deletePlasmid`

**用途：** delete Plasmid。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2500`（`views.deletePlasmidData`）
**源码说明：** deletePlasmidData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePlasmid?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePlasmid"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 59. `GET /WebDatabase/deletePlasmidFile`

**用途：** delete Plasmid File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2542`（`views.deletePlasmidFileAddress`）
**源码说明：** deletePlasmidFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PlasmidName` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePlasmidFile?PlasmidName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePlasmidFile"
response = session.get(url, params={"PlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 60. `GET /WebDatabase/deletePlasmidParent`

**用途：** delete Plasmid Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2571`（`views.DeleteParentPlasmid`）
**源码说明：** DeleteParentPlasmid API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidName` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePlasmidParent?plasmidName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePlasmidParent"
response = session.get(url, params={"plasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 61. `POST /WebDatabase/PlasmidFilter`

**用途：** Plasmid Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:1361`（`views.PlasmidFilter`）
**源码说明：** PlasmidFilter API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Enzyme` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page_size` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/PlasmidFilter" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Enzyme\": \"example\", \"Scar\": \"example\", \"marker\": \"example\", \"name\": \"example\", \"ori\": \"example\", \"page\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidFilter"
response = session.post(url, json={"Enzyme": "example", "Scar": "example", "marker": "example", "name": "example", "ori": "example", "page": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 62. `POST /WebDatabase/UpdateParentInfo`

**用途：** Update Parent Info。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4635`（`views.AddPlasmidParentInfo`）
**源码说明：** AddPlasmidParentInfo API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PlasmidID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `PlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `PlasmidParentInfo` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateParentInfo" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"PlasmidID\": \"example\", \"PlasmidName\": \"example\", \"PlasmidParentInfo\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateParentInfo"
response = session.post(url, json={"PlasmidID": "example", "PlasmidName": "example", "PlasmidParentInfo": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 63. `POST /WebDatabase/setPlasmidCulture`

**用途：** set Plasmid Culture。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2598`（`views.setPlasmidCulture`）
**源码说明：** setPlasmidCulture API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/setPlasmidCulture" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"marker\": \"example\", \"name\": \"example\", \"ori\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/setPlasmidCulture"
response = session.post(url, json={"marker": "example", "name": "example", "ori": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 64. `GET /WebDatabase/getPlasmidCulture`

**用途：** get Plasmid Culture。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2646`（`views.getPlasmidCulture`）
**源码说明：** getPlasmidCulture API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidId` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPlasmidCulture?plasmidId=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPlasmidCulture"
response = session.get(url, params={"plasmidId": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 65. `POST /WebDatabase/UpdatePlasmidSequence`

**用途：** Update Plasmid Sequence。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5434`（`views.UpdatePlasmidSequence`）
**源码说明：** UpdatePlasmidSequence API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdatePlasmidSequence" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"name\": \"example\", \"sequence\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePlasmidSequence"
response = session.post(url, json={"name": "example", "sequence": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 66. `GET /WebDatabase/plasmidlistbyuser/<str:username>`

**用途：** plasmidlistbyuser。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2691`（`views.PlasmidListByUser`）
**源码说明：** PlasmidListByUser API view. Args: request: Django HttpRequest object. username: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `username` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/plasmidlistbyuser/example-username" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/plasmidlistbyuser/example-username"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 67. `GET/POST /WebDatabase/plasmidfields`

**用途：** plasmidfields。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2669`（`views.PlasmidFields`）
**源码说明：** PlasmidFields API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/plasmidfields" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/plasmidfields"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 68. `GET/POST /WebDatabase/deletePlasmidFeature`

**用途：** deleteplasmidfeature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3873`（`views.deletePlasmidFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deletePlasmidFeature" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deletePlasmidFeature"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 69. `GET/POST /WebDatabase/AddPlasmidFeature/<str:PlasmidName>`

**用途：** Add Plasmid Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3861`（`views.AddPlasmidFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PlasmidName` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/AddPlasmidFeature/example-PlasmidName" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPlasmidFeature/example-PlasmidName"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 70. `GET/POST /WebDatabase/UpdatePlasmidFeature`

**用途：** Update Plasmid Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3869`（`views.UpdatePlasmidFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/UpdatePlasmidFeature" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdatePlasmidFeature"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 71. `GET/POST /WebDatabase/GetPlasmidFeature/<int:PlasmidID>`

**用途：** Get Plasmid Feature。接口类型：HTTP 接口。

**源码：** `WebDatabase/views.py:3865`（`views.GetPlasmidFeature`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `未从源码静态确定`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PlasmidID` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPlasmidFeature/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPlasmidFeature/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 72. `GET /WebDatabase/backbonecount`

**用途：** backbonecount。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2722`（`views.BackboneCount`）
**源码说明：** BackboneCount API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/backbonecount" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/backbonecount"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 73. `GET /WebDatabase/Backbone`

**用途：** Backbone。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2756`（`views.BackboneDataALL`）
**源码说明：** BackboneDataALL API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `page` | query | string | 由视图逻辑决定 |
| `page_size` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/Backbone?page=example&page_size=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/Backbone"
response = session.get(url, params={"page": "example", "page_size": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 74. `GET /WebDatabase/BackboneName`

**用途：** Backbone Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3016`（`views.SearchByBackboneName`）
**源码说明：** SearchByBackboneName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 75. `GET /WebDatabase/BackboneByID`

**用途：** Backbone I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3045`（`views.SearchByBackboneID`）
**源码说明：** SearchByBackboneID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 76. `GET /WebDatabase/BackboneSeq`

**用途：** Backbone Seq。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3076`（`views.SearchByBackboneSeq`）
**源码说明：** SearchByBackboneSeq API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `seq` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneSeq?seq=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneSeq"
response = session.get(url, params={"seq": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 77. `GET /WebDatabase/GetBackboneSeqByID`

**用途：** Get Backbone Seq By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3107`（`views.GetBackboneSeqByID`）
**源码说明：** GetBackboneSeqByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backboneid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetBackboneSeqByID?backboneid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetBackboneSeqByID"
response = session.get(url, params={"backboneid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 78. `GET /WebDatabase/BackboneSpecies`

**用途：** Backbone Species。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3135`（`views.SearchByBackboneSpecies`）
**源码说明：** SearchByBackboneSpecies API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `species` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneSpecies?species=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneSpecies"
response = session.get(url, params={"species": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 79. `GET /WebDatabase/BackboneOri`

**用途：** Backbone Ori。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3201`（`views.SearchByBackboneOri`）
**源码说明：** SearchByBackboneOri API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ori` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneOri?ori=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneOri"
response = session.get(url, params={"ori": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 80. `GET /WebDatabase/BackboneMarker`

**用途：** Backbone Marker。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3166`（`views.SearchByBackboneMarker`）
**源码说明：** SearchByBackboneMarker API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `marker` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneMarker?marker=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneMarker"
response = session.get(url, params={"marker": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 81. `GET /WebDatabase/BackboneCopyNumber`

**用途：** Backbone Copy Number。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3232`（`views.SearchByCopyNumber`）
**源码说明：** SearchByCopyNumber API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `copynumber` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneCopyNumber?copynumber=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneCopyNumber"
response = session.get(url, params={"copynumber": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 82. `GET /WebDatabase/BackboneFile`

**用途：** Backbone File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3261`（`views.SearchBackboneFileAddress`）
**源码说明：** SearchBackboneFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneFile?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneFile"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 83. `GET /WebDatabase/BackboneID`

**用途：** Backbone I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4510`（`views.GetBackboneIDByName`）
**源码说明：** GetBackboneIDByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneID?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneID"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 84. `GET /WebDatabase/BackboneNameByID`

**用途：** Backbone Name By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4534`（`views.GetBackboneNameByID`）
**源码说明：** GetBackboneNameByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneNameByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneNameByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 85. `GET /WebDatabase/BackboneAliasByID`

**用途：** Backbone Alias By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4557`（`views.GetBackboneAliasByID`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ID` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneAliasByID?ID=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneAliasByID"
response = session.get(url, params={"ID": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 86. `POST /WebDatabase/AddBackbone`

**用途：** Add Backbone。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3293`（`views.AddBackboneData`）
**源码说明：** AddBackboneData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `copynumber` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `species` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `tag` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddBackbone" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"alias\": \"example\", \"copynumber\": \"example\", \"name\": \"example\", \"note\": \"example\", \"sequence\": \"example\", \"species\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddBackbone"
response = session.post(url, json={"alias": "example", "copynumber": "example", "name": "example", "note": "example", "sequence": "example", "species": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 87. `POST /WebDatabase/AddBackboneFile`

**用途：** Add Backbone File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3358`（`views.AddBackboneFileAddress`）
**源码说明：** AddBackboneFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `address` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddBackboneFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "address=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddBackboneFile"
response = session.post(url, data={"address": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 88. `POST /WebDatabase/UpdateBackbone`

**用途：** Update Backbone。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3386`（`views.UpdateBackboneData`）
**源码说明：** UpdateBackboneData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `BackboneID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `OriginalName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `copynumber` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `newName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `species` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `tag` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateBackbone" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"BackboneID\": \"example\", \"OriginalName\": \"example\", \"alias\": \"example\", \"copynumber\": \"example\", \"newName\": \"example\", \"note\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateBackbone"
response = session.post(url, json={"BackboneID": "example", "OriginalName": "example", "alias": "example", "copynumber": "example", "newName": "example", "note": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 89. `POST /WebDatabase/UpdateBackboneFile`

**用途：** Update Backbone File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3450`（`views.UpdateBackboneFileAddress`）
**源码说明：** UpdateBackboneFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `address` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateBackboneFile" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"address\": \"example\", \"name\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateBackboneFile"
response = session.post(url, json={"address": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 90. `GET /WebDatabase/deleteBackbone`

**用途：** delete Backbone。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3480`（`views.DeleteBackboneData`）
**源码说明：** DeleteBackboneData API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backboneid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deleteBackbone?backboneid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deleteBackbone"
response = session.get(url, params={"backboneid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 91. `GET /WebDatabase/deleteBackboneFile`

**用途：** delete Backbone File。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3517`（`views.DeleteBackboneFileAddress`）
**源码说明：** DeleteBackboneFileAddress API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deleteBackboneFile?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deleteBackboneFile"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 92. `POST /WebDatabase/BackboneFilter`

**用途：** Backbone Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2815`（`views.BackboneFilter`）
**源码说明：** BackboneFilter API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Enzyme` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page_size` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/BackboneFilter" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Enzyme\": \"example\", \"Scar\": \"example\", \"marker\": \"example\", \"name\": \"example\", \"ori\": \"example\", \"page\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneFilter"
response = session.post(url, json={"Enzyme": "example", "Scar": "example", "marker": "example", "name": "example", "ori": "example", "page": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 93. `POST /WebDatabase/UpdateBackboneSequence`

**用途：** Update Backbone Sequence。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5403`（`views.UpdateBackboneSequence`）
**源码说明：** UpdateBackboneSequence API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateBackboneSequence" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"name\": \"example\", \"sequence\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateBackboneSequence"
response = session.post(url, json={"name": "example", "sequence": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 94. `POST /WebDatabase/setBackboneCulture`

**用途：** set Backbone Culture。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3545`（`views.setBackboneCulture`）
**源码说明：** setBackboneCulture API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/setBackboneCulture" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"id\": \"example\", \"marker\": \"example\", \"name\": \"example\", \"ori\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/setBackboneCulture"
response = session.post(url, json={"id": "example", "marker": "example", "name": "example", "ori": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 95. `GET /WebDatabase/backbonelistbyuser/<str:username>`

**用途：** backbonelistbyuser。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3612`（`views.BackboneListByUser`）
**源码说明：** BackboneListByUser API view. Args: request: Django HttpRequest object. username: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `username` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/backbonelistbyuser/example-username" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/backbonelistbyuser/example-username"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 96. `GET/POST /WebDatabase/backbonefields`

**用途：** backbonefields。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3594`（`views.BackboneFields`）
**源码说明：** BackboneFields API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/backbonefields" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/backbonefields"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 97. `GET /WebDatabase/deleteBackboneFeature`

**用途：** deletebackbonefeature。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3635`（`views.deleteBackboneFeature`）
**源码说明：** deleteBackboneFeature API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/deleteBackboneFeature?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deleteBackboneFeature"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 98. `POST /WebDatabase/AddBackboneFeature/<str:BackboneName>`

**用途：** Add Backbone Feature。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3659`（`views.AddBackboneFeature`）
**源码说明：** AddBackboneFeature API view. Args: request: Django HttpRequest object. BackboneName: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `BackboneName` | path | str | 必需 |
| `ape_info` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `color` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `end_position` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `feature_type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `label` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `start_position` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddBackboneFeature/example-BackboneName" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ape_info\": \"example\", \"color\": \"example\", \"end_position\": \"example\", \"feature_type\": \"example\", \"label\": \"example\", \"start_position\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddBackboneFeature/example-BackboneName"
response = session.post(url, json={"ape_info": "example", "color": "example", "end_position": "example", "feature_type": "example", "label": "example", "start_position": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 99. `GET /WebDatabase/GetBackboneFeature/<int:BackboneID>`

**用途：** Get Backbone Feature。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3696`（`views.GetBackboneFeature`）
**源码说明：** GetBackboneFeature API view. Args: request: Django HttpRequest object. BackboneID: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `BackboneID` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetBackboneFeature/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetBackboneFeature/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 100. `GET /WebDatabase/TestDataName`

**用途：** Test Data Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3880`（`views.SearchByTestdataName`）
**源码说明：** SearchByTestdataName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/TestDataName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/TestDataName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 101. `GET /WebDatabase/GetDBDList`

**用途：** Get D B D List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3911`（`views.GetDBDList`）
**源码说明：** GetDBDList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 102. `GET /WebDatabase/GetDBDNameList`

**用途：** Get D B D Name List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3936`（`views.GetDBDNameList`）
**源码说明：** GetDBDNameList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDNameList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDNameList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 103. `GET /WebDatabase/GetDBDKdList`

**用途：** Get D B D Kd List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3958`（`views.GetDBDKdList`）
**源码说明：** GetDBDKdList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDKdList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDKdList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 104. `GET /WebDatabase/GetDBD`

**用途：** Get D B D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:3980`（`views.GetDBD`）
**源码说明：** GetDBD API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBD?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBD"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 105. `GET /WebDatabase/GetDBDAllByName`

**用途：** Get D B D By All Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4003`（`views.GetDBDAllByName`）
**源码说明：** GetDBDAllByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDAllByName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDAllByName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 106. `GET /WebDatabase/GetDBDMenu`

**用途：** Get D B D Menu。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4028`（`views.GetDBDMenu`）
**源码说明：** GetDBDMenu API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDMenu" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDMenu"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 107. `GET /WebDatabase/GetDBDKd`

**用途：** Get D B D Kd。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4050`（`views.GetDBDKd`）
**源码说明：** GetDBDKd API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetDBDKd?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetDBDKd"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 108. `POST /WebDatabase/AddDBD`

**用途：** Add D B D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4073`（`views.AddDBD`）
**源码说明：** AddDBD API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `i0` | form | string | 由视图逻辑决定 |
| `kd` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddDBD" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "i0=example" \
  --data-urlencode "kd=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddDBD"
response = session.post(url, data={"i0": "example", "kd": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 109. `POST /WebDatabase/UpdateDBD`

**用途：** Update D B D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4093`（`views.UpdateDBD`）
**源码说明：** UpdateDBD API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `i0` | form | string | 由视图逻辑决定 |
| `kd` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateDBD" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "i0=example" \
  --data-urlencode "kd=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateDBD"
response = session.post(url, data={"i0": "example", "kd": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 110. `GET /WebDatabase/GetLBDDimer`

**用途：** Get L B D Dimer。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4122`（`views.GetLBDDimer`）
**源码说明：** GetLBDDimer API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDDimer" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDDimer"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 111. `GET /WebDatabase/GetLBDDimerMenu`

**用途：** Get L B D Dimer Menu。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4147`（`views.GetLBDDimerMenu`）
**源码说明：** GetLBDDimerMenu API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDDimerMenu" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDDimerMenu"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 112. `GET /WebDatabase/GetLBDDimerNameList`

**用途：** Get L B D Dimer Name List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4196`（`views.GetLBDDimerNameList`）
**源码说明：** GetLBDDimerNameList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDDimerNameList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDDimerNameList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 113. `GET /WebDatabase/GetLBDDimerAllByName`

**用途：** Get L B D Dimer All By Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4170`（`views.GetLBDDimerAllByName`）
**源码说明：** GetLBDDimerAllByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDDimerAllByName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDDimerAllByName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 114. `POST /WebDatabase/ADDLBDDimer`

**用途：** A D D L B D Dimer。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4218`（`views.AddLBDDimer`）
**源码说明：** AddLBDDimer API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `i` | form | string | 由视图逻辑决定 |
| `k1` | form | string | 由视图逻辑决定 |
| `k2` | form | string | 由视图逻辑决定 |
| `k3` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/ADDLBDDimer" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "i=example" \
  --data-urlencode "k1=example" \
  --data-urlencode "k2=example" \
  --data-urlencode "k3=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/ADDLBDDimer"
response = session.post(url, data={"i": "example", "k1": "example", "k2": "example", "k3": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 115. `POST /WebDatabase/UpdateLbdDimer`

**用途：** Update Lbd Dimer。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4241`（`views.UpdateLbdDimer`）
**源码说明：** UpdateLbdDimer API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `i` | form | string | 由视图逻辑决定 |
| `k1` | form | string | 由视图逻辑决定 |
| `k2` | form | string | 由视图逻辑决定 |
| `k3` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateLbdDimer" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "i=example" \
  --data-urlencode "k1=example" \
  --data-urlencode "k2=example" \
  --data-urlencode "k3=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateLbdDimer"
response = session.post(url, data={"i": "example", "k1": "example", "k2": "example", "k3": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 116. `GET /WebDatabase/GetLBDNr`

**用途：** Get L B D Nr。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4272`（`views.GetLBDNr`）
**源码说明：** GetLBDNr API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDNr" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDNr"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 117. `GET /WebDatabase/GetLBDNRMenu`

**用途：** Get L B D N R Menu。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4299`（`views.GetLBDNRMenu`）
**源码说明：** GetLBDNRMenu API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDNRMenu" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDNRMenu"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 118. `GET /WebDatabase/GetLBDAllByName`

**用途：** Get L B D N R All By Name。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4322`（`views.GetLBDNRAllByName`）
**源码说明：** GetLBDNRAllByName API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDAllByName?name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDAllByName"
response = session.get(url, params={"name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 119. `GET /WebDatabase/GetLBDNRNameList`

**用途：** Get L B D N R Name List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4348`（`views.GetLBDNRNameList`）
**源码说明：** GetLBDNRNameList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetLBDNRNameList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetLBDNRNameList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 120. `POST /WebDatabase/AddLbdnr`

**用途：** Add Lbdnr。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4371`（`views.AddLbdnr`）
**源码说明：** AddLbdnr API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `k1` | form | string | 由视图逻辑决定 |
| `k2` | form | string | 由视图逻辑决定 |
| `k3` | form | string | 由视图逻辑决定 |
| `kx1` | form | string | 由视图逻辑决定 |
| `kx2` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddLbdnr" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "k1=example" \
  --data-urlencode "k2=example" \
  --data-urlencode "k3=example" \
  --data-urlencode "kx1=example" \
  --data-urlencode "kx2=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddLbdnr"
response = session.post(url, data={"k1": "example", "k2": "example", "k3": "example", "kx1": "example", "kx2": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 121. `POST /WebDatabase/UpdateLBDnr`

**用途：** Update L B Dnr。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4395`（`views.UpdateLBDnr`）
**源码说明：** UpdateLBDnr API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `k1` | form | string | 由视图逻辑决定 |
| `k2` | form | string | 由视图逻辑决定 |
| `k3` | form | string | 由视图逻辑决定 |
| `kx1` | form | string | 由视图逻辑决定 |
| `kx2` | form | string | 由视图逻辑决定 |
| `name` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/UpdateLBDnr" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "k1=example" \
  --data-urlencode "k2=example" \
  --data-urlencode "k3=example" \
  --data-urlencode "kx1=example" \
  --data-urlencode "kx2=example" \
  --data-urlencode "name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/UpdateLBDnr"
response = session.post(url, data={"k1": "example", "k2": "example", "k3": "example", "kx1": "example", "kx2": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 122. `POST /WebDatabase/login`

**用途：** login。接口类型：页面/跳转。

**源码：** `WebDatabase/account.py:327`（`account.login_view`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`, `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `next` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/login" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/login"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 123. `GET/POST /WebDatabase/logout`

**用途：** logout。接口类型：页面/跳转。

**源码：** `WebDatabase/account.py:400`（`account.logout`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/logout" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/logout"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 124. `POST /WebDatabase/register`

**用途：** register。接口类型：页面/跳转。

**源码：** `WebDatabase/account.py:371`（`account.register`）
**源码说明：** 用户注册视图
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`, `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/register" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/register"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 125. `POST /WebDatabase/AdminRegister`

**用途：** Admin Register。接口类型：页面/跳转。

**源码：** `WebDatabase/account.py:409`（`account.admin_register`）
**源码说明：** 用户注册视图
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`, `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AdminRegister" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AdminRegister"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 126. `GET /WebDatabase/reset`

**用途：** resetpassword。接口类型：页面/跳转。

**源码：** `WebDatabase/account.py:443`（`account.reset_password`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`, `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/reset" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/reset"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 127. `GET /WebDatabase/PartNameFilter`

**用途：** Part Name Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:444`（`views.SearchByPartNameFilter`）
**源码说明：** Args: request: django request Returns: JsonResponse: 1. JsonResponse.json() = Part dict, JsonResponse.status_code = 200, if search successfully, 2. JsonResponse.json() = error information, JsonResponse.status_code = 400/404, if search unsuccessfully.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Type` | query | string | 由视图逻辑决定 |
| `keywords` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PartNameFilter?Type=example&keywords=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PartNameFilter"
response = session.get(url, params={"Type": "example", "keywords": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 128. `GET /WebDatabase/BackboneNameFilter`

**用途：** Backbone Name Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:503`（`views.SearchByBackboneNameFilter`）
**源码说明：** SearchByBackboneNameFilter API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `keywords` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/BackboneNameFilter?keywords=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/BackboneNameFilter"
response = session.get(url, params={"keywords": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 129. `GET /WebDatabase/PlasmidNameFilter`

**用途：** Plasmid Name Filter。接口类型：JSON API。

**源码：** `WebDatabase/views.py:537`（`views.SearchByPlasmidNameFilter`）
**源码说明：** SearchByPlasmidNameFilter API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `keywords` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/PlasmidNameFilter?keywords=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/PlasmidNameFilter"
response = session.get(url, params={"keywords": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 130. `POST /WebDatabase/AddPartParent`

**用途：** Add Part Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4676`（`views.AddParentPart`）
**源码说明：** AddParentPart API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentPartName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidId` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPartParent" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentPartName\": \"example\", \"SonPlasmidId\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartParent"
response = session.post(url, json={"ParentPartName": "example", "SonPlasmidId": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 131. `POST /WebDatabase/AddPartParentByID`

**用途：** Add Part Parent By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4726`（`views.AddParentPartByID`）
**源码说明：** AddParentPartByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentPartID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPartParentByID" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentPartID\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPartParentByID"
response = session.post(url, json={"ParentPartID": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 132. `POST /WebDatabase/AddBackboneParent`

**用途：** Add Parent Backbone。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4773`（`views.AddParentBackbone`）
**源码说明：** AddParentBackbone API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentBackboneName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidId` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddBackboneParent" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentBackboneName\": \"example\", \"SonPlasmidId\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddBackboneParent"
response = session.post(url, json={"ParentBackboneName": "example", "SonPlasmidId": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 133. `POST /WebDatabase/AddBackboneParentByID`

**用途：** Add Backbone Parent By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4823`（`views.AddBackboneParentByID`）
**源码说明：** AddBackboneParentByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentBackboneID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddBackboneParentByID" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentBackboneID\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddBackboneParentByID"
response = session.post(url, json={"ParentBackboneID": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 134. `POST /WebDatabase/AddPlasmidParent`

**用途：** Add Parent Plasmid。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2123`（`views.AddParentPlasmid`）
**源码说明：** AddParentPlasmid API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidId` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPlasmidParent" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentPlasmidName\": \"example\", \"SonPlasmidId\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPlasmidParent"
response = session.post(url, json={"ParentPlasmidName": "example", "SonPlasmidId": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 135. `POST /WebDatabase/AddPlasmidParentByID`

**用途：** Add Plasmid Parent By I D。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2170`（`views.AddPlasmidParentByID`）
**源码说明：** AddPlasmidParentByID API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `ParentPlasmidID` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SonPlasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/AddPlasmidParentByID" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"ParentPlasmidID\": \"example\", \"SonPlasmidName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/AddPlasmidParentByID"
response = session.post(url, json={"ParentPlasmidID": "example", "SonPlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 136. `GET /WebDatabase/GetPartParent`

**用途：** Get Part Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2215`（`views.GetParentPart`）
**源码说明：** GetParentPart API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPartParent?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPartParent"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 137. `GET /WebDatabase/GetBackboneParent`

**用途：** Get Backbone Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2238`（`views.GetParentBackbone`）
**源码说明：** GetParentBackbone API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetBackboneParent?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetBackboneParent"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 138. `GET /WebDatabase/GetPlasmidParent`

**用途：** Get Plasmid Parent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2261`（`views.GetParentPlasmid`）
**源码说明：** GetParentPlasmid API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPlasmidParent?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPlasmidParent"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 139. `GET /WebDatabase/GetPlasmidSon`

**用途：** Get Plasmid Son。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2282`（`views.GetSonPlasmid`）
**源码说明：** GetSonPlasmid API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPlasmidSon?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPlasmidSon"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 140. `GET /WebDatabase/GetPlasmidRelations`

**用途：** Get Plasmid Relations。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2303`（`views.GetPlasmidRelations`）
**源码说明：** Return plasmid parent relationships and IDs matching a related keyword.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `keyword` | query | string | 由视图逻辑决定 |
| `plasmidids` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetPlasmidRelations?keyword=example&plasmidids=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetPlasmidRelations"
response = session.get(url, params={"keyword": "example", "plasmidids": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 141. `GET /WebDatabase/GetUploadRecords`

**用途：** Get Upload Records。接口类型：JSON API。

**源码：** `WebDatabase/views.py:2354`（`views.GetUploadRecords`）
**源码说明：** Query upload records without exposing WebDatabase models to other apps.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `filter` | query | string | 由视图逻辑决定 |
| `page` | query | string | 由视图逻辑决定 |
| `pagesize` | query | string | 由视图逻辑决定 |
| `table` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/GetUploadRecords?filter=example&page=example&pagesize=example&table=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/GetUploadRecords"
response = session.get(url, params={"filter": "example", "page": "example", "pagesize": "example", "table": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 142. `GET /WebDatabase/DeletePlasmidParent`

**用途：** deleteplasmidparent。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4871`（`views.DeletePlasmidParent`）
**源码说明：** DeletePlasmidParent API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/DeletePlasmidParent?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/DeletePlasmidParent"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 143. `GET /WebDatabase/getPartValueList/<str:column>`

**用途：** get Part Value List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4891`（`views.getPartValueList`）
**源码说明：** getPartValueList API view. Args: request: Django HttpRequest object. column: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `column` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPartValueList/example-column" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPartValueList/example-column"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 144. `GET /WebDatabase/getBackboneValueList/<str:column>`

**用途：** get Backbone Value List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4914`（`views.getBackboneValueList`）
**源码说明：** getBackboneValueList API view. Args: request: Django HttpRequest object. column: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `column` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getBackboneValueList/example-column" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getBackboneValueList/example-column"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 145. `GET /WebDatabase/getPlasmidValueList/<str:column>`

**用途：** get Plasmid Value List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4947`（`views.getPlasmidValueList`）
**源码说明：** getPlasmidValueList API view. Args: request: Django HttpRequest object. column: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `column` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPlasmidValueList/example-column" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPlasmidValueList/example-column"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 146. `GET /WebDatabase/getPartScarList`

**用途：** get Part Scar List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5250`（`views.getPartScarList`）
**源码说明：** getPartScarList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPartScarList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPartScarList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 147. `GET /WebDatabase/getBackboneScarList`

**用途：** get Backbone Scar List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5289`（`views.getBackboneScarList`）
**源码说明：** getBackboneScarList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getBackboneScarList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getBackboneScarList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 148. `GET /WebDatabase/getPlasmidScarList`

**用途：** get Plasmid Scar List。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5328`（`views.getPlasmidScarList`）
**源码说明：** getPlasmidScarList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPlasmidScarList" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPlasmidScarList"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 149. `GET /WebDatabase/getPartScar`

**用途：** get Part Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:4981`（`views.getPartScar`）
**源码说明：** getPartScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPartScar?id=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPartScar"
response = session.get(url, params={"id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 150. `POST /WebDatabase/setPartScar`

**用途：** set Part Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5009`（`views.setPartScar`）
**源码说明：** setPartScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `aari` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bbsi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsai` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsmbi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sapi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/setPartScar" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"aari\": \"example\", \"bbsi\": \"example\", \"bsai\": \"example\", \"bsmbi\": \"example\", \"name\": \"example\", \"sapi\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/setPartScar"
response = session.post(url, json={"aari": "example", "bbsi": "example", "bsai": "example", "bsmbi": "example", "name": "example", "sapi": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 151. `GET /WebDatabase/getBackboneScar`

**用途：** get Backbone Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5072`（`views.getBackboneScar`）
**源码说明：** getBackboneScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getBackboneScar?id=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getBackboneScar"
response = session.get(url, params={"id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 152. `POST /WebDatabase/setBackboneScar`

**用途：** set Backbone Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5102`（`views.setBackboneScar`）
**源码说明：** setBackboneScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `aari` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `backboneid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bbsi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsai` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsmbi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sapi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/setBackboneScar" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"aari\": \"example\", \"backboneid\": \"example\", \"bbsi\": \"example\", \"bsai\": \"example\", \"bsmbi\": \"example\", \"name\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/setBackboneScar"
response = session.post(url, json={"aari": "example", "backboneid": "example", "bbsi": "example", "bsai": "example", "bsmbi": "example", "name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 153. `GET /WebDatabase/getPlasmidScar`

**用途：** get Plasmid Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5166`（`views.getPlasmidScar`）
**源码说明：** getPlasmidScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getPlasmidScar?plasmidid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getPlasmidScar"
response = session.get(url, params={"plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 154. `POST /WebDatabase/setPlasmidScar`

**用途：** set Plasmid Scar。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5188`（`views.setPlasmidScar`）
**源码说明：** setPlasmidScar API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `aari` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bbsi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsai` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `bsmbi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmidid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sapi` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/setPlasmidScar" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"aari\": \"example\", \"bbsi\": \"example\", \"bsai\": \"example\", \"bsmbi\": \"example\", \"name\": \"example\", \"plasmidid\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/setPlasmidScar"
response = session.post(url, json={"aari": "example", "bbsi": "example", "bsai": "example", "bsmbi": "example", "name": "example", "plasmidid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 155. `GET /WebDatabase/getuserlist`

**用途：** getuserlist。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5467`（`views.getuserlist`）
**源码说明：** getuserlist API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getuserlist" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getuserlist"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 156. `GET /WebDatabase/getalluseruploadlist`

**用途：** getalluseruploaduser。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5484`（`views.getAllUserUploadList`）
**源码说明：** getAllUserUploadList API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getalluseruploadlist" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getalluseruploadlist"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 157. `GET /WebDatabase/getuserpartcount/<str:uname>`

**用途：** getuserpartcount。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5507`（`views.getUserPartCount`）
**源码说明：** getUserPartCount API view. Args: request: Django HttpRequest object. uname: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `uname` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getuserpartcount/example-uname" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getuserpartcount/example-uname"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 158. `GET /WebDatabase/getuserbackbonecount/<str:uname>`

**用途：** getuserbackbonecount。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5525`（`views.getUserBackboneCount`）
**源码说明：** getUserBackboneCount API view. Args: request: Django HttpRequest object. uname: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `uname` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getuserbackbonecount/example-uname" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getuserbackbonecount/example-uname"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 159. `GET /WebDatabase/getuserplasmidcount/<str:uname>`

**用途：** getuserplasmidcount。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5543`（`views.getUserPlasmidCount`）
**源码说明：** getUserPlasmidCount API view. Args: request: Django HttpRequest object. uname: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `uname` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getuserplasmidcount/example-uname" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getuserplasmidcount/example-uname"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 160. `GET /WebDatabase/getrepocountbyuser/<str:uid>`

**用途：** getrepocountbyuser。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5561`（`views.getUserrepositoryCount`）
**源码说明：** getUserrepositoryCount API view. Args: request: Django HttpRequest object. uid: Input parameter. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `uid` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getrepocountbyuser/example-uid" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getrepocountbyuser/example-uid"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 161. `POST /WebDatabase/createRepo`

**用途：** createrepo。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5584`（`views.create_repository`）
**源码说明：** create_repository API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `alias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `level` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `note` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/createRepo" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Name\": \"example\", \"alias\": \"example\", \"level\": \"example\", \"note\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/createRepo"
response = session.post(url, json={"Name": "example", "alias": "example", "level": "example", "note": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 162. `GET /WebDatabase/getrepos`

**用途：** getrepos。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5627`（`views.get_repositories`）
**源码说明：** get_repositories API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getrepos" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getrepos"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 163. `POST /WebDatabase/getrepo`

**用途：** getrepo。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5655`（`views.get_repository`）
**源码说明：** get_repository API view. Args: request: Django HttpRequest object. Returns: JsonResponse | Any: View response or computed result.
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 410。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/getrepo" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Name\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getrepo"
response = session.post(url, json={"Name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 164. `POST /WebDatabase/addparts`

**用途：** addparts。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5689`（`views.add_part_to_repository`）
**源码说明：** 添加part到仓库
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400, 404, 410。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `RepoName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `part_end_scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `part_ids` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `part_start_scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/addparts" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"RepoName\": \"example\", \"part_end_scar\": \"example\", \"part_ids\": \"example\", \"part_start_scar\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/addparts"
response = session.post(url, json={"RepoName": "example", "part_end_scar": "example", "part_ids": "example", "part_start_scar": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 165. `POST /WebDatabase/addbackbones`

**用途：** addbackbones。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5809`（`views.add_backbone_to_repository`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400, 401, 404, 405, 410, 500。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `RepoName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `backbone_ids` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/addbackbones" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"RepoName\": \"example\", \"backbone_ids\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/addbackbones"
response = session.post(url, json={"RepoName": "example", "backbone_ids": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 166. `POST /WebDatabase/addplasmids`

**用途：** addplasmids。接口类型：JSON API。

**源码：** `WebDatabase/views.py:5914`（`views.add_plasmid_to_repository`）
**源码说明：** 灏嗗厓浠禝D娣诲姞鍒扮敤鎴风殑涓存椂浠撳簱涓? 鏀寔鍗曚釜鍏冧欢ID鎴栧厓浠禝D鍒楄〃
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400, 401, 404, 405, 410。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `RepoName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmid_ids` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/addplasmids" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"RepoName\": \"example\", \"plasmid_ids\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/addplasmids"
response = session.post(url, json={"RepoName": "example", "plasmid_ids": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 167. `POST /WebDatabase/removeparts`

**用途：** removeparts。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6024`（`views.remove_part_from_repository`）
**源码说明：** 浠庣敤鎴风殑涓存椂浠撳簱涓Щ闄ゅ厓浠禝D
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400, 404, 410, 500。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `RepoName` | form | string | 由视图逻辑决定 |
| `part_ids` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/removeparts" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"part_ids\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/removeparts"
response = session.post(url, json={"part_ids": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 168. `GET /WebDatabase/getparts`

**用途：** getparts。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6105`（`views.get_repository_parts`）
**源码说明：** 鑾峰彇鐢ㄦ埛涓存椂浠撳簱涓殑鎵€鏈夊厓浠禝D
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 401, 405, 500。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getparts" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getparts"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 169. `POST /WebDatabase/createVisitorProfile`

**用途：** create Visitor Profile。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6221`（`views.createVisitorProfile`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `cookie_key` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `created_by_user_id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `institution` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `lab_name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `person_name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/createVisitorProfile" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"cookie_key\": \"example\", \"created_by_user_id\": \"example\", \"institution\": \"example\", \"lab_name\": \"example\", \"person_name\": \"example\", \"visitor_uuid\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/createVisitorProfile"
response = session.post(url, json={"cookie_key": "example", "created_by_user_id": "example", "institution": "example", "lab_name": "example", "person_name": "example", "visitor_uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 170. `GET /WebDatabase/getVisitorProfile`

**用途：** get Visitor Profile。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6263`（`views.getVisitorProfile`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `cookie_key` | query | string | 由视图逻辑决定 |
| `id` | query | string | 由视图逻辑决定 |
| `visitor_uuid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getVisitorProfile?cookie_key=example&id=example&visitor_uuid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getVisitorProfile"
response = session.get(url, params={"cookie_key": "example", "id": "example", "visitor_uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 171. `GET /WebDatabase/listVisitorProfiles`

**用途：** list Visitor Profiles。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6289`（`views.listVisitorProfiles`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `created_by_user_id` | query | string | 由视图逻辑决定 |
| `institution` | query | string | 由视图逻辑决定 |
| `keyword` | query | string | 由视图逻辑决定 |
| `lab_name` | query | string | 由视图逻辑决定 |
| `person_name` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/listVisitorProfiles?created_by_user_id=example&institution=example&keyword=example&lab_name=example&person_name=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/listVisitorProfiles"
response = session.get(url, params={"created_by_user_id": "example", "institution": "example", "keyword": "example", "lab_name": "example", "person_name": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 172. `POST /WebDatabase/updateVisitorProfile`

**用途：** update Visitor Profile。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6320`（`views.updateVisitorProfile`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `last_seen_at` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/updateVisitorProfile" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"id\": \"example\", \"last_seen_at\": \"example\", \"visitor_uuid\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/updateVisitorProfile"
response = session.post(url, json={"id": "example", "last_seen_at": "example", "visitor_uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 173. `POST /WebDatabase/deleteVisitorProfile`

**用途：** delete Visitor Profile。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6361`（`views.deleteVisitorProfile`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/deleteVisitorProfile" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"id\": \"example\", \"visitor_uuid\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deleteVisitorProfile"
response = session.post(url, json={"id": "example", "visitor_uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 174. `POST /WebDatabase/createVisitorFeedback`

**用途：** create Visitor Feedback。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6449`（`views.createVisitorFeedback`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 201, 400, 404, 405, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `contact_email` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `content` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `feedback_type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page_path` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `status` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `title` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/createVisitorFeedback" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"contact_email\": \"example\", \"content\": \"example\", \"feedback_type\": \"example\", \"page_path\": \"example\", \"status\": \"example\", \"title\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/createVisitorFeedback"
response = session.post(url, json={"contact_email": "example", "content": "example", "feedback_type": "example", "page_path": "example", "status": "example", "title": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 175. `POST /WebDatabase/createVisitorAccessLog`

**用途：** create Visitor Access Log。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6388`（`views.createVisitorAccessLog`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `cookie_snapshot` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ip` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `method` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `path` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `referer` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `user_agent` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/createVisitorAccessLog" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"cookie_snapshot\": \"example\", \"ip\": \"example\", \"method\": \"example\", \"path\": \"example\", \"referer\": \"example\", \"user_agent\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/createVisitorAccessLog"
response = session.post(url, json={"cookie_snapshot": "example", "ip": "example", "method": "example", "path": "example", "referer": "example", "user_agent": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 176. `GET /WebDatabase/getVisitorAccessLog`

**用途：** get Visitor Access Log。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6505`（`views.getVisitorAccessLog`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/getVisitorAccessLog?id=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/getVisitorAccessLog"
response = session.get(url, params={"id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 177. `GET /WebDatabase/listVisitorAccessLogs`

**用途：** list Visitor Access Logs。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6522`（`views.listVisitorAccessLogs`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `method` | query | string | 由视图逻辑决定 |
| `path` | query | string | 由视图逻辑决定 |
| `visitor_id` | query | string | 由视图逻辑决定 |
| `visitor_uuid` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/WebDatabase/listVisitorAccessLogs?method=example&path=example&visitor_id=example&visitor_uuid=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/listVisitorAccessLogs"
response = session.get(url, params={"method": "example", "path": "example", "visitor_id": "example", "visitor_uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 178. `POST /WebDatabase/updateVisitorAccessLog`

**用途：** update Visitor Access Log。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6549`（`views.updateVisitorAccessLog`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `visitor_id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/updateVisitorAccessLog" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"id\": \"example\", \"visitor_id\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/updateVisitorAccessLog"
response = session.post(url, json={"id": "example", "visitor_id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 179. `POST /WebDatabase/deleteVisitorAccessLog`

**用途：** delete Visitor Access Log。接口类型：JSON API。

**源码：** `WebDatabase/views.py:6577`（`views.deleteVisitorAccessLog`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 404, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `id` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/WebDatabase/deleteVisitorAccessLog" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"id\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/WebDatabase/deleteVisitorAccessLog"
response = session.post(url, json={"id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

## 文档边界与维护

- 路由总数：179。
- 参数名称来自 `request.GET`、`request.POST`、`request.FILES` 和常见 JSON payload 的静态提取。
- 动态生成的字段、模型序列化结构和异常分支可能无法通过静态分析完整恢复；相应位置明确标记为“未从源码静态确定”。
- 修改 URL 或视图后，运行 `python scripts/generate_source_api_docs.py` 重新生成。
