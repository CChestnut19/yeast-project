import sys
sys.path.append('..')
import numpy as np
from bokeh.io import curdoc
from bokeh.models import Row,Column,widgets,ColumnDataSource,Slider,InlineStyleSheet
from bokeh.plotting import figure
from Entity.DBD import GetDBDMenu,GetDBDNameList
from Entity.LBD import GetLBDDimerMenu,GetLBDNRMenu,GetLBDDimerNameList,GetLBDNRNameList
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from pathlib import Path
import os


#下游启动子输出
def DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0):
    """Stable yeast CIC response; Imax is amplitude (ceiling I0 + Imax)."""
    k1, k2, k3, I, L, Imax, kd, I0 = (
        np.asarray(value, dtype=float)
        for value in (k1, k2, k3, I, L, Imax, kd, I0))
    if any(not np.isfinite(value).all() or np.any(value < 0)
            for value in (k1, k2, k3, I, L, Imax, kd, I0)):
        raise ValueError("Response parameters must be finite and non-negative")
    b = 1.0 + k2 * I
    d = k1 + k2**2 * k3 * I**2
    root = np.sqrt(b**2 + 8.0 * d * L)
    active_pool = d * np.square(2.0 * L / (b + root))
    z = kd * active_pool
    return I0 + Imax * z / (1.0 + z)


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
api_url = os.environ.get("WebDatabase_URL") or os.environ.get("BIOAPP_API_URL")
if not api_url:
    raise RuntimeError("CIC-Designer 配置错误：请在 CIC-Designer/.env 中设置 WebDatabase_URL 或 BIOAPP_API_URL")

class TimeoutSession(requests.Session):
    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', 10)
        return super().request(method, url, **kwargs)


session = TimeoutSession()
retry = Retry(
    total=4,
    connect=4,
    read=4,
    status=4,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({'GET'}),
)
session.mount('http://', HTTPAdapter(max_retries=retry))
session.mount('https://', HTTPAdapter(max_retries=retry))

def ReadExcel(Type):
    if(Type == "LBDDimer"):
        return GetLBDDimerMenu(api_url,session)
    elif(Type == "LBDNR"):
        return GetLBDNRMenu(api_url,session)
    elif(Type == "DBD"):
        return GetDBDMenu(api_url,session)

def GetNameList(Type):
    if(Type == "LBDDimer"):
        return GetLBDDimerNameList(api_url,session)
    elif(Type == "LBDNR"):
        return GetLBDNRNameList(api_url,session)
    elif(Type == "DBD"):
        return GetDBDNameList(api_url,session)


def update_LBDDBDDimerData(attr,old,new):
    NewParameter = LBDDimerMenu[new]
    k1 = NewParameter[0]
    k2 = NewParameter[1]
    k3 = NewParameter[2]
    DBDParameter = DBDMenu[DBDSelect.value]
    I0 = DBDParameter[0]
    kd = DBDParameter[1]
    I = np.logspace(-6,4,N)
    L = LSlider.value
    y1 = DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0)
    source1.data = dict(Inducer = I, Output = y1)




def update_DBDData(attr,old,new):
    L = LSlider.value
    print(LBDDimerSelect.value)
    DBDParameter = DBDMenu[new]
    I0 = DBDParameter[0]
    kd = DBDParameter[1]
    DimerParameter = LBDDimerMenu[str(LBDDimerSelect.value)]
    k1 = DimerParameter[0]
    k2 = DimerParameter[1]
    k3 = DimerParameter[2]
    I = np.logspace(-6,4,N)
    y1 = DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0)
    source1.data = dict(Inducer = I, Output = y1)


def update_LSlider_data(attrname,old,new):
    L = LSlider.value
    DBDParameter = DBDMenu[DBDSelect.value]
    I0 = DBDParameter[0]
    kd = KdSlider.value
    DimerParameter = LBDDimerMenu[LBDDimerSelect.value]
    k1 = DimerParameter[0]
    k2 = DimerParameter[1]
    k3 = DimerParameter[2]
    I = np.logspace(-6,4,N)
    y1 = DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0)
    source1.data = dict(Inducer = I, Output = y1)
    

def update_KdSlider_data(attrname,old,new):
    L = LSlider.value
    kd = KdSlider.value
    DBDParameter = DBDMenu[DBDSelect.value]
    I0 = DBDParameter[0]
    DimerParameter = LBDDimerMenu[LBDDimerSelect.value]
    k1 = DimerParameter[0]
    k2 = DimerParameter[1]
    k3 = DimerParameter[2]
    I = np.logspace(-6,4,N)
    y1 = DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0)
    source1.data = dict(Inducer = I, Output = y1)




LBDDimerMenu = ReadExcel("LBDDimer")
print(LBDDimerMenu)

DBDMenu = ReadExcel("DBD")
print(DBDMenu)
stylesheet = InlineStyleSheet(css="""
.title{
    width:50%;
    height:100%;
    font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size:16px;
    margin:auto;
    text-align:center;
}
.description{
    width:80%;
    margin:auto;
    font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size:14px;
}
.FooterClass{
    width:100%
}
""")

stylesheet2 = InlineStyleSheet(css="""
.inputs{
    border:1px solid black;
    margin-left:30px;
}
.sliderpart{
    margin-top:30px;
}
.plot{
    margin-left:50px;
}
.LBDDBDContainerClass{
    width:50%;
    margin:auto;
}
""")



