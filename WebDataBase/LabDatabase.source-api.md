# LabDatabase 源码校验 API 文档

> 本文档由 Django URL 配置与对应视图源码生成并人工约束：只记录仓库中可验证的行为。
> 请求/响应示例为源码推导示例，并非线上抓包结果；部署域名、权限策略和实际数据以运行环境为准。

## 快速开始

- 基础路径：`{BASE_URL}/LabDatabase/`
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
| 1 | `GET` | `/LabDatabase/index` | 页面/跳转 | `views.index` |
| 2 | `GET` | `/LabDatabase/design-builder` | 页面/跳转 | `views.design_builder` |
| 3 | `GET` | `/LabDatabase/design-builder/gene-search` | JSON API | `views.design_gene_search` |
| 4 | `POST` | `/LabDatabase/design-builder/submit` | JSON API | `views.submit_design_assembly` |
| 5 | `GET` | `/LabDatabase/getdata` | JSON API | `views.getData` |
| 6 | `POST` | `/LabDatabase/filterdata` | JSON API | `views.DataFilter` |
| 7 | `GET/POST` | `/LabDatabase/login` | 页面/跳转 | `admin.login` |
| 8 | `GET/POST` | `/LabDatabase/logout` | 页面/跳转 | `admin.logout` |
| 9 | `GET/POST` | `/LabDatabase/register` | 页面/跳转 | `admin.register` |
| 10 | `GET/POST` | `/LabDatabase/AdminRegister` | 页面/跳转 | `admin.register_admin` |
| 11 | `POST` | `/LabDatabase/UploadMap` | JSON API | `views.UploadMap` |
| 12 | `POST` | `/LabDatabase/CheckAndFixGenBank` | JSON API | `views.CheckAndFixGenBank` |
| 13 | `GET, POST` | `/LabDatabase/CustomScar` | JSON API | `views.CustomScar` |
| 14 | `POST` | `/LabDatabase/UploadFile` | JSON API | `views.UploadFile` |
| 15 | `GET/POST` | `/LabDatabase/task_status/<str:task_id>` | JSON API | `views.task_status` |
| 16 | `GET/POST` | `/LabDatabase/excel_task_status/<str:task_id>` | JSON API | `views.excel_task_status` |
| 17 | `GET` | `/LabDatabase/part/<int:partid>` | 页面/跳转 | `views.part_detail_show` |
| 18 | `GET` | `/LabDatabase/backbone/<int:backboneid>` | 页面/跳转 | `views.backbone_detail_show` |
| 19 | `GET` | `/LabDatabase/plasmid/<int:plasmidid>` | 页面/跳转 | `views.plasmid_detail_show` |
| 20 | `POST` | `/LabDatabase/deletepart` | JSON API | `views.delete_part` |
| 21 | `POST` | `/LabDatabase/deletebackbone` | JSON API | `views.delete_backbone` |
| 22 | `POST` | `/LabDatabase/deleteplasmid` | JSON API | `views.delete_plasmid` |
| 23 | `POST` | `/LabDatabase/modifypart/<int:partid>` | 页面/跳转 | `views.modify_part` |
| 24 | `POST` | `/LabDatabase/modifybackbone/<int:backboneid>` | 页面/跳转 | `views.modify_backbone` |
| 25 | `POST` | `/LabDatabase/modifyplasmid/<int:plasmidid>` | 页面/跳转 | `views.modify_plasmid` |
| 26 | `GET/POST` | `/LabDatabase/download/<str:type>` | 文件下载 | `views.download_template` |
| 27 | `GET` | `/LabDatabase/downloadPlasmidMap/<int:plasmidid>` | 文件下载 | `views.downloadPlasmidMap` |
| 28 | `GET` | `/LabDatabase/downloadBackboneMap/<int:backboneid>` | 文件下载 | `views.downloadBackboneMap` |
| 29 | `GET` | `/LabDatabase/downloadPartMap/<int:partid>` | 文件下载 | `views.downloadPartMap` |
| 30 | `GET/POST` | `/LabDatabase/adminPage` | 页面/跳转 | `admin_views.AdminDashbordView` |
| 31 | `GET` | `/LabDatabase/exportUserData/<str:username>` | JSON API | `views.exportuserdata` |
| 32 | `GET` | `/LabDatabase/exportallData` | JSON API | `views.ExportAllData` |
| 33 | `GET` | `/LabDatabase/getDocument/<str:fileid>` | 文件下载 | `views.getDocument` |
| 34 | `GET` | `/LabDatabase/getDocByAdd` | 文件下载 | `views.getDocumentByAddress` |
| 35 | `GET` | `/LabDatabase/getAssembly/<str:fileName>` | 文件下载 | `views.getAssemblyFile` |
| 36 | `GET` | `/LabDatabase/getAssemblyArchive/<str:task_id>` | 文件下载 | `views.getAssemblyArchive` |
| 37 | `POST` | `/LabDatabase/createRepo` | JSON API | `views.CreateTempRepository` |
| 38 | `POST` | `/LabDatabase/AssemblyRepo` | JSON API | `views.AssemblyRepo` |
| 39 | `POST` | `/LabDatabase/AssemblyWithoutRepo` | JSON API | `views.AssemblyWithoutRepo` |
| 40 | `GET/POST` | `/LabDatabase/FetchExperienceDetail/<str:partName>` | 页面/跳转 | `views.GetExperienceDetail` |
| 41 | `GET` | `/LabDatabase/api/upload/view` | JSON API | `views.view_upload_records` |
| 42 | `GET` | `/LabDatabase/user/<str:username>` | 页面/跳转 | `views.user` |
| 43 | `GET` | `/LabDatabase/GetParent` | JSON API | `views.GetParentInfo` |
| 44 | `GET/POST` | `/LabDatabase/RepositoryDiagram/<str:repositoryName>` | HTTP 接口 | `DNADiagram.generate_plasmid_view` |
| 45 | `GET` | `/LabDatabase/ShowRepository/<str:repositoryName>` | 页面/跳转 | `views.showRepository` |

