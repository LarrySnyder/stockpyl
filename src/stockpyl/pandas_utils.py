"""Pandas DataFrame wrappers for selected stockpyl functions.

This module provides additive, non-breaking wrappers that accept pandas
DataFrames and return DataFrames. Wrappers call existing scalar functions
in `stockpyl` only when necessary, but the implementations here are fully
vectorized for large DataFrames.
"""

try:
    import numpy as np
    import pandas as pd
except ImportError:
    raise ImportError(
        "pandas and numpy are required to use stockpyl.pandas_utils. "
        "Install them with: pip install pandas numpy"
    )

from scipy.stats import norm, poisson

from stockpyl import eoq
from stockpyl import loss_functions
from stockpyl import newsvendor


def normal_loss_df(df: pd.DataFrame,
                   x_col: str = 'x',
                   mean_col: str = 'mean',
                   sd_col: str = 'sd',
                   n_col: str = 'n',
                   n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute normal loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x``, ``mean``, and ``sd``.
    x_col, mean_col, sd_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, mean_col, sd_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    mean = df[mean_col].astype(float)
    sd = df[sd_col].astype(float)

    if (sd <= 0).any():
        raise ValueError("demand_sd must be positive")

    z = (x - mean) / sd
    L = norm.pdf(z) - z * (1 - norm.cdf(z))
    L_bar = z + L

    out = pd.DataFrame({
        n_col: sd * L,
        n_bar_col: sd * L_bar,
    }, index=df.index)

    return out


def poisson_loss_df(df: pd.DataFrame,
                    x_col: str = 'x',
                    mean_col: str = 'mean',
                    n_col: str = 'n',
                    n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute Poisson loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x`` and ``mean``.
    x_col, mean_col : str
        Column names for the inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, mean_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    mean = df[mean_col].astype(float)

    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(mean)):
        raise ValueError("x and mean must be finite numbers")

    if not np.all(np.isclose(x, np.floor(x))):
        raise ValueError("x must be integer-valued")

    pmf = poisson.pmf(x, mean)
    cdf = poisson.cdf(x, mean)

    out = pd.DataFrame({
        n_col: -(x - mean) * (1 - cdf) + mean * pmf,
        n_bar_col: (x - mean) * cdf + mean * pmf,
    }, index=df.index)

    return out


def economic_order_quantity_df(df: pd.DataFrame,
                               fixed_cost_col: str = 'fixed_cost',
                               holding_cost_col: str = 'holding_cost',
                               demand_rate_col: str = 'demand_rate',
                               order_quantity_col: str = 'order_quantity',
                               q_col: str = 'order_quantity',
                               cost_col: str = 'cost') -> pd.DataFrame:
    """Compute EOQ and cost for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``fixed_cost``, ``holding_cost``,
        and ``demand_rate``. ``order_quantity`` is optional and used for cost
        evaluation if present.
    fixed_cost_col, holding_cost_col, demand_rate_col : str
        Column names for the EOQ inputs.
    order_quantity_col : str
        Column name for an optional order quantity override.
    q_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``q_col`` and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (fixed_cost_col, holding_cost_col, demand_rate_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    fixed_cost = df[fixed_cost_col].astype(float)
    holding_cost = df[holding_cost_col].astype(float)
    demand_rate = df[demand_rate_col].astype(float)

    if (fixed_cost < 0).any():
        raise ValueError("fixed_cost must be non-negative")
    if (holding_cost <= 0).any():
        raise ValueError("holding_cost must be positive")
    if (demand_rate < 0).any():
        raise ValueError("demand_rate must be non-negative")

    order_quantity = np.full(len(df), np.nan)
    if order_quantity_col in df.columns:
        override = df[order_quantity_col].astype(float)
        mask = override.notna()
        if (override[mask] <= 0).any():
            raise ValueError("order_quantity must be positive")
        order_quantity[mask] = override[mask]

    q_opt = np.sqrt(2 * fixed_cost * demand_rate / holding_cost)
    q = np.where(np.isnan(order_quantity), q_opt, order_quantity)

    cost = np.where(
        np.isnan(order_quantity),
        q * holding_cost,
        fixed_cost * demand_rate / q + holding_cost * q / 2,
    )

    out = pd.DataFrame({
        q_col: q,
        cost_col: cost,
    }, index=df.index)

    return out


def newsvendor_normal_df(df: pd.DataFrame,
                         holding_cost_col: str = 'holding_cost',
                         stockout_cost_col: str = 'stockout_cost',
                         demand_mean_col: str = 'demand_mean',
                         demand_sd_col: str = 'demand_sd',
                         lead_time_col: str = 'lead_time',
                         base_stock_level_col: str = 'base_stock_level',
                         base_stock_col: str = 'base_stock_level',
                         cost_col: str = 'cost') -> pd.DataFrame:
    """Compute the newsvendor normal solution and cost for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``holding_cost``, ``stockout_cost``,
        ``demand_mean``, and ``demand_sd``. ``lead_time`` and ``base_stock_level``
        are optional.
    holding_cost_col, stockout_cost_col, demand_mean_col, demand_sd_col : str
        Column names for the inputs.
    lead_time_col : str
        Column name for optional lead time values.
    base_stock_level_col : str
        Column name for optional supplied base-stock levels.
    base_stock_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``base_stock_col`` and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_cols = (holding_cost_col, stockout_cost_col, demand_mean_col, demand_sd_col)
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    holding_cost = df[holding_cost_col].astype(float)
    stockout_cost = df[stockout_cost_col].astype(float)
    demand_mean = df[demand_mean_col].astype(float)
    demand_sd = df[demand_sd_col].astype(float)

    if (holding_cost <= 0).any():
        raise ValueError("holding_cost must be positive")
    if (stockout_cost <= 0).any():
        raise ValueError("stockout_cost must be positive")
    if (demand_mean <= 0).any():
        raise ValueError("demand_mean must be positive")
    if (demand_sd <= 0).any():
        raise ValueError("demand_sd must be positive")

    lead_time = df[lead_time_col].astype(float) if lead_time_col in df.columns else pd.Series(0.0, index=df.index)
    lead_time = lead_time.fillna(0.0)
    ltd_mean = demand_mean * (lead_time + 1)
    ltd_sd = demand_sd * np.sqrt(lead_time + 1)

    alpha = stockout_cost / (stockout_cost + holding_cost)
    z_alpha = norm.ppf(alpha)
    base_stock_opt = norm.ppf(alpha, loc=ltd_mean, scale=ltd_sd)
    cost_opt = (holding_cost + stockout_cost) * norm.pdf(z_alpha) * ltd_sd

    base_stock = base_stock_opt.copy()
    if base_stock_level_col in df.columns:
        base_stock_override = df[base_stock_level_col].astype(float)
        valid_override = base_stock_override.notna()
        if valid_override.any() and (base_stock_override[valid_override] <= 0).any():
            raise ValueError("base_stock_level must be positive")
        base_stock = np.where(valid_override, base_stock_override, base_stock_opt)

    base_stock_df = pd.DataFrame({
        'base_stock_level': base_stock,
        'ltd_mean': ltd_mean,
        'ltd_sd': ltd_sd,
    }, index=df.index)

    loss_results = normal_loss_df(base_stock_df, x_col='base_stock_level', mean_col='ltd_mean', sd_col='ltd_sd', n_col='n', n_bar_col='n_bar')
    cost_override = holding_cost * loss_results['n_bar'] + stockout_cost * loss_results['n']

    cost = np.where(
        base_stock_level_col in df.columns,
        np.where(base_stock_df['base_stock_level'].notna(), cost_override, cost_opt),
        cost_opt,
    )

    out = pd.DataFrame({
        base_stock_col: base_stock,
        cost_col: cost,
    }, index=df.index)

    return out


def newsvendor_poisson_df(df: pd.DataFrame,
                          holding_cost_col: str = 'holding_cost',
                          stockout_cost_col: str = 'stockout_cost',
                          demand_mean_col: str = 'demand_mean',
                          base_stock_level_col: str = 'base_stock_level',
                          base_stock_col: str = 'base_stock_level',
                          cost_col: str = 'cost') -> pd.DataFrame:
    """Compute the newsvendor Poisson solution and cost for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``holding_cost``, ``stockout_cost``,
        and ``demand_mean``. ``base_stock_level`` is optional.
    holding_cost_col, stockout_cost_col, demand_mean_col : str
        Column names for the inputs.
    base_stock_level_col : str
        Column name for optional supplied base-stock levels.
    base_stock_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``base_stock_col`` and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_cols = (holding_cost_col, stockout_cost_col, demand_mean_col)
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    holding_cost = df[holding_cost_col].astype(float)
    stockout_cost = df[stockout_cost_col].astype(float)
    demand_mean = df[demand_mean_col].astype(float)

    if (holding_cost <= 0).any():
        raise ValueError("holding_cost must be positive")
    if (stockout_cost <= 0).any():
        raise ValueError("stockout_cost must be positive")
    if (demand_mean <= 0).any():
        raise ValueError("demand_mean must be positive")

    alpha = stockout_cost / (stockout_cost + holding_cost)
    base_stock_opt = poisson.ppf(alpha, demand_mean)

    if base_stock_level_col in df.columns:
        base_stock_override = df[base_stock_level_col].astype(float)
        valid_override = base_stock_override.notna()
        if valid_override.any() and not np.all(np.isclose(base_stock_override[valid_override], np.floor(base_stock_override[valid_override]))):
            raise ValueError("base_stock_level must be integer-valued")
        base_stock = np.where(valid_override, base_stock_override, base_stock_opt)
    else:
        base_stock = base_stock_opt

    loss_results = poisson_loss_df(
        pd.DataFrame({
            'x': base_stock,
            'mean': demand_mean,
        }, index=df.index),
        x_col='x',
        mean_col='mean',
        n_col='n',
        n_bar_col='n_bar',
    )
    cost = holding_cost * loss_results['n_bar'] + stockout_cost * loss_results['n']

    out = pd.DataFrame({
        base_stock_col: base_stock,
        cost_col: cost,
    }, index=df.index)

    return out


def normal_second_loss_df(df: pd.DataFrame,
                          x_col: str = 'x',
                          mean_col: str = 'mean',
                          sd_col: str = 'sd',
                          n2_col: str = 'n2',
                          n2_bar_col: str = 'n2_bar') -> pd.DataFrame:
    """Compute normal second-order loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x``, ``mean``, and ``sd``.
    x_col, mean_col, sd_col : str
        Column names in ``df`` for the respective inputs.
    n2_col, n2_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n2_col`` and ``n2_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, mean_col, sd_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    mean = df[mean_col].astype(float)
    sd = df[sd_col].astype(float)

    if (sd <= 0).any():
        raise ValueError("demand_sd must be positive")

    z = (x - mean) / sd
    L2 = 0.5 * ((z**2 + 1) * (1 - norm.cdf(z)) - z * norm.pdf(z))
    L2_bar = 0.5 * (z**2 + 1) - L2

    out = pd.DataFrame({
        n2_col: sd**2 * L2,
        n2_bar_col: sd**2 * L2_bar,
    }, index=df.index)

    return out


def lognormal_loss_df(df: pd.DataFrame,
                      x_col: str = 'x',
                      mu_col: str = 'mu',
                      sigma_col: str = 'sigma',
                      n_col: str = 'n',
                      n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute lognormal loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x``, ``mu``, and ``sigma``.
    x_col, mu_col, sigma_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, mu_col, sigma_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    mu = df[mu_col].astype(float)
    sigma = df[sigma_col].astype(float)

    if (x <= 0).any():
        raise ValueError("x must be positive")

    E = np.exp(mu + sigma**2 / 2)
    n = E * norm.cdf((mu + sigma**2 - np.log(x)) / sigma) - x * (1 - norm.cdf((np.log(x) - mu) / sigma))
    n_bar = x - E + n

    out = pd.DataFrame({
        n_col: n,
        n_bar_col: n_bar,
    }, index=df.index)

    return out


def gamma_loss_df(df: pd.DataFrame,
                  x_col: str = 'x',
                  a_col: str = 'a',
                  b_col: str = 'b',
                  n_col: str = 'n',
                  n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute gamma loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x``, ``a``, and ``b``.
    x_col, a_col, b_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, a_col, b_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    a = df[a_col].astype(float)
    b = df[b_col].astype(float)

    if (x <= 0).any():
        raise ValueError("x must be positive")

    from scipy.stats import gamma
    f = gamma.pdf(x, a, scale=b)
    F = gamma.cdf(x, a, scale=b)
    E = gamma.mean(a, scale=b)

    n = ((a - x/b) * (1 - F) + x * f) * b
    n_bar = x - E + n

    out = pd.DataFrame({
        n_col: n,
        n_bar_col: n_bar,
    }, index=df.index)

    return out


def exponential_loss_df(df: pd.DataFrame,
                        x_col: str = 'x',
                        mu_col: str = 'mu',
                        n_col: str = 'n',
                        n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute exponential loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x`` and ``mu``.
    x_col, mu_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, mu_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    mu = df[mu_col].astype(float)

    if (x < 0).any():
        raise ValueError("x must be >= 0")

    E = 1.0 / mu
    n = np.exp(-mu * x) / mu
    n_bar = x - E + n

    out = pd.DataFrame({
        n_col: n,
        n_bar_col: n_bar,
    }, index=df.index)

    return out


def uniform_loss_df(df: pd.DataFrame,
                    x_col: str = 'x',
                    a_col: str = 'a',
                    b_col: str = 'b',
                    n_col: str = 'n',
                    n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute uniform loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x``, ``a``, and ``b``.
    x_col, a_col, b_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, a_col, b_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    a = df[a_col].astype(float)
    b = df[b_col].astype(float)

    if ((x < a) | (x > b)).any():
        raise ValueError("x must be >= a and <= b")

    n = (b - x)**2 / (2 * (b - a))
    n_bar = (x - a)**2 / (2 * (b - a))

    out = pd.DataFrame({
        n_col: n,
        n_bar_col: n_bar,
    }, index=df.index)

    return out


def geometric_loss_df(df: pd.DataFrame,
                      x_col: str = 'x',
                      p_col: str = 'p',
                      n_col: str = 'n',
                      n_bar_col: str = 'n_bar') -> pd.DataFrame:
    """Compute geometric loss and complementary loss for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``x`` and ``p``.
    x_col, p_col : str
        Column names in ``df`` for the respective inputs.
    n_col, n_bar_col : str
        Column names to use for the outputs in the returned DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``n_col`` and ``n_bar_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (x_col, p_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    x = df[x_col].astype(float)
    p = df[p_col].astype(float)

    if not np.all(np.isclose(x, np.floor(x))):
        raise ValueError("x must be integer-valued")

    E = 1.0 / p
    n = ((1 - p) / p) * (1 - p)**(x - 1)
    n_bar = x - E + n

    out = pd.DataFrame({
        n_col: n,
        n_bar_col: n_bar,
    }, index=df.index)

    return out


def economic_production_quantity_df(df: pd.DataFrame,
                                    fixed_cost_col: str = 'fixed_cost',
                                    holding_cost_col: str = 'holding_cost',
                                    demand_rate_col: str = 'demand_rate',
                                    production_rate_col: str = 'production_rate',
                                    q_col: str = 'order_quantity',
                                    cost_col: str = 'cost') -> pd.DataFrame:
    """Compute EPQ and cost for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``fixed_cost``, ``holding_cost``,
        ``demand_rate``, and ``production_rate``.
    fixed_cost_col, holding_cost_col, demand_rate_col, production_rate_col : str
        Column names for the inputs.
    q_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``q_col`` and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (fixed_cost_col, holding_cost_col, demand_rate_col, production_rate_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    fixed_cost = df[fixed_cost_col].astype(float)
    holding_cost = df[holding_cost_col].astype(float)
    demand_rate = df[demand_rate_col].astype(float)
    production_rate = df[production_rate_col].astype(float)

    if (fixed_cost < 0).any():
        raise ValueError("fixed_cost must be non-negative")
    if (holding_cost <= 0).any():
        raise ValueError("holding_cost must be positive")
    if (demand_rate < 0).any():
        raise ValueError("demand_rate must be non-negative")
    if (production_rate <= demand_rate).any():
        raise ValueError("production_rate must be > demand_rate")

    q = np.sqrt(2 * fixed_cost * demand_rate / (holding_cost * (1 - demand_rate / production_rate)))
    cost = np.sqrt(2 * fixed_cost * demand_rate * holding_cost * (1 - demand_rate / production_rate))

    out = pd.DataFrame({
        q_col: q,
        cost_col: cost,
    }, index=df.index)

    return out


def economic_order_quantity_with_backorders_df(df: pd.DataFrame,
                                               fixed_cost_col: str = 'fixed_cost',
                                               holding_cost_col: str = 'holding_cost',
                                               stockout_cost_col: str = 'stockout_cost',
                                               demand_rate_col: str = 'demand_rate',
                                               q_col: str = 'order_quantity',
                                               stockout_fraction_col: str = 'stockout_fraction',
                                               cost_col: str = 'cost') -> pd.DataFrame:
    """Compute EOQB for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``fixed_cost``, ``holding_cost``,
        ``stockout_cost``, and ``demand_rate``.
    fixed_cost_col, holding_cost_col, stockout_cost_col, demand_rate_col : str
        Column names for the inputs.
    q_col, stockout_fraction_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and three new columns:
        ``q_col``, ``stockout_fraction_col``, and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (fixed_cost_col, holding_cost_col, stockout_cost_col, demand_rate_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    fixed_cost = df[fixed_cost_col].astype(float)
    holding_cost = df[holding_cost_col].astype(float)
    stockout_cost = df[stockout_cost_col].astype(float)
    demand_rate = df[demand_rate_col].astype(float)

    if (fixed_cost < 0).any():
        raise ValueError("fixed_cost must be non-negative")
    if (holding_cost <= 0).any():
        raise ValueError("holding_cost must be positive")
    if (stockout_cost < 0).any():
        raise ValueError("stockout_cost must be non-negative")
    if (demand_rate < 0).any():
        raise ValueError("demand_rate must be non-negative")

    q = np.sqrt(2 * fixed_cost * demand_rate * (holding_cost + stockout_cost) / (holding_cost * stockout_cost))
    stockout_fraction = holding_cost / (holding_cost + stockout_cost)
    cost = np.sqrt(2 * fixed_cost * demand_rate * holding_cost * stockout_cost / (holding_cost + stockout_cost))

    out = pd.DataFrame({
        q_col: q,
        stockout_fraction_col: stockout_fraction,
        cost_col: cost,
    }, index=df.index)

    return out


def myopic_df(df: pd.DataFrame,
              holding_cost_col: str = 'holding_cost',
              stockout_cost_col: str = 'stockout_cost',
              purchase_cost_col: str = 'purchase_cost',
              purchase_cost_next_per_col: str = 'purchase_cost_next_per',
              demand_mean_col: str = 'demand_mean',
              demand_sd_col: str = 'demand_sd',
              discount_factor_col: str = 'discount_factor',
              base_stock_col: str = 'base_stock_level',
              cost_col: str = 'cost') -> pd.DataFrame:
    """Compute myopic solution for each row in ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns for ``holding_cost``, ``stockout_cost``,
        ``purchase_cost``, ``purchase_cost_next_per``, ``demand_mean``, ``demand_sd``,
        and ``discount_factor``.
    holding_cost_col, stockout_cost_col, purchase_cost_col, purchase_cost_next_per_col, demand_mean_col, demand_sd_col, discount_factor_col : str
        Column names for the inputs.
    base_stock_col, cost_col : str
        Column names for the outputs.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the same index as ``df`` and two new columns:
        ``base_stock_col`` and ``cost_col``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in (holding_cost_col, stockout_cost_col, purchase_cost_col, purchase_cost_next_per_col, demand_mean_col, demand_sd_col, discount_factor_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in DataFrame")

    holding_cost = df[holding_cost_col].astype(float)
    stockout_cost = df[stockout_cost_col].astype(float)
    purchase_cost = df[purchase_cost_col].astype(float)
    purchase_cost_next_per = df[purchase_cost_next_per_col].astype(float)
    demand_mean = df[demand_mean_col].astype(float)
    demand_sd = df[demand_sd_col].astype(float)
    discount_factor = df[discount_factor_col].astype(float)

    c_plus = purchase_cost - discount_factor * purchase_cost_next_per
    if ((c_plus < -holding_cost) | (c_plus > stockout_cost)).any():
        raise ValueError("myopic() requires -h_t <= c_t - gamma * c_{t+1} <= p_t")

    alpha = (stockout_cost - c_plus) / (stockout_cost + holding_cost)
    base_stock = norm.ppf(alpha, loc=demand_mean, scale=demand_sd)

    # Cost calculation: use normal_loss_df to get n and n_bar
    loss_df = pd.DataFrame({
        'x': base_stock,
        'mean': demand_mean,
        'sd': demand_sd,
    }, index=df.index)
    loss_results = normal_loss_df(loss_df, x_col='x', mean_col='mean', sd_col='sd', n_col='n', n_bar_col='n_bar')
    
    g = holding_cost * loss_results['n_bar'] + stockout_cost * loss_results['n']
    cost = purchase_cost * base_stock + g - discount_factor * purchase_cost_next_per * (base_stock - demand_mean)

    out = pd.DataFrame({
        base_stock_col: base_stock,
        cost_col: cost,
    }, index=df.index)

    return out
