"""Fit shared LBD parameters and a kd value for each DBD."""

import torch
import torch.nn as nn


class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.k1 = nn.Parameter(torch.tensor(0.0001))
        self.k2 = nn.Parameter(torch.tensor(1.0))
        self.k3 = nn.Parameter(torch.tensor(0.01))
        self.kd = nn.Parameter(torch.tensor(10.0))

    def forward(self, L, I, I0, Imax):
        eps = torch.finfo(L.dtype).eps
        x1 = torch.sqrt(
            (self.k2 * I + 1) ** 2
            + 8 * L * (self.k2**2 * self.k3 * I**2 + self.k1)
            + eps
        )
        ratio = (x1 - (self.k2 * I + 1)) / (
            x1 + (self.k2 * I + 1) + eps
        )
        occupied = (L / 2) * ratio * self.kd
        return Imax * occupied / (1 + occupied + eps) + I0


def _tensor(dataframe, column, default=None):
    if column in dataframe.columns:
        series = dataframe[column]
        if default is not None:
            series = series.fillna(default)
        values = series.to_numpy(dtype="float32")
    elif default is not None:
        values = [default] * len(dataframe)
    else:
        raise ValueError(f"Fitting data is missing column {column}")
    return torch.as_tensor(values, dtype=torch.float32)


def _fit(model, parameters, dataframe, I0, Imax, epochs=10000):
    L = _tensor(dataframe, "LBD")
    inducer = _tensor(dataframe, "inducer")
    baseline = _tensor(dataframe, "I0", I0)
    maximum = _tensor(dataframe, "Imax", Imax)
    target = _tensor(dataframe, "RPU")
    optimizer = torch.optim.Adam(parameters, lr=0.0001)

    for _ in range(epochs):
        optimizer.zero_grad()
        loss = nn.functional.mse_loss(
            model(L, inducer, baseline, maximum), target
        )
        if not torch.isfinite(loss):
            raise ValueError("sameLBD fitting produced a non-finite loss")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(parameters, max_norm=1)
        optimizer.step()
        with torch.no_grad():
            model.k1.clamp_(min=1e-12)
            model.k2.clamp_(min=1e-12)
            model.k3.clamp_(min=1e-12)
            model.kd.clamp_(min=1e-12)


def cal(model, data_all, DBDNameList, SperAllData, I0, Imax):
    if len(DBDNameList) != len(SperAllData):
        raise ValueError("DBD names and fitting groups have different lengths")

    _fit(model, [model.k1, model.k2, model.k3], data_all, I0, Imax)
    model.k1.requires_grad_(False)
    model.k2.requires_grad_(False)
    model.k3.requires_grad_(False)

    results = []
    for dbd_name, dataframe in zip(DBDNameList, SperAllData):
        with torch.no_grad():
            model.kd.fill_(10.0)
        _fit(model, [model.kd], dataframe, I0, Imax)
        fitted_i0 = (
            float(dataframe["I0"].dropna().mean())
            if "I0" in dataframe and dataframe["I0"].notna().any()
            else float(I0)
        )
        results.append(
            {"name": dbd_name, "I0": fitted_i0, "kd": model.kd.item()}
        )
    return results
