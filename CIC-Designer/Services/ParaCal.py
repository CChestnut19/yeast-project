"""Fit DBD and LBD parameters from uploaded CSV files."""

import pandas as pd

from Entity import DBD, LBD
from . import DiffLBD, DiffLBDCurveFit, sameLBD


REQUIRED_COLUMNS = {"LBDName", "DBDName", "LBD", "inducer", "RPU"}
NUMERIC_COLUMNS = ("LBD", "inducer", "RPU", "I0", "Imax")


def _entity_api_base(api_url):
    """Return the host prefix expected by legacy Entity API helpers."""
    base = api_url.rstrip("/")
    suffix = "/WebDatabase"
    if base.lower().endswith(suffix.lower()):
        return base[:-len(suffix)]
    return base


def GetKd(api_url, session, dbd_name):
    """Fetch a DBD kd value through the WebDatabase API."""
    return DBD.GetDBDKd(_entity_api_base(api_url), dbd_name, session)


def _read_uploads(upload_file_list):
    if not upload_file_list:
        raise ValueError("No fitting data has been uploaded")

    frames = [pd.read_csv(path) for path in upload_file_list]
    dataframe = pd.concat(frames, ignore_index=True)
    missing = sorted(REQUIRED_COLUMNS.difference(dataframe.columns))
    if missing:
        raise ValueError(
            "Fitting data is missing required columns: " + ", ".join(missing)
        )

    for column in NUMERIC_COLUMNS:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    dataframe = dataframe.dropna(subset=list(REQUIRED_COLUMNS)).reset_index(drop=True)
    if dataframe.empty:
        raise ValueError("Fitting data contains no valid rows")
    return dataframe


def AnalysisExcel(upload_file_list, algorithm, I0, Imax, api_url, session):
    dataframe = _read_uploads(upload_file_list)

    # Fit DBD parameters using all DBDs measured with the same reference LBD.
    fixed_lbd_name = dataframe["LBDName"].iloc[0]
    dbd_source = dataframe[dataframe["LBDName"] == fixed_lbd_name]
    dbd_groups = list(dbd_source.groupby("DBDName", sort=False))
    dbd_name_list = [name for name, _ in dbd_groups]
    dbd_data = [group.copy().reset_index(drop=True) for _, group in dbd_groups]
    all_dbd_data = pd.concat(dbd_data, ignore_index=True)

    # Fit LBD parameters using all LBDs measured with the same reference DBD.
    fixed_dbd_name = dbd_name_list[0]
    lbd_source = dataframe[dataframe["DBDName"] == fixed_dbd_name]
    lbd_groups = list(lbd_source.groupby("LBDName", sort=False))
    lbd_name_list = [name for name, _ in lbd_groups]

    return CalPara(
        algorithm,
        float(I0),
        float(Imax),
        all_dbd_data,
        dbd_name_list,
        dbd_data,
        lbd_name_list,
        lbd_groups,
        fixed_dbd_name,
        api_url,
        session,
    )


def CalPara(
    algorithm,
    I0,
    Imax,
    all_dbd_data,
    dbd_name_list,
    dbd_data,
    lbd_name_list,
    lbd_groups,
    fixed_dbd_name,
    api_url,
    session,
):
    entity_api_url = _entity_api_base(api_url)
    model = sameLBD.MyModel()
    dbd_results = sameLBD.cal(
        model, all_dbd_data, dbd_name_list, dbd_data, I0, Imax
    )
    print(dbd_results)

    result_list_dbd = []
    for result in dbd_results:
        dbd = DBD.DBD(
            result["name"], "", "", "", "", "", "", "",
            result["I0"], result["kd"],
        )
        print(dbd.save(entity_api_url, session))
        result_list_dbd.append(
            {"name": result["name"], "I0": result["I0"], "kd": result["kd"]}
        )

    kd = GetKd(api_url, session, fixed_dbd_name)
    if kd is None:
        raise ValueError(f"No kd value returned for DBD {fixed_dbd_name}")
    print(kd)
    lbd_data = []
    for _, group in lbd_groups:
        fit_data = group.copy().reset_index(drop=True)
        fit_data["kd"] = float(kd)
        lbd_data.append(fit_data)
    
    fitter = DiffLBD.cal if algorithm == "CNN" else DiffLBDCurveFit.cal
    result_list_lbd = []
    print("1111")
    for lbd_name, fit_data in zip(lbd_name_list, lbd_data):
        fitted = fitter(lbd_name, fit_data, I0, Imax)
        lbddimer = LBD.LBDDimer(
            lbd_name, "", "", "", "", "", "", "",
            fitted[0], fitted[1], fitted[2], 1,
        )
        lbddimer.save(entity_api_url, session)
        print("0000000")
        result_list_lbd.append(
            {
                "name": lbd_name,
                "k1": fitted[0],
                "k2": fitted[1],
                "k3": fitted[2],
                "I": 1,
            }
        )

    return [result_list_dbd, result_list_lbd]


if __name__ == "__main__":
    raise SystemExit("Run parameter fitting through the Flask /Fitting endpoint")