## 端点详情

### 1. `GET /LabDatabase/index`

**用途：** index。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:447`（`views.index`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`, `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/index" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/index"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 2. `GET /LabDatabase/design-builder`

**用途：** design builder。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:553`（`views.design_builder`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/design-builder" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/design-builder"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 3. `GET /LabDatabase/design-builder/gene-search`

**用途：** design gene search。接口类型：JSON API。

**源码：** `LabDatabase/views.py:562`（`views.design_gene_search`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `q` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/design-builder/gene-search?q=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/design-builder/gene-search"
response = session.get(url, params={"q": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 4. `POST /LabDatabase/design-builder/submit`

**用途：** submit design assembly。接口类型：JSON API。

**源码：** `LabDatabase/views.py:572`（`views.submit_design_assembly`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 500。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/design-builder/submit" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/design-builder/submit"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 5. `GET /LabDatabase/getdata`

**用途：** get Data。接口类型：JSON API。

**源码：** `LabDatabase/views.py:620`（`views.getData`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `page` | query | string | 由视图逻辑决定 |
| `type` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/getdata?page=example&type=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/getdata"
response = session.get(url, params={"page": "example", "type": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 6. `POST /LabDatabase/filterdata`

**用途：** filterdata。接口类型：JSON API。

**源码：** `LabDatabase/views.py:684`（`views.DataFilter`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `Enzyme` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Scar` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `SearchType` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `Type` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `page_size` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/filterdata" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"Enzyme\": \"example\", \"Marker\": \"example\", \"Ori\": \"example\", \"Scar\": \"example\", \"SearchType\": \"example\", \"Type\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/filterdata"
response = session.post(url, json={"Enzyme": "example", "Marker": "example", "Ori": "example", "Scar": "example", "SearchType": "example", "Type": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 7. `GET/POST /LabDatabase/login`

**用途：** login。接口类型：页面/跳转。

**源码：** `LabDatabase/admin.py:4`（`admin.login`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/login" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/login"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 8. `GET/POST /LabDatabase/logout`

**用途：** logout。接口类型：页面/跳转。

**源码：** `LabDatabase/admin.py:8`（`admin.logout`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/logout" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/logout"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 9. `GET/POST /LabDatabase/register`

**用途：** register。接口类型：页面/跳转。

**源码：** `LabDatabase/admin.py:11`（`admin.register`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/register" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/register"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 10. `GET/POST /LabDatabase/AdminRegister`

**用途：** Admin Register。接口类型：页面/跳转。

**源码：** `LabDatabase/admin.py:14`（`admin.register_admin`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/AdminRegister" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/AdminRegister"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 11. `POST /LabDatabase/UploadMap`

**用途：** Upload Map。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1451`（`views.UploadMap`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `save_feature` | form | string | 由视图逻辑决定 |
| `type` | form | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/UploadMap" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data-urlencode "save_feature=example" \
  --data-urlencode "type=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/UploadMap"
response = session.post(url, data={"save_feature": "example", "type": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 12. `POST /LabDatabase/CheckAndFixGenBank`

**用途：** Check And Fix Gen Bank。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1500`（`views.CheckAndFixGenBank`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 405。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `file` | multipart file | binary | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/CheckAndFixGenBank" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -F "file=@./example.dat" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/CheckAndFixGenBank"
with open("example.dat", "rb") as upload:
    response = session.post(url, files={"file": upload}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 13. `GET, POST /LabDatabase/CustomScar`

**用途：** Custom Scar。接口类型：JSON API。

**源码：** `LabDatabase/views.py:492`（`views.CustomScar`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400, 409。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `description` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `scar_description` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `scar_name` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `scar_sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/CustomScar" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/CustomScar"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 14. `POST /LabDatabase/UploadFile`

**用途：** Upload File。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1323`（`views.UploadFile`）
**函数级安全标记：** `csrf_exempt`。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `title` | form | string | 由视图逻辑决定 |
| `file` | multipart file | binary | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/UploadFile" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -F "title=example" \
  -F "file=@./example.dat" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/UploadFile"
with open("example.dat", "rb") as upload:
    response = session.post(url, files={"file": upload}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 15. `GET/POST /LabDatabase/task_status/<str:task_id>`

**用途：** task status。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1368`（`views.task_status`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `task_id` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/task_status/example-task_id" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/task_status/example-task_id"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 16. `GET/POST /LabDatabase/excel_task_status/<str:task_id>`

**用途：** excel task status。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1417`（`views.excel_task_status`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400, 404。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `task_id` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/excel_task_status/example-task_id" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/excel_task_status/example-task_id"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 17. `GET /LabDatabase/part/<int:partid>`

**用途：** part detail。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:1544`（`views.part_detail_show`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/part/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/part/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 18. `GET /LabDatabase/backbone/<int:backboneid>`

**用途：** backbone detail。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:1580`（`views.backbone_detail_show`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backboneid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/backbone/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/backbone/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 19. `GET /LabDatabase/plasmid/<int:plasmidid>`

**用途：** plasmid detail。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:1613`（`views.plasmid_detail_show`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/plasmid/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/plasmid/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 20. `POST /LabDatabase/deletepart`

**用途：** delete part。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2029`（`views.delete_part`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/deletepart" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/deletepart"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 21. `POST /LabDatabase/deletebackbone`

**用途：** delete backbone。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2054`（`views.delete_backbone`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/deletebackbone" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/deletebackbone"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 22. `POST /LabDatabase/deleteplasmid`

**用途：** delete plasmid。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2084`（`views.delete_plasmid`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/deleteplasmid" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/deleteplasmid"
response = session.post(url, data={}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 23. `POST /LabDatabase/modifypart/<int:partid>`

**用途：** modify part。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3533`（`views.modify_part`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `render`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partid` | path | int | 必需 |
| `elementType` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `geneAlias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `geneName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `notes` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `references` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `speciesSource` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/modifypart/1" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"elementType\": \"example\", \"geneAlias\": \"example\", \"geneName\": \"example\", \"notes\": \"example\", \"references\": \"example\", \"sequence\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/modifypart/1"
response = session.post(url, json={"elementType": "example", "geneAlias": "example", "geneName": "example", "notes": "example", "references": "example", "sequence": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 24. `POST /LabDatabase/modifybackbone/<int:backboneid>`

**用途：** modify backbone。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3576`（`views.modify_backbone`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `render`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backboneid` | path | int | 必需 |
| `copyNumber` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `host` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `notes` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `scarSites` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `vectorAlias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `vectorId` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `vectorName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/modifybackbone/1" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"copyNumber\": \"example\", \"host\": \"example\", \"marker\": \"example\", \"notes\": \"example\", \"ori\": \"example\", \"scarSites\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/modifybackbone/1"
response = session.post(url, json={"copyNumber": "example", "host": "example", "marker": "example", "notes": "example", "ori": "example", "scarSites": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 25. `POST /LabDatabase/modifyplasmid/<int:plasmidid>`

**用途：** modify plasmid。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3620`（`views.modify_plasmid`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `render`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | path | int | 必需 |
| `level` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `marker` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `notes` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `ori` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `parentBackbone` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `parentPart` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `parentPlasmid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmidAlias` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmidId` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmidName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `scarSites` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `sequence` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/modifyplasmid/1" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"level\": \"example\", \"marker\": \"example\", \"notes\": \"example\", \"ori\": \"example\", \"parentBackbone\": \"example\", \"parentPart\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/modifyplasmid/1"
response = session.post(url, json={"level": "example", "marker": "example", "notes": "example", "ori": "example", "parentBackbone": "example", "parentPart": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 26. `GET/POST /LabDatabase/download/<str:type>`

**用途：** downloadtemplate。接口类型：文件下载。

**源码：** `LabDatabase/views.py:821`（`views.download_template`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `type` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/download/example-type" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/download/example-type"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 27. `GET /LabDatabase/downloadPlasmidMap/<int:plasmidid>`

**用途：** download Plasmid Map。接口类型：文件下载。

**源码：** `LabDatabase/views.py:1812`（`views.downloadPlasmidMap`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `plasmidid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/downloadPlasmidMap/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/downloadPlasmidMap/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 28. `GET /LabDatabase/downloadBackboneMap/<int:backboneid>`

**用途：** download Backbone Map。接口类型：文件下载。

**源码：** `LabDatabase/views.py:1750`（`views.downloadBackboneMap`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backboneid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/downloadBackboneMap/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/downloadBackboneMap/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 29. `GET /LabDatabase/downloadPartMap/<int:partid>`

**用途：** download Part Map。接口类型：文件下载。

**源码：** `LabDatabase/views.py:1679`（`views.downloadPartMap`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partid` | path | int | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/downloadPartMap/1" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/downloadPartMap/1"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 30. `GET/POST /LabDatabase/adminPage`

**用途：** admin Page。接口类型：页面/跳转。

**源码：** `LabDatabase/AdminManage/admin_views.py:14`（`admin_views.AdminDashbordView`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `render`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/adminPage" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/adminPage"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 31. `GET /LabDatabase/exportUserData/<str:username>`

**用途：** exportuserdata。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2107`（`views.exportuserdata`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `username` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/exportUserData/example-username" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/exportUserData/example-username"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 32. `GET /LabDatabase/exportallData`

**用途：** exportall Data。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2232`（`views.ExportAllData`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| — | — | — | 无显式输入参数 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/exportallData" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/exportallData"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 33. `GET /LabDatabase/getDocument/<str:fileid>`

**用途：** get Document。接口类型：文件下载。

**源码：** `LabDatabase/views.py:2365`（`views.getDocument`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `fileid` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/getDocument/example-fileid" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/getDocument/example-fileid"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 34. `GET /LabDatabase/getDocByAdd`

**用途：** get Doc By Add。接口类型：文件下载。

**源码：** `LabDatabase/views.py:2382`（`views.getDocumentByAddress`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `address` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/getDocByAdd?address=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/getDocByAdd"
response = session.get(url, params={"address": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 35. `GET /LabDatabase/getAssembly/<str:fileName>`

**用途：** get Assembly。接口类型：文件下载。

**源码：** `LabDatabase/views.py:2400`（`views.getAssemblyFile`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `fileName` | path | str | 必需 |
| `task_id` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/getAssembly/example-fileName?task_id=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/getAssembly/example-fileName"
response = session.get(url, params={"task_id": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 36. `GET /LabDatabase/getAssemblyArchive/<str:task_id>`

**用途：** get Assembly Archive。接口类型：文件下载。

**源码：** `LabDatabase/views.py:2424`（`views.getAssemblyArchive`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `FileResponse`, `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `task_id` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/getAssemblyArchive/example-task_id" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/getAssemblyArchive/example-task_id"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 37. `POST /LabDatabase/createRepo`

**用途：** create Repo。接口类型：JSON API。

**源码：** `LabDatabase/views.py:1287`（`views.CreateTempRepository`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `file` | multipart file | binary | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/createRepo" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -F "file=@./example.dat" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/createRepo"
with open("example.dat", "rb") as upload:
    response = session.post(url, files={"file": upload}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 38. `POST /LabDatabase/AssemblyRepo`

**用途：** Assembly Repo。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2679`（`views.AssemblyRepo`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `repositoryName` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/AssemblyRepo" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"repositoryName\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/AssemblyRepo"
response = session.post(url, json={"repositoryName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 39. `POST /LabDatabase/AssemblyWithoutRepo`

**用途：** Assembly Without Repo。接口类型：JSON API。

**源码：** `LabDatabase/views.py:2897`（`views.AssemblyWithoutRepo`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `backbone` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `part` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `plasmid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |
| `uuid` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X POST "$BASE_URL/LabDatabase/AssemblyWithoutRepo" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{\"backbone\": \"example\", \"part\": \"example\", \"plasmid\": \"example\", \"uuid\": \"example\"}" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/AssemblyWithoutRepo"
response = session.post(url, json={"backbone": "example", "part": "example", "plasmid": "example", "uuid": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 40. `GET/POST /LabDatabase/FetchExperienceDetail/<str:partName>`

**用途：** Fetch Experience Detail。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3719`（`views.GetExperienceDetail`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `redirect`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `partName` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/FetchExperienceDetail/example-partName" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/FetchExperienceDetail/example-partName"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 41. `GET /LabDatabase/api/upload/view`

**用途：** view upload records。接口类型：JSON API。

**源码：** `LabDatabase/views.py:3737`（`views.view_upload_records`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `filter` | query | string | 由视图逻辑决定 |
| `page` | query | string | 由视图逻辑决定 |
| `pagesize` | query | string | 由视图逻辑决定 |
| `table` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/api/upload/view?filter=example&page=example&pagesize=example&table=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/api/upload/view"
response = session.get(url, params={"filter": "example", "page": "example", "pagesize": "example", "table": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 42. `GET /LabDatabase/user/<str:username>`

**用途：** user。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3774`（`views.user`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `render`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `username` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/user/example-username" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/user/example-username"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 43. `GET /LabDatabase/GetParent`

**用途：** Get Parent。接口类型：JSON API。

**源码：** `LabDatabase/views.py:3802`（`views.GetParentInfo`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`。
**显式状态码：** 200, 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `PlasmidName` | query | string | 由视图逻辑决定 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/GetParent?PlasmidName=example" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/GetParent"
response = session.get(url, params={"PlasmidName": "example"}, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 44. `GET/POST /LabDatabase/RepositoryDiagram/<str:repositoryName>`

**用途：** Repository Diagram。接口类型：HTTP 接口。

**源码：** `LabDatabase/CaculateModule/DNADiagram.py:733`（`DNADiagram.generate_plasmid_view`）
**源码说明：** 生成质粒图谱的视图
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `HttpResponse`。
**显式状态码：** 源码未显式指定。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `repositoryName` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/RepositoryDiagram/example-repositoryName" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/RepositoryDiagram/example-repositoryName"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

### 45. `GET /LabDatabase/ShowRepository/<str:repositoryName>`

**用途：** Show Repository。接口类型：页面/跳转。

**源码：** `LabDatabase/views.py:3860`（`views.showRepository`）
**函数级安全标记：** 无函数级认证/CSRF 装饰器。仍需遵循项目 Session 与 CSRF 约定。
**响应形式：** `JsonResponse`, `render`。
**显式状态码：** 400。

| 名称 | 位置 | 类型 | 必需性 |
|---|---|---|---|
| `repositoryName` | path | str | 必需 |

**cURL 示例**

```bash
curl -i -X GET "$BASE_URL/LabDatabase/ShowRepository/example-repositoryName" \
  -b "sessionid=$SESSION_ID"
```

**Python 示例**

```python
base_url = "http://10.30.76.2:8080"
import requests

session = requests.Session()
url = base_url + "/LabDatabase/ShowRepository/example-repositoryName"
response = session.get(url, timeout=30)
response.raise_for_status()
print(response.text)
```

**响应校验建议**

- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。
- 页面接口：允许 3xx，并检查最终页面或 `Location`。
- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。
- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。

## 文档边界与维护

- 路由总数：45。
- 参数名称来自 `request.GET`、`request.POST`、`request.FILES` 和常见 JSON payload 的静态提取。
- 动态生成的字段、模型序列化结构和异常分支可能无法通过静态分析完整恢复；相应位置明确标记为“未从源码静态确定”。
- 修改 URL 或视图后，运行 `python scripts/generate_source_api_docs.py` 重新生成。
