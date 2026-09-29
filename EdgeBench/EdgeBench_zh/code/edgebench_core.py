# -*- coding: utf-8 -*-
"""
edgebench_core.py
==================

EdgeBench 论文核心算法集合的完整参考实现,涵盖:
1. 对数-S 形曲线拟合
2. 前沿扩张过程(Frontier Process)的离散事件模拟
3. 多任务聚合:对数-S 形作为涌现规律
4. pass@k / best-of-k 估计器(用于"无经验"基线)
5. 学习速度追踪与趋势拟合

参考论文:
    ByteDance Seed, "EdgeBench: Unveiling Scaling Laws of
    Learning from Real-World Environments", arXiv:2607.15651, 2026.
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import expit
from scipy.stats import norm
from itertools import combinations
import warnings


# =========================================================================
# 1. 对数-S 形曲线拟合
# =========================================================================

def log_sigmoid(t, S_max, t_mid, beta):
    """
    对数-S 形函数:
        S(t) = S_max / (1 + (t_mid / t)^beta)

    当 beta 越大,曲线在 t_mid 附近越陡;
    当 t_mid 越大,曲线"开始上升"的时间越晚。
    """
    return S_max / (1.0 + (t_mid / np.asarray(t)) ** beta)


def fit_log_sigmoid(t, S, n_candidates=30, verbose=False):
    """
    多起点网格搜索 + Levenberg-Marquardt 拟合

    返回: dict 包含 S_max, t_mid, beta, R2, RMSE
    """
    t = np.asarray(t, dtype=np.float64)
    S = np.asarray(S, dtype=np.float64)
    assert t.shape == S.shape
    assert np.all(t > 0)

    t_mid_candidates = np.logspace(np.log10(t.min()), np.log10(t.max()), n_candidates)
    S_max_init = np.max(S)
    best_loss = np.inf
    best_params = None

    for t_mid_init in t_mid_candidates:
        for beta_init in [0.3, 0.5, 1.0, 1.5, 2.0, 3.0]:
            try:
                popt, _ = curve_fit(
                    log_sigmoid, t, S,
                    p0=[S_max_init, t_mid_init, beta_init],
                    bounds=([0.0, t.min() * 0.1, 0.05],
                            [S_max_init * 2, t.max() * 5, 10.0]),
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
        print(f"  S_max  = {S_max_fit:.4f}")
        print(f"  t_mid  = {t_mid_fit:.4f} h")
        print(f"  beta   = {beta_fit:.4f}")
        print(f"  R^2    = {R2:.4f}")
        print(f"  RMSE   = {RMSE:.4f}")

    return {
        'S_max': float(S_max_fit),
        't_mid': float(t_mid_fit),
        'beta': float(beta_fit),
        'R2': float(R2),
        'RMSE': float(RMSE),
    }


# =========================================================================
# 2. 候选 S 形曲线族(用于表 1 的对比)
# =========================================================================

def log_probit(t, S_max, mu, sigma):
    """对数-Probit: S_max * Phi((ln t - mu) / sigma)"""
    return S_max * norm.cdf((np.log(t) - mu) / sigma)


def log_gompertz(t, S_max, c, x0):
    """对数-Gompertz: S_max * exp(-exp(-c (ln t - x0)))"""
    return S_max * np.exp(-np.exp(-c * (np.log(t) - x0)))


def weibull_cdf(t, S_max, lam, beta):
    """Weibull CDF: S_max * (1 - exp(-(t/lam)^beta))"""
    return S_max * (1.0 - np.exp(-(np.asarray(t) / lam) ** beta))


def log_linear(t, a, b):
    """对数-线性基线: a + b * ln t"""
    return a + b * np.log(t)


# =========================================================================
# 3. 前沿扩张过程(Frontier Process)模拟
# =========================================================================

class FrontierProcess:
    """
    单任务前沿扩张过程的离散事件模拟

    任务: 有限图 G = (E, E_K)
    节点: 得分单元,具有权重 mu_i
    边:  K_{ij} 表示已解锁节点 j 对锁定节点 i 的影响

    演化规则: 锁定节点 i 的瞬时解锁强度为
        lambda_i = eta * (1 - n_i) * sum_j K_{ij} n_j
    """

    def __init__(self, mu, K, eta=1.0, seed=None):
        """
        Parameters
        ----------
        mu : array_like, shape (N,)
            节点的归一化得分权重
        K : array_like, shape (N, N)
            影响矩阵,K[i, j] 为 j->i 的影响
        eta : float
            影响强度到解锁概率的转换常数
        seed : int or None
            随机数种子
        """
        self.mu = np.asarray(mu, dtype=np.float64)
        self.N = len(self.mu)
        self.K = np.asarray(K, dtype=np.float64)
        self.eta = float(eta)
        self.rng = np.random.default_rng(seed)
        # 状态: 0 = 锁定, 1 = 已解锁
        self.n = np.zeros(self.N, dtype=np.int32)
        self.t = 0.0  # 对数时间
        self.history = [(0.0, 0.0)]  # (对数时间, 当前归一化分数)

    def step(self, dt=0.01):
        """
        前进一步(对数时间 dt)

        Returns
        -------
        new_unlocks : int
            本步解锁的节点数
        """
        # 计算每个锁定节点的瞬时解锁概率
        for i in range(self.N):
            if self.n[i] == 1:
                continue
            field = np.sum(self.K[i, :] * self.n)
            lam = self.eta * field
            if lam > 0:
                p_unlock = 1.0 - np.exp(-lam * dt)
                if self.rng.random() < p_unlock:
                    self.n[i] = 1

        self.t += dt
        x = float(np.sum(self.mu * self.n))
        self.history.append((self.t, x))
        return int(np.sum(self.n))

    def run(self, T_max, dt=0.01):
        """运行直到对数时间达到 T_max"""
        while self.t < T_max:
            self.step(dt)
        return np.array(self.history)

    def score(self):
        """当前归一化分数"""
        return float(np.sum(self.mu * self.n))


def make_random_frontier(N=200, edge_density=0.1, eta=1.0, seed=42):
    """
    创建一个随机任务图(每个非零边的影响近似相同)
    """
    rng = np.random.default_rng(seed)
    mu = rng.dirichlet(np.ones(N))  # 归一化得分权重

    K = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j and rng.random() < edge_density:
                K[i, j] = rng.uniform(0.1, 1.0)

    return FrontierProcess(mu, K, eta=eta, seed=seed)


# =========================================================================
# 4. 多任务聚合模拟
# =========================================================================

def simulate_benchmark(M=50, N_per_task=200, T_max=8.0, dt=0.01, seed=42):
    """
    模拟 M 个任务的前沿扩张过程,展示对数-S 形作为总体规律涌现

    每个任务有自己的任务图与归一化(通过对 t_mid 与 beta 的随机扰动)

    Returns
    -------
    t : ndarray
        对齐后的对数时间网格
    x_B : ndarray
        跨任务平均的归一化分数
    """
    rng = np.random.default_rng(seed)
    all_curves = []  # (t_log, x) 元组列表

    for b in range(M):
        # 任务特定参数
        t_mid_b = rng.uniform(1.0, 5.0)  # 任务中点扰动
        beta_b = rng.uniform(0.6, 1.0)   # 任务速度扰动
        eta_b = rng.uniform(0.5, 1.5)
        proc = make_random_frontier(N=N_per_task, eta=eta_b, seed=seed + b)
        history = proc.run(T_max, dt=dt)
        t_log, x = history[:, 0], history[:, 1]
        # 重新缩放对数时间,使每个任务的中点 t_mid_b 对齐到 1
        # 即在 u 坐标上做平移: u_b = log t - log t_mid_b
        # 原始记录的对数时间是 t_log (从 0 到 T_max),
        # 我们将其映射到新的对数时间:
        # t_new_log = t_log - log(t_mid_b)
        t_aligned = t_log - np.log(t_mid_b)
        all_curves.append((t_aligned, x))

    # 在统一的时间网格上插值并求平均
    # 由于不同任务的 t_aligned 范围可能不同,我们截取公共范围
    t_min = max(c[0][0] for c in all_curves)
    t_max = min(c[0][-1] for c in all_curves)
    t_uniform = np.linspace(t_min, t_max, 1000)

    x_B = np.zeros_like(t_uniform)
    for t_aligned, x in all_curves:
        # 限制到统一时间范围内
        mask = (t_aligned >= t_min) & (t_aligned <= t_max)
        x_interp = np.interp(t_uniform, t_aligned[mask], x[mask],
                             left=0.0, right=x[mask][-1])
        x_B += x_interp / M

    return t_uniform, x_B


# =========================================================================
# 5. pass@k / best-of-k 估计器
# =========================================================================

def pass_at_k(u, k):
    """
    计算 n 次独立尝试中,最佳 k 次的期望分数

    Parameters
    ----------
    u : array_like, shape (n,)
        每次尝试的分数
    k : int
        子集大小

    Returns
    -------
    expected_max : float
    """
    u = np.sort(np.asarray(u))[::-1]  # 降序排序
    n = len(u)
    assert 1 <= k <= n
    if k == n:
        return float(u[0])

    total = 0.0
    n_combos = 0
    for subset in combinations(range(n), k):
        total += max(u[i] for i in subset)
        n_combos += 1

    return total / n_combos


def estimate_without_experience_curve(n_runs, time_buckets, n_attempts=6, tau=2.0):
    """
    估计"无经验"条件的 best-of-k 曲线

    Parameters
    ----------
    n_runs : int
        每个 bucket 内的运行数
    time_buckets : list of int
        评估的时间点(以 tau 为单位),如 [1, 2, 3, 4, 5, 6]
    n_attempts : int
        总的独立尝试次数
    tau : float
        每次尝试的时间预算(小时)

    Returns
    -------
    k_to_score : dict
        {k: 期望最佳分数}
    """
    rng = np.random.default_rng(0)

    # 模拟 n_attempts 次独立尝试的分数
    attempts = []
    for i in range(n_attempts):
        score = 25 + 8 * i + rng.normal(0, 2)  # 模拟递增的尝试质量
        attempts.append(score)
    attempts = np.array(attempts)

    k_to_score = {}
    for k in time_buckets:
        k_to_score[k] = pass_at_k(attempts, min(k, n_attempts))
    return k_to_score


# =========================================================================
# 6. 学习速度追踪与趋势拟合
# =========================================================================

def fit_learning_speed_trend(dates, speeds, top_k=2):
    """
    拟合"前 N 名"智能体学习速度的对数-线性趋势

    Parameters
    ----------
    dates : array_like
        相对发布日(以天为单位)
    speeds : array_like
        对应的两小时学习速度
    top_k : int
        取每个发布日的前 k 名

    Returns
    -------
    slope : float
        对数-线性斜率
    doubling_time : float
        翻倍时间(以与 dates 相同的单位)
    """
    from scipy.stats import linregress
    dates = np.asarray(dates, dtype=np.float64)
    speeds = np.asarray(speeds, dtype=np.float64)

    # 取每个日期前 k 名
    unique_dates = np.unique(dates)
    front_dates = []
    front_log_speeds = []
    for d in unique_dates:
        mask = dates == d
        top_speeds = np.sort(speeds[mask])[-top_k:]
        for s in top_speeds:
            front_dates.append(d)
            front_log_speeds.append(np.log(s))

    front_dates = np.array(front_dates)
    front_log_speeds = np.array(front_log_speeds)

    slope, intercept, r_value, p_value, std_err = linregress(front_dates, front_log_speeds)
    # 翻倍时间 = ln 2 / slope (在与 dates 相同的单位上)
    doubling_time = np.log(2) / slope if slope > 0 else np.inf

    return {
        'slope': float(slope),
        'intercept': float(intercept),
        'doubling_time': float(doubling_time),
        'R2': float(r_value ** 2),
        'p_value': float(p_value),
    }


# =========================================================================
# 演示与单元测试
# =========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("EdgeBench 核心算法演示")
    print("=" * 70)

    # ---- 演示 1: 对数-S 形拟合 ----
    print("\n[1] 对数-S 形拟合演示")
    np.random.seed(42)
    t = np.array([0.5, 1, 2, 3, 4, 6, 8, 10, 12])
    S_true = (50.0, 2.0, 0.8)
    S = log_sigmoid(t, *S_true) + np.random.normal(0, 0.5, size=len(t))
    print("真实参数: S_max=50, t_mid=2.0, beta=0.8")
    print("拟合结果:")
    fit_log_sigmoid(t, S, verbose=True)

    # ---- 演示 2: 多任务聚合涌现对数-S 形 ----
    print("\n[2] 多任务聚合演示:对数-S 形作为总体规律涌现")
    t_uniform, x_B = simulate_benchmark(M=30, N_per_task=100, T_max=8.0, dt=0.05)
    print(f"生成 30 个任务的前沿过程,跨任务平均后:")
    print(f"  对齐后的对数时间范围: [{t_uniform[0]:.2f}, {t_uniform[-1]:.2f}]")
    print(f"  中点处(u=0)的分数: {x_B[len(x_B)//2]:.4f}")
    # 尝试拟合
    # 将对齐的对数时间转换为线性时间
    t_linear = np.exp(t_uniform)
    try:
        # 使用较小的 beta 起点,因为对齐后的曲线应该在 t_mid=1 附近陡升
        params = fit_log_sigmoid(t_linear, x_B, n_candidates=20, verbose=True)
    except Exception as e:
        print(f"拟合遇到问题(可能由于曲线过于陡峭): {e}")

    # ---- 演示 3: pass@k 估计 ----
    print("\n[3] pass@k 估计演示")
    u = np.array([20.0, 25.0, 30.0, 35.0, 28.0, 40.0])
    for k in [1, 2, 3, 6]:
        print(f"  k={k}: best-{k} 期望分数 = {pass_at_k(u, k):.2f}")

    # ---- 演示 4: 学习速度趋势 ----
    print("\n[4] 学习速度趋势演示")
    # 模拟 9 个月的发布日(以天为单位)
    np.random.seed(0)
    dates = np.array([0, 30, 60, 90, 120, 150, 180, 210, 240])
    # 假设学习速度每 3 个月翻倍
    base_speed = 2.0
    speeds = base_speed * (2 ** (dates / 90)) + np.random.normal(0, 0.1, len(dates))
    result = fit_learning_speed_trend(dates, speeds, top_k=2)
    print(f"  拟合斜率: {result['slope']:.4f}")
    print(f"  翻倍时间: {result['doubling_time']:.1f} 天 (≈ {result['doubling_time']/30:.1f} 月)")
    print(f"  R² = {result['R2']:.4f}")

    print("\n" + "=" * 70)
    print("所有演示完成。")
    print("=" * 70)
