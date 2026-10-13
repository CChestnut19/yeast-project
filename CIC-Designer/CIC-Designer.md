---
title: CIC-Designer
language_tabs:
  - http: HTTP
  - javascript: JavaScript
  - python: Python
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30,@WEIBOYAN"

---

# CIC Designer


## POST createConnect

GET /createConnect

用户登录创建和数据库的连接

> 返回示例

> success Response

```json
{
  "success": "True"
}
```
>error Response

```json
{
  "Error":"Login Error"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» success|string|true|none||none|

## POST Opt

POST /Opt

输入用户对LBD，DBD最优化的偏向需求（alpha和beta），对最优解进行计算病返回最大foldChange，最优LBD，最优DBD，最优表达量，最优RPU

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|alpha|query|integer| 是 |用户对于最优解的偏好（fold change1）|
|bata|query|integer| 是 |用户对于最优解的偏好（fold change2）|

> 返回示例

> 200 Response

```json
{
  "MaxFoldchange": 0,
  "LBD": "string",
  "DBD": "string",
  "L": 0,
  "RPU": 0
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» MaxFoldchange|number|true|none|最大FoldChange|none|
|» LBD|string|true|none|LBD选择|none|
|» DBD|string|true|none|DBD选择|none|
|» L|number|true|none|最佳L|none|
|» RPU|number|true|none|最佳表达量|none|

## GET TFPlot

GET /TFPlot

渲染界面，并嵌入Bokeh服务

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

## POST Assembly

POST /Assembly

元件组装

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|LBD|query|string| 否 |none|
|DBD|query|string| 否 |none|
|L|query|number| 否 |none|

> 返回示例

> 200 Response

```json
{
  "success": "True"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» success|string|true|none||none|

## GET Download

GET /Download

返回组装后的文件（Level3.gb）

> 返回示例

> 200 Response

```
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

## POST UploadData

POST /UploadData

用户上传实验数据文件

> Body 请求参数

```yaml
file: ""

```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» file|body|string(binary)| 否 |none|

> 返回示例

> 200 Response

```json
{
  "success": true,
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded": 1
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» Success|string|true|none||none|

## GET DownloadTemplate

GET /DownloadTemplate

用户请求下载实验数据标准模板（Template.csv）

> 返回示例

> 200 Response

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

## POST Fitting

POST /Fitting

根据用户提供的实验数据进行参数拟合

`application/x-www-form-urlencoded` 请求必须包含 `upload_id`，另可传 `Algorithm` 和 `I0`。

> 返回示例

> 200 Response

```json
{
  "success": "True"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» success|string|true|none||none|
