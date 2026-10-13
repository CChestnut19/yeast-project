# TFPlot

TFPlot 是一个基于 Flask 与 Bokeh 的转录因子设计工具，提供数据上传、参数拟合、设计结果可视化以及 Level 2/Level 3 组装。组装任务完成后，浏览器会自动下载生成的 GenBank（`.gb`）文件。

## 服务组成

本项目需要同时运行两个进程：

| 服务 | 入口 | 默认用途 |
| --- | --- | --- |
| Bokeh 服务 | `GUI/Plot.py` | 提供交互式曲线图 |
| Flask 服务 | `app.py` | 提供页面、拟合、组装和文件下载接口 |

Flask 的 `/TFPlot` 页面会连接 `Plot_Bokeh` 指定的 Bokeh 地址，因此应先启动 Bokeh，再启动 Flask。

## 环境要求

- Windows 或 Linux
- Python 3.10 或 3.11
- Conda（推荐）或 `venv`
- 可访问配置的 WebDatabase 服务

> 当前 `requirements.txt` 包含 CUDA/Linux 相关依赖（例如 `nvidia-*`、`triton`）。Windows 或无 CUDA 的机器如果完整安装失败，可先安装下方列出的运行所需核心依赖。

## 安装依赖

### 推荐：创建独立 Conda 环境

```powershell
conda create -n tfplot python=3.11 -y
conda activate tfplot
cd C:\Users\admin\Desktop\外包项目\TFPlot
python -m pip install Flask==3.1.1 bokeh==3.7.3 tornado==6.5.1 python-dotenv requests
python -m pip install numpy pandas scipy matplotlib biopython openpyxl
python -m pip install dna-features-viewer dnacauldron fuzzywuzzy python-Levenshtein snapgene-reader xlrd xlwt xmltodict
```

如果当前平台能够满足 `requirements.txt` 中的全部依赖，也可以直接安装：

```powershell
python -m pip install -r requirements.txt
python -m pip install python-dotenv requests
```

## 配置 `.env`

在项目根目录（与 `app.py` 同级）创建或修改 `.env`：

```dotenv
# Flask 监听地址（可选，默认 0.0.0.0）
data_host=0.0.0.0

# 上传目录和下载模板，必须使用实际存在的绝对路径
UPLOAD_File=C:/path/to/TFPlot/File/UPLOAD_FOLDER/Data
template_file=C:/path/to/TFPlot/File/UPLOAD_FOLDER/Template.csv

# WebDatabase 中已存在的载体名称
Level2_Backbone_Name=Level2载体名称
Level3_Backbone_Name=Level3载体名称

# Django 服务根地址，不包含 /WebDatabase 或 /LabDatabase
WebDatabase_URL=http://数据库服务地址:端口

# WebDatabase 登录凭据，不要提交到 Git
username=你的用户名
password=你的密码

# Bokeh 应用地址；末尾路径必须与 Plot.py 文件名一致
Plot_Bokeh=http://Bokeh服务地址:5006/Plot

# 上传任务限制（可选）
UPLOAD_TASK_TTL_SECONDS=86400
UPLOAD_MAX_FILES=20
UPLOAD_MAX_REQUEST_BYTES=52428800

# 可选：指定组装结果在服务器上的临时保存位置
# result_file=C:/path/to/output/Level3.gb
```

### 环境变量说明

