# LabDatabase API 文档

## 基本信息

- Base URL: `http://10.30.76.2:8080/LabDatabase`
- Django 路由源：`LabDatabase/urls.py`
- 版本：1.1.0
- 认证：大多数页面和数据操作依赖当前登录会话；写操作通常还需要 `csrftoken` Cookie 和 `X-CSRFToken` 请求头。
- 路径参数使用 Django 声明形式，例如 `<int:partid>`；实际请求时应替换为具体值。

## 通用约定

- JSON 响应通常包含 `success`、`message`、`data` 等字段；异步任务响应包含 `task_id`、`status` 和 `progress`。
- 错误通常以 `400` 返回；请求方法不正确时通常返回 `405`；任务或文件不存在时可能返回 `404`。
- 本文记录 `LabDatabase/urls.py` 中所有有效路由。页面接口返回 HTML，文件接口返回下载流或重定向，其余接口返回 JSON。

## 1. 页面与设计工具

### `GET /index`

返回 LabDatabase 首页 HTML。未登录用户会被重定向至 `/WebDatabase/login`。

### `GET /design-builder`

返回基础设计工具页面 HTML。

### `GET /design-builder/gene-search`

按名称搜索设计候选基因。

| 参数 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- |
| `q` | query | 否 | 搜索词，默认为空字符串 |

成功响应：`{"success": true, "data": [...]}`。

### `POST /design-builder/submit`

提交设计参数，推荐元件与骨架，创建仓库并启动异步组装。请求体为 `application/json`，字段由设计页面生成并传给设计引擎。

成功响应包含 `success`、`task_id`、`repository_name`、`selected_parts`、`selected_backbone`、`strengths` 和 `message`。使用 `/task_status/<task_id>` 查询进度。

### `GET /adminPage`

返回管理员仪表盘 HTML。

### `GET /user/<str:username>`

返回当前登录用户的个人页 HTML。实现使用会话中的当前用户信息，路径中的 `username` 不用于切换用户。

## 2. 数据查询

### `GET /getdata`

分页读取指定类型的数据。

| 参数 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- |
| `type` | query | 是 | `part`、`backbone` 或 `plasmid` |
| `page` | query | 否 | 页码，默认 `1` |

### `POST /filterdata`

按筛选条件查询 Part、Backbone 或 Plasmid。请求体为 `application/json`，包含数据类型及对应筛选字段；成功响应返回匹配数据和分页信息。

### `GET /part/<int:partid>`

返回指定 Part 的详情页 HTML。

### `GET /backbone/<int:backboneid>`

返回指定 Backbone 的详情页 HTML。

### `GET /plasmid/<int:plasmidid>`

返回指定 Plasmid 的详情页 HTML，并加载其 Part、Backbone、Plasmid 上级关系及下级关系。

### `GET /FetchExperienceDetail/<str:partName>`

按 Part 名称查询实验经验系统中的记录，并重定向至对应的经验详情页。

### `GET /api/upload/view`

查询按上传日期分表保存的原始记录。

| 参数 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- |
| `table` | query | 是 | `parttable`、`backbonetable` 或 `plasmidneed` |
| `filter` | query | 否 | 下游数据库支持的筛选表达式 |
| `page` | query | 否 | 页码，默认 `1` |
| `pagesize` | query | 否 | 每页数量，默认 `100`，最大 `5000` |

### `GET /GetParent`

查询 Plasmid 的上级 Part、Backbone 和 Plasmid 信息。

| 参数 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- |
| `PlasmidName` | query | 是 | Plasmid 名称 |

成功响应包含 `parentPart`、`parentBackbone`、`parentPlasmid` 和 `parentInfo`。

## 3. 登录与注册

以下路由由 `LabDatabase/admin.py` 转发给 WebDatabase 的认证控制器，接受的表单字段及返回格式与对应 WebDatabase 认证接口一致。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET/POST` | `/login` | 显示登录页或提交登录 |
| `GET/POST` | `/logout` | 退出登录 |
| `GET/POST` | `/register` | 显示或提交普通用户注册 |
| `GET/POST` | `/AdminRegister` | 显示或提交管理员注册 |

## 4. 上传、校验与异步任务

### `GET /CustomScar`

获取全部自定义 Scar 记录。成功响应：`{"success": true, "data": [...]}`。

### `POST /CustomScar`

创建自定义 Scar。支持 `application/json` 或表单请求。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `scar_name` / `name` | 是 | Scar 名称，忽略大小写判重 |
| `scar_sequence` / `sequence` | 是 | IUPAC 碱基序列 |
| `scar_description` / `description` | 否 | 描述 |

重名返回 `409`；字段为空或序列包含非法字符返回 `400`。

### `POST /UploadMap`

批量上传序列图谱，`Content-Type` 为 `multipart/form-data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `files` | 是 | 一个或多个图谱文件 |
| `type` | 是 | 上传的数据类型 |
| `save_feature` | 否 | 是否保存识别出的 feature；接受 `true/1/yes/on`，默认 `false` |

成功响应包含 `task_id`，使用 `/task_status/<task_id>` 查询处理进度。

### `POST /CheckAndFixGenBank`

校验并修复 GenBank 文件，`Content-Type` 为 `multipart/form-data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `file` | 是 | 待校验的 GenBank 文件 |

成功响应包含 `changed`、`issue_count`、`issues`、`fixed_filename`、`fixed_content` 和 `file_path`。

### `POST /UploadFile`

上传并异步处理 Excel 数据文件，`Content-Type` 为 `multipart/form-data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `file` | 是 | Excel 文件 |
| `title` | 否 | 文件标题，默认使用上传文件名 |

