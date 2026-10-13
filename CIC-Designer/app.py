import flask
from bokeh.client import pull_session
from bokeh.embed import server_session
from Services.opt import HtmlReturn
# from WebAssembly import WebAssembly
from Services.WebAssembly import WebAssembly
from Services.WebDatabaseAssemblyClient import AssemblyAPIError
from Services.UploadTaskStore import create_upload_task, get_upload_task_files
from werkzeug.utils import secure_filename
import os
import Services.ParaCal as ParaCal
from Entity import LBD, DBD
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().with_name(".env"))

_required_config = ("UPLOAD_File", "template_file", "Plot_Bokeh")
_missing_config = [name for name in _required_config if not os.getenv(name)]
if not (os.getenv("WebDatabase_URL") or os.getenv("BIOAPP_API_URL")):
    _missing_config.append("WebDatabase_URL 或 BIOAPP_API_URL")
if _missing_config:
    raise RuntimeError(
        "TFPlot 配置错误：缺少 " + ", ".join(_missing_config)
        + "。请复制 TFPlot/.env.example 为 TFPlot/.env 并填写配置。"
    )

app = flask.Flask(__name__,template_folder='templates')
ALLOWED_EXTENSIONS = {'xlsx','xls','csv'}
UPLOAD_File = rf'{os.environ["UPLOAD_File"]}'
TEMPLATE_FILE = rf'{os.environ["template_file"]}'
WEBDATABASE_URL = os.getenv("WebDatabase_URL") or os.getenv("BIOAPP_API_URL")
Plot_Bokeh=rf'{os.environ["Plot_Bokeh"]}'
app.config['UPLOAD_FILE'] = UPLOAD_File
app.config['MAX_CONTENT_LENGTH'] = int(
    os.getenv('UPLOAD_MAX_REQUEST_BYTES', str(50 * 1024 * 1024))
)
import requests
app.config['api_url'] =  WEBDATABASE_URL
def get_webdb_session(force_login=False):
    session = app.config.get('webdb_session')
    if force_login or session is None:
        session = requests.Session()
        app.config['webdb_session'] = session
    if flask.has_request_context():
        token = flask.request.headers.get('Token', '')
        if token:
            session.headers.update({'Token': token})
    return session
# @app.route("/login",methods = ['GET'])
# def login():
#     # print("111111")
    # login_url = f'{app.config["api_url"]}login'
    # test_url = f'{app.config["api_url"]}Part'
    # credentials = {'uname':'root','password':'chenlab'}
    # session = requests.Session()
    # response = session.get(login_url)
    # csrftoken = session.cookies.get('csrftoken')
    # headers = {'X-CSRFToken':csrftoken,'Content-Type':'application/json'}
    # response = session.post(login_url,json=credentials,headers=headers)
    # if(response.status_code == 200):
    #     print(111)
    #     return flask.redirect('/test')
    # else:
    #     print("000")
    # session = requests.get(f'{app.config["api_url"]}login')
    # print(f'{app.config["api_url"]}login')
    # print(session.text)
# @app.route("/test",methods=['GET'])
# def test_connection():
#     try:
#         print(f'{app.config["api_url"]}GetLBDDimerNameList')
#         response = requests.get(f'{app.config["api_url"]}GetLBDDimerNameList')
#         return f"{response.text}"
#     except requests.exceptions.ConnectionError:
#         return False
def getsession():
    return get_webdb_session()
@app.route("/Opt",methods=['POST'])
def Opt():
    session = get_webdb_session()
    alpha = flask.request.form.get('alpha')
    beta = flask.request.form.get('beta')
    LBD = flask.request.form.get('LBD') or flask.request.form.get('lbd')
    DBD = flask.request.form.get('DBD') or flask.request.form.get('dbd')
    try:
        Result = HtmlReturn(alpha,beta,app.config['api_url'],session,LBD,DBD)
    except ValueError as exc:
        return flask.jsonify({'success': False, 'message': str(exc)}), 400
    #使用Result中的LBD和DBD进行自动化设计对于上游TF的选择
    response = {'MaxFoldchange':Result[0],"LBD":Result[1],"DBD":Result[2],"L":Result[3],"RPU":Result[4]}
    return flask.jsonify(response)
@app.route("/TFPlot",methods=['GET'])
def bkapp_page():
    
    # url 为Bokeh服务的启动地址（根据实际情况更改）
    with pull_session(url=Plot_Bokeh) as session_bokeh:
        # session = requests.Session()
        # login_response = session.get(f'{app.config["api_url"]}login')
        # response = requests.post(f'{app.config["api_url"]}login')
        # print(f'{app.config["api_url"]}login')
        session = get_webdb_session(force_login=True)


        script = server_session(session_id=session_bokeh.id,url=Plot_Bokeh)
        LBDList = LBD.GetLBDDimerNameList(app.config['api_url'],session)
        DBDList = DBD.GetDBDNameList(app.config['api_url'],session)
        return flask.render_template("TF Plot.html",LBDList = LBDList, DBDList = DBDList, script = script,template="Flask")
