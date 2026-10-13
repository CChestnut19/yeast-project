"""Fit one LBD with PyTorch while keeping the DBD kd fixed."""

import torch
from torch import nn


class Energy(nn.Module):
    def __init__(self):
        super().__init__()
        self.k1 = nn.Parameter(torch.tensor(1.6039031e-8))
        self.k2 = nn.Parameter(torch.tensor(0.01934156))
        self.k3 = nn.Parameter(torch.tensor(0.150686))

    def forward(self, L, I, I0, Imax, kd):
        eps = torch.finfo(L.dtype).eps
        x1 = torch.sqrt(
            (self.k2 * I + 1) ** 2
            + 8 * L * (self.k2**2 * self.k3 * I**2 + self.k1)
            + eps
        )
        ratio = (x1 - (self.k2 * I + 1)) / (
            x1 + (self.k2 * I + 1) + eps
        )
        occupied = (L / 2) * ratio * kd
        return Imax * occupied / (1 + occupied + eps) + I0


def _values(dataframe, column, default=None):
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


def cal(LBDName, SperLBDData, I0_val, Imax_val):
    if SperLBDData.empty:
        raise ValueError(f"No fitting rows for LBD {LBDName}")

    L = _values(SperLBDData, "LBD")
    inducer = _values(SperLBDData, "inducer")
    baseline = _values(SperLBDData, "I0", I0_val)
    maximum = _values(SperLBDData, "Imax", Imax_val)
    kd = _values(SperLBDData, "kd")
    target = _values(SperLBDData, "RPU")

    net = Energy()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    best_loss = float("inf")
    best = None

    for _ in range(50000):
        optimizer.zero_grad()
        loss = nn.functional.mse_loss(
            net(L, inducer, baseline, maximum, kd), target
        )
        if not torch.isfinite(loss):
            raise ValueError(f"DiffLBD fitting failed for {LBDName}")
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            net.k1.clamp_(min=1e-12, max=1)
            net.k2.clamp_(min=1e-12, max=10000)
            net.k3.clamp_(min=1e-12, max=10000)
            current_loss = loss.item()
            if current_loss < best_loss:
                best_loss = current_loss
                best = (net.k1.item(), net.k2.item(), net.k3.item())

    if best is None:
        raise ValueError(f"DiffLBD fitting returned no result for {LBDName}")
    return list(best)