成功响应包含 `task_id`；使用 `/excel_task_status/<task_id>` 查询进度。

### `GET /task_status/<str:task_id>`

查询图谱上传、仓库创建或组装任务状态。响应包含 `task_id`、`status`、`progress`、`success`、`message`，有结果时还包含 `result`，失败时包含 `error`。

### `GET /excel_task_status/<str:task_id>`

查询 Excel 处理或导出任务状态。完成时返回 `{"status": "completed", "file_id": "..."}`；未完成时返回 `{"success": true}`。

## 5. 删除与修改

### 删除接口

请求体均为 `application/json`。

| 方法 | 路径 | 请求字段 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/deletepart` | `partid` | 删除 Part |
| `POST` | `/deletebackbone` | `backboneid` | 删除 Backbone |
| `POST` | `/deleteplasmid` | `Plasmidid` | 删除 Plasmid（字段大小写与实现一致） |

### `GET /modifypart/<int:partid>`

返回 Part 编辑页 HTML。

### `POST /modifypart/<int:partid>`

更新 Part。JSON 字段：`elementType`、`geneName`、`geneAlias`、`sequence`、`speciesSource`、`references`、`notes`。

### `GET /modifybackbone/<int:backboneid>`

返回 Backbone 编辑页 HTML。

### `POST /modifybackbone/<int:backboneid>`

更新 Backbone。JSON 字段：`vectorId`、`vectorName`、`vectorAlias`、`sequence`、`host`、`copyNumber`、`notes`、`ori`、`marker`、`scarSites`。`scarSites` 包含 `BsmBI`、`BsaI`、`BbsI`、`Aari`、`Sapi`。

### `GET /modifyplasmid/<int:plasmidid>`

返回 Plasmid 编辑页 HTML。

### `POST /modifyplasmid/<int:plasmidid>`

更新 Plasmid 及亲本关系。JSON 字段：`plasmidId`、`plasmidName`、`plasmidAlias`、`level`、`sequence`、`ori`、`marker`、`notes`、`scarSites`、`parentPart`、`parentBackbone`、`parentPlasmid`。

## 6. 下载与导出

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/download/<str:type>` | 下载模板；`type` 对应 Part、Backbone、Plasmid 或 Assembly 模板类型 |
| `GET` | `/downloadPartMap/<int:partid>` | 下载指定 Part 的图谱文件 |
| `GET` | `/downloadBackboneMap/<int:backboneid>` | 下载指定 Backbone 的图谱文件 |
| `GET` | `/downloadPlasmidMap/<int:plasmidid>` | 下载指定 Plasmid 的图谱文件 |
| `GET` | `/exportUserData/<str:username>` | 启动指定用户的数据导出，返回 `task_id` |
| `GET` | `/exportallData` | 启动全部数据导出，返回 `task_id` |
| `GET` | `/getDocument/<str:fileid>` | 下载异步任务生成的文档 |
| `GET` | `/getAssembly/<str:fileName>` | 下载组装文件；可附加 query 参数 `task_id` 指定任务 |
| `GET` | `/getAssemblyArchive/<str:task_id>` | 下载组装任务生成的归档文件 |

### `GET /getDocByAdd`

按服务器文件地址下载文档。

| 参数 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- |
| `address` | query | 是 | 文档地址 |

## 7. 仓库与组装

### `POST /createRepo`

上传组装方案文件并异步创建临时仓库，`Content-Type` 为 `multipart/form-data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `file` | 是 | 组装方案文件 |

成功响应包含 `task_id`，使用 `/task_status/<task_id>` 查询进度。

### `POST /AssemblyRepo`

对已有仓库启动异步组装。请求体为 `application/json`，包含仓库名称及页面提供的组装配置；成功响应包含 `task_id`。

### `POST /AssemblyWithoutRepo`

不创建仓库直接提交组装任务。请求体为 `application/json`，包含待组装元件、骨架及组装配置；成功响应包含任务或组装结果信息。

### `GET /RepositoryDiagram/<str:repositoryName>`

生成指定仓库的质粒示意图，返回图片或文件响应；仓库不存在或无法生成时返回失败响应。

### `GET /ShowRepository/<str:repositoryName>`

返回指定仓库的详情页 HTML。

## 路由覆盖清单

本文共记录 `LabDatabase/urls.py` 中的 45 个有效路由：

```text
index
design-builder
design-builder/gene-search
design-builder/submit
getdata
filterdata
login
logout
register
AdminRegister
UploadMap
CheckAndFixGenBank
CustomScar
UploadFile
task_status/<str:task_id>
excel_task_status/<str:task_id>
part/<int:partid>
backbone/<int:backboneid>
plasmid/<int:plasmidid>
deletepart
deletebackbone
deleteplasmid
modifypart/<int:partid>
modifybackbone/<int:backboneid>
modifyplasmid/<int:plasmidid>
download/<str:type>
downloadPlasmidMap/<int:plasmidid>
downloadBackboneMap/<int:backboneid>
downloadPartMap/<int:partid>
adminPage
exportUserData/<str:username>
exportallData
getDocument/<str:fileid>
getDocByAdd
getAssembly/<str:fileName>
getAssemblyArchive/<str:task_id>
createRepo
AssemblyRepo
AssemblyWithoutRepo
FetchExperienceDetail/<str:partName>
api/upload/view
user/<str:username>
GetParent
RepositoryDiagram/<str:repositoryName>
ShowRepository/<str:repositoryName>
```