| 变量 | 必填 | 用途 |
| --- | --- | --- |
| `UPLOAD_File` | 是 | Flask 保存上传数据文件的目录；目录必须提前创建并具有写权限 |
| `template_file` | 是 | `/DownloadTempalte` 接口返回的模板文件绝对路径 |
| `Level2_Backbone_Name` | 是 | Level 2 组装使用的 WebDatabase 载体名称 |
| `Level3_Backbone_Name` | 是 | Level 3 组装使用的 WebDatabase 载体名称 |
| `WebDatabase_URL` | 是 | WebDatabase API 根地址 |
| `username` | 是 | `WebDatabaseAssemblyClient` 使用的登录用户名 |
| `password` | 是 | `WebDatabaseAssemblyClient` 使用的登录密码 |
| `Plot_Bokeh` | 是 | Flask 嵌入的 Bokeh 应用完整地址，通常以 `/Plot` 结尾 |
| `UPLOAD_TASK_TTL_SECONDS` | 否 | 上传拟合任务保留时间，默认 86400 秒 |
| `UPLOAD_MAX_FILES` | 否 | 单次最多上传 CSV 数，默认 20 |
| `UPLOAD_MAX_REQUEST_BYTES` | 否 | 单次上传请求最大字节数，默认 50 MiB |
| `data_host` | 否 | Flask 监听地址，默认 `0.0.0.0` |
| `result_file` | 否 | 固定组装结果路径；不设置时使用按任务 UUID 生成的临时文件 |

路径推荐使用正斜杠，例如 `C:/data/uploads`。如果使用反斜杠，不需要在 `.env` 中写成 Python 字符串形式，也不要添加 `r"..."`。

## 启动服务

下面的命令需要在两个终端中分别运行，并激活同一个 Python 环境。

### 1. 启动 Bokeh

```powershell
conda activate tfplot
cd C:\Users\admin\Desktop\外包项目\TFPlot\GUI
bokeh serve Plot.py --port 5006 --allow-websocket-origin=10.30.76.2:8101
```

如果 Flask 使用其他主机名或端口，请同步修改 `--allow-websocket-origin`。仅在受信任的开发网络中，可以临时使用：

```powershell
bokeh serve Plot.py --port 5006 --allow-websocket-origin=*
```

