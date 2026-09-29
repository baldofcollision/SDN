# -*- coding: utf-8 -*-
"""
log_sigmoid_fit.py
==================

对数-S 形曲线拟合:EdgeBench 论文核心算法实现

拟合模型:
    S(t) = S_max / (1 + (t_mid / t)^beta)

参考论文:
    ByteDance Seed, "EdgeBench: Unveiling Scaling Laws of
    Learning from Real-World Environments", arXiv:2607.15651, 2026.
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import expit


def log_sigmoid(t, S_max, t_mid, beta):
    """
    对数-S 形函数(对数时间下的 logistic 形式)

    Parameters
    ----------
    t : array_like
        已用交互时间(小时)
    S_max : float
        可达到的分数上限
    t_mid : float
        达到 S_max/2 的时间
    beta : float
        对数时间下进度集中的陡峭程度

    Returns
    -------
    S : ndarray
        拟合分数
    """
    return S_max / (1.0 + (t_mid / t) ** beta)


def fit_log_sigmoid(t, S, n_candidates=30, verbose=False):
    """
    多起点网格搜索 + 非线性最小二乘拟合对数-S 形曲线

    Parameters
    ----------
    t : array_like, shape (N,)
        时间点
    S : array_like, shape (N,)
        最佳-迄今分数
    n_candidates : int
        t_mid 的候选点数量
    verbose : bool
        是否打印拟合细节

    Returns
    -------
    params : dict
        拟合参数 {'S_max', 't_mid', 'beta', 'R2', 'RMSE'}
    """
    t = np.asarray(t, dtype=np.float64)
    S = np.asarray(S, dtype=np.float64)
    assert t.shape == S.shape, "t 与 S 必须同形状"
    assert np.all(t > 0), "所有时间点必须为正"
    assert np.all(np.diff(t) > 0), "时间点必须严格递增"

    # 排除 t<=0 边界,聚焦对数时间下的主曲线
    valid = (t > 0) & np.isfinite(S)
    t, S = t[valid], S[valid]

    # 候选 t_mid 值
    t_mid_candidates = np.logspace(np.log10(t.min()), np.log10(t.max()), n_candidates)
    S_max_init = np.max(S)

    best_loss = np.inf
    best_params = None

    for t_mid_init in t_mid_candidates:
        # 多组初始值,提高稳健性
        for beta_init in [0.3, 0.5, 1.0, 1.5, 2.0, 3.0]:
            try:
                popt, _ = curve_fit(
                    log_sigmoid,
                    t, S,
                    p0=[S_max_init, t_mid_init, beta_init],
                    bounds=([0.0, t.min() * 0.1, 0.05], [S_max_init * 2, t.max() * 5, 10.0]),
                    maxfev=10000,
                )
                residuals = S - log_sigmoid(t, *popt)
                loss = np.sum(residuals ** 2)
                if loss < best_loss:
                    best_loss = loss
                    best_params = popt
            except (RuntimeError, ValueError):
                continue

    S_max_fit, t_mid_fit, beta_fit = best_params
    residuals = S - log_sigmoid(t, S_max_fit, t_mid_fit, beta_fit)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((S - S.mean()) ** 2)
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    RMSE = np.sqrt(ss_res / len(S))

    if verbose:
        print(f"S_max  = {S_max_fit:.4f}")
        print(f"t_mid  = {t_mid_fit:.4f} h")
        print(f"beta   = {beta_fit:.4f}")
        print(f"R2     = {R2:.4f}")
        print(f"RMSE   = {RMSE:.4f}")

    return {
        'S_max': float(S_max_fit),
        't_mid': float(t_mid_fit),
        'beta': float(beta_fit),
        'R2': float(R2),
        'RMSE': float(RMSE),
    }


# =========================================================================
# 单元测试
# =========================================================================
if __name__ == "__main__":
    # 模拟一条对数-S 形学习曲线
    np.random.seed(42)
    t = np.array([0.5, 1, 2, 3, 4, 6, 8, 10, 12])  # 小时
    S_true_params = (S_max_true, t_mid_true, beta_true) = (50.0, 2.0, 0.8)
    S_clean = log_sigmoid(t, *S_true_params)
    noise = np.random.normal(0, 0.5, size=len(t))
    S = S_clean + noise  # 添加少量噪声

    print("=== 拟合测试 ===")
    params = fit_log_sigmoid(t, S, verbose=True)
    print(f"\n真实参数: S_max={S_max_true}, t_mid={t_mid_true}, beta={beta_true}")
    print(f"拟合参数: S_max={params['S_max']:.2f}, t_mid={params['t_mid']:.2f}, beta={params['beta']:.2f}")