@app.route("/Assembly",methods=['POST'])
def AssemblyServe():
    LBD = flask.request.form.get('LBD')
    DBD = flask.request.form.get('DBD')
    L = flask.request.form.get('L')
    print(DBD)
    print(LBD)
    try:
        session = get_webdb_session()
        token = flask.request.headers.get('Token', '')
        assembly = WebAssembly(LBD, DBD, L, app.config['api_url'], session, token=token)
        result = assembly.AssemblyFuntion()
        return flask.jsonify(result)
    except (AssemblyAPIError, OSError, KeyError) as exc:
        return flask.jsonify({"success": False, "message": str(exc)}), 500
@app.route("/UploadData",methods=['POST'])
def UploadDataMethod():
    upload_files = [
        uploaded_file
        for uploaded_file in flask.request.files.getlist('file')
        if uploaded_file.filename
    ]
    if not upload_files:
        return flask.jsonify({
            "success": False,
            "message": "No files were selected for upload.",
        }), 400

    invalid_files = [
        uploaded_file.filename
        for uploaded_file in upload_files
        if Path(secure_filename(uploaded_file.filename)).suffix.lower() != '.csv'
    ]
    if invalid_files:
        return flask.jsonify({
            "success": False,
            "message": "Only CSV files are supported: " + ", ".join(invalid_files),
        }), 400

    max_files = int(os.getenv("UPLOAD_MAX_FILES", "20"))
    if len(upload_files) > max_files:
        return flask.jsonify({
            "success": False,
            "message": f"A maximum of {max_files} files may be uploaded at once.",
        }), 400

    task_files = [
        (uploaded_file, secure_filename(uploaded_file.filename))
        for uploaded_file in upload_files
    ]
    metadata = create_upload_task(app.config['UPLOAD_FILE'], task_files)
    return flask.jsonify({
        "success": True,
        "upload_id": metadata["upload_id"],
        "uploaded": len(metadata["files"]),
        "message": f"{len(metadata['files'])} file(s) uploaded successfully.",
    })


@app.errorhandler(413)
def UploadTooLarge(_error):
    return flask.jsonify({
        "success": False,
        "message": "The upload request exceeds the configured size limit.",
    }), 413
@app.route("/DownloadTempalte",methods=['GET'])
def DownloadTemplate():
    # 发送文件地址根据实际情况更改
    print(TEMPLATE_FILE)
    return flask.send_file(TEMPLATE_FILE)
@app.route("/Fitting",methods=['POST'])
def FittingCal():
    if(flask.request.method == "POST"):
        upload_id = flask.request.form.get("upload_id", "").strip()
        if not upload_id:
            return flask.jsonify({
                "success": False,
                "message": "upload_id is required. Upload the fitting data first.",
            }), 400
        session = get_webdb_session()
        algorithm = flask.request.form.get("Algorithm")
        I0 = flask.request.form.get("I0")
        if(I0 == None or I0 == "" or I0 == 0):
            I0 = 0.015930056
        else:
            I0 = float(I0)
        Imax = 35.84931505
        try:
            upload_file_list = get_upload_task_files(
                app.config['UPLOAD_FILE'], upload_id
            )
            result = ParaCal.AnalysisExcel(
                upload_file_list,
                algorithm,
                I0,
                Imax,
                app.config['api_url'],
                session,
            )
        except (ValueError, OSError) as exc:
            print(str(exc))
            return flask.jsonify(
                {"success": False, "message": str(exc)}
            ), 400
        DBDResult = result[0][0]
        LBDResult = result[1][0]
        return flask.jsonify({"success":True,"DBD":DBDResult['name'],"LBD":LBDResult['name']})


@app.route("/FittingResult", methods=['GET'])
def FittingResult():
    dbd_name = flask.request.args.get('DBD', '').strip()
    lbd_name = flask.request.args.get('LBD', '').strip()
    if not dbd_name or not lbd_name:
        return flask.jsonify({
            "success": False,
            "message": "DBD and LBD query parameters are required.",
        }), 400

    api_url = app.config['api_url'].rstrip('/')
    if api_url.lower().endswith('/webdatabase'):
        api_url = api_url[:-len('/WebDatabase')]

    try:
        session = get_webdb_session()
        # dbd = DBD.GetDBD(api_url, dbd_name, session)
        DBD_Data = DBD.GetDBDKdI0(api_url,dbd_name,session)
        # lbd = LBD.GetLBDDimer(api_url, lbd_name, session)
        LBD_Data = LBD.GetLBDValue(api_url,lbd_name,session)
        print(DBD_Data)
        print(LBD_Data)
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        return flask.jsonify({
            "success": False,
            "message": f"Failed to load fitting result: {exc}",
        }), 502

    if DBD_Data is None or LBD_Data is None:
        return flask.jsonify({
            "success": False,
            "message": "The requested DBD or LBD fitting result was not found.",
        }), 404

    data = {
        "DBD": {
            "Name": dbd_name,
            "I0": DBD_Data["Kd"],
            "kd": DBD_Data["I0"],
        },
        "LBD": {
            "Name": lbd_name,
            "k1": LBD_Data["k1"],
            "k2": LBD_Data["k2"],
            "k3": LBD_Data["k3"],
            "I": LBD_Data["I"],
        },
    }
    return flask.render_template("FittingResultShow.html", data=data)


if __name__ == "__main__":
    app.run(
        host=os.getenv("data_host", "0.0.0.0"),
        port=int(os.getenv("PORT", "8101")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