stylesheet4 = InlineStyleSheet(css="""
.content{
    width:80%;
    margin:auto;
}
.inputs{
    border:1px solid black;
    width:100%;
}
""")

stylesheet5 = InlineStyleSheet(css = """
.LBDContainerClass{
    height:250px;
    width:50%;
    margin:auto;
}
.DBDContainerClass{
    height:250px;
    width:50%;
    margin:auto;
}
""")

stylesheet6 = InlineStyleSheet(css = """
.bk-clearfix{
    width:100%;
}
""")


Title = widgets.Div(text="""
<h1>CIC Designer</h1>
""")
Description = widgets.Div(text="""
<hr>
<p>Use the figure below to explore how changes to the various parameter values. The Dimer module plot are colored in blue.The figure was generated using the Bokeh plotting framework.</p>
""")
N=1000
k1 = 0.0000727
k2 = 4.627521
k3 = 0.693479
kx1 = 0.65925
kx2 = 3.65837
L = 1.5
Imax = 35.84932
#假设为连续的
kd = 6.216347694
I0 = 0.01
I = np.logspace(-6,4,N)
y1 = DimerModelCaculate(k1,k2,k3,I,L,Imax,kd,I0)
# y2 = NRModelCaculate(k1,k2,k3,kx1,kx2,I,L,Imax,kd,I0)
source1 = ColumnDataSource(data = dict(Inducer = I, Output = y1))
# source2 = ColumnDataSource(data = dict(Inducer = I, Output = y2))


TwinPlot = figure(height=300,width=300,title="Dimer Plot",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_axis_type = "log",
              y_axis_type = "log",
              x_range=[0.000001,1000],y_range=[0.01,100])
TwinPlot.title.text_font_size = "16px"
TwinPlot.line('Inducer','Output',source=source1,line_width=2,line_color = "#4D80E6")
TwinPlot.css_classes = ["plot"]

# NRPlot = figure(height=300,width=300,title = "NR Plot",
#                 tools="crosshair,pan,reset,save,wheel_zoom",x_axis_type="log",y_axis_type="log",x_range=[0.000001,1000],y_range=[0.01,100])
# NRPlot.title.text_font_size = "16px"
# NRPlot.line('Inducer','Output',source = source2,line_width=2,line_color = "#FA8072")

LSlider = Slider(title='L',value=1.5,start=0,end=10,step=0.001,bar_color='rgb(115,143,193)')
KdSlider = Slider(title='kd',value=6.216347694,start=0,end=41,step=0.001,bar_color='rgb(232,177,157)')

DimerNameList = list(LBDDimerMenu.keys())
DBDNameList = list(DBDMenu.keys())
print(DimerNameList)
print(DBDNameList)
LBDDimerSelect = widgets.Select(title="Dimer LBD",value = DimerNameList[0],options=DimerNameList)
# LBDNRSelect = widgets.Select(title = "NR LBD",value = NRNameList[0],options=NRNameList)
DBDSelect = widgets.Select(title = "DBD",value = DBDNameList[0],options=DBDNameList)

LBDDimerSelect.on_change('value',update_LBDDBDDimerData)
# LBDNRSelect.on_change('value',update_LBDDBDNRData)
DBDSelect.on_change('value',update_DBDData)

LSlider.on_change('value',update_LSlider_data)
KdSlider.on_change('value',update_KdSlider_data)
LBDTitle = widgets.Div(text = """
<h5> LBD Parameters </h5>
""")
DBDTitle = widgets.Div(text="""
<h5> DBD Parameters </h5>
""")
#fixed
LBDDimerContainer = Row(children = [LBDDimerSelect])
# LBDNRContainer = Row(children = [LBDNRSelect])
LBDContainer = Column(children=[LBDTitle,LBDDimerContainer])
LBDContainer.css_classes = ["LBDContainerClass"]
DBDContainer = Column(children=[DBDTitle,DBDSelect])
DBDContainer.css_classes = ["DBDContainerClass"]
LBDDBDContainer = Row(children=[LBDContainer,DBDContainer])
LBDDBDContainer.css_classes = ["LBDDBDContainerClass"]
LBDDBDContainer.stylesheets = [stylesheet5]



# inputs = Column(children=[LSlider,KdSlider,LBDDBDContainer])
SliderParts = Column(children=[LSlider,KdSlider])
SliderParts.css_classes = ["sliderpart"]
inputs = Row(children=[SliderParts,LBDDBDContainer])
inputs.css_classes = ["inputs"]
inputs.stylesheets = [stylesheet2]
Title.css_classes = ["title"]
Description.css_classes = ["description"]
PlotRow = Row(children=[TwinPlot])
ControllerRow = Column(children=[inputs,PlotRow])
ControllerRow.stylesheets = [stylesheet4]
ControllerRow.css_classes = ["content"]
layout = Column(children = [Title,Description,
                            ControllerRow,
                           ])
layout.stylesheets = [stylesheet,stylesheet2,stylesheet4]

curdoc().title = "CIC-Designer"
curdoc().add_root(layout)
from bokeh.embed import server_document
url = os.environ["Plot_Bokeh"]
print(url)
script = server_document(url)
# print(script)