PowerShell 命令末尾不要添加 `\`；它不是 Windows 的续行符。

### 2. 启动 Flask

打开第二个终端：

```powershell
conda activate tfplot
cd C:\Users\admin\Desktop\外包项目\TFPlot
python app.py
```

Flask 的监听地址由 `.env` 中的 `data_host` 控制，默认 `0.0.0.0`；端口由 `PORT` 控制，默认 `8101`。仅本机访问可将 `data_host` 设置为 `127.0.0.1`。

### 3. 访问页面

浏览器打开：

```text
http://10.30.76.2:8101/TFPlot
```

正常情况下，页面会显示 Bokeh 图表，并可以执行参数计算、数据拟合和组装。点击 Assembly 后，后端等待 Level 2 和 Level 3 任务完成，然后浏览器自动下载 `Level3-<UUID>.gb`。

## 启动前检查

```powershell
python -c "from dotenv import dotenv_values; c=dotenv_values('.env'); print({k: bool(c.get(k)) for k in ('UPLOAD_File','template_file','Level2_Backbone_Name','Level3_Backbone_Name','WebDatabase_URL','username','password','Plot_Bokeh')})"
```

所有项目都应显示为 `True`。该命令只检查变量是否存在，不会输出密码。

还应确认：

1. `UPLOAD_File` 目录存在且可写。
2. `template_file` 指向的文件存在。
3. `WebDatabase_URL` 可以从运行 TFPlot 的机器访问。
4. `Plot_Bokeh` 与实际 Bokeh 地址、端口和 `/Plot` 路径一致。
5. Flask 的来源地址已加入 Bokeh 的 `--allow-websocket-origin`。

## 常见问题

### `PackagesNotFoundError: dotenv`

安装包名是 `python-dotenv`，导入名才是 `dotenv`：

```powershell
python -m pip install python-dotenv
```

### Bokeh 页面空白或提示 WebSocket 连接失败

- 确认 Bokeh 服务已经启动。
- 确认 `.env` 中的 `Plot_Bokeh` 以 `/Plot` 结尾。
- 确认 Flask 的 `主机:端口` 已传给 `--allow-websocket-origin`。
- 不要在 `--allow-websocket-origin` 参数末尾添加反斜杠。

### `KeyError` 或提示缺少配置

检查 `.env` 是否位于项目根目录，以及变量名大小写是否与本文完全一致。修改 `.env` 后应重启 Flask 和 Bokeh 进程。

### `[ASN1: NOT_ENOUGH_DATA]`

这是 Anaconda Python 读取 Windows 证书库失败，并非 `Plot.py` 代码错误。建议使用新建的独立 Conda 环境；如果新环境仍报错，需要检查 Windows 证书库中的异常证书。

## 当前配置限制

- `GUI/Plot.py` 当前仍包含独立的 WebDatabase 地址和登录配置，尚未读取根目录 `.env`。部署到其他环境时，需要同步修改该文件；生产环境建议后续统一改为从 `.env` 读取，并移除代码中的明文凭据。
- `.env` 含敏感信息，应加入 `.gitignore`，不要提交用户名和密码。

## 主要目录

| 路径 | 说明 |
| --- | --- |
| `app.py` | Flask 入口及页面/API 路由 |
| `GUI/Plot.py` | Bokeh 绘图服务入口 |
| `Services/` | 参数计算、拟合和 WebDatabase 组装客户端 |
| `Entity/` | Part、LBD、DBD、Backbone 等领域模型 |
| `templates/` | Flask HTML 模板 |
| `File/` | 上传模板、示例数据和历史输出文件 |


## CIC-Designer 组装 API 对接

组装客户端使用 Django 登录会话与 CSRF，不再使用 bio-app Token。启动前在本目录的 `.env` 配置 `WebDatabase_URL`、`username`、`password` 和两个 Backbone 名称；也支持 `WEBDATABASE_USERNAME` / `WEBDATABASE_PASSWORD`。每个组装请求使用独立会话，登录后再读取元件。

- 提交：`POST /LabDatabase/AssemblyWithoutRepo`，JSON 字段为 `uuid`、`part`（ID）、`backbone`（名称）、`plasmid`（名称）、`scar`。
- 轮询：`GET /LabDatabase/task_status/{task_id}`，读取顶层 `status` 和 `result`。
- 第一阶段：读取 `result.plasmid_id`，通过 `/WebDatabase/PlasmidNameByID?ID=...` 获取真实入库名称，再提交第二阶段。
- 第二阶段：通过同一登录会话下载 `result.download_url`；Flask `/Assembly` 返回文件附件，与页面下载逻辑对应。默认临时文件在读取后删除；设置 `result_file` 则保留指定文件（并发使用应保持默认）。

提交请求不会自动重试，避免创建重复任务。当前 WebDatabase 的无仓库接口不读取客户端 `level`，数据库中的结果等级仍由服务端推断；客户端的 Level2/Level3 是流程阶段名称。未更改服务端的组装或等级规则。


## 优化评分与 yeast 对齐

`Services/opt.py` 直接实现稳定 CIC 质量守恒与响应公式，不导入 yeast。默认优化目标为 `log10(on/off) + log10(on-off)`，固定等权；页面不再提供 alpha/beta 控件。

DBD 的名称、`I0` 和 `kd` 从同一次 `GetDBDMenu` 返回中配对读取。无诱导响应使用诱导剂浓度 0。排除非有限值及不满足 `on > off > 0` 的候选；没有有效候选时返回错误，不选择最后一条记录。

默认仍搜索 L=0.3～10 的 2000 个等距点，`Imax=35.84931505` 表示幅度而非总上限，诱导剂浓度采用各 LBD 参数记录中的 `i`，单位必须与该记录的参数一致。数值入口 `scan_designs` 可传入网格、幅度与可选核转运参数，以便与 yeast 使用完全相同输入进行比较；本次未增加 Pareto 或高斯过程搜索，也未修改参数拟合损失。

`/Opt` 返回 `score`；`MaxFoldchange` 保留为兼容别名，二者均为综合评分而非单独诱导倍数。保留三个历史 CSV 文件名：`new_foldchange_max_values.csv`（评分）、`new_max_L_values.csv`（浓度）、`new_output.csv`（诱导输出）；无有效点的组合留空。
