import pandas as pd
import numpy as np
import pytest

from stockpyl import loss_functions


def test_normal_loss_df():
    """RED test: DataFrame input to normal_loss_df should match scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 60.0, 10.5],
        'mean': [15.0, 50.0, 12.0],
        'sd': [3.0, 8.0, 2.5]
    })

    # Expected results using the existing scalar function
    expected = df.apply(lambda r: loss_functions.normal_loss(r['x'], r['mean'], r['sd']), axis=1)
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    # Import wrapper (should be implemented in src/stockpyl/pandas_utils.py)
    from stockpyl.pandas_utils import normal_loss_df

    result = normal_loss_df(df, x_col='x', mean_col='mean', sd_col='sd', n_col='n', n_bar_col='n_bar')

    # Compare numeric equality with tolerance
    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_economic_order_quantity_df():
    """RED test: DataFrame input to economic_order_quantity_df should match scalar outputs."""
    df = pd.DataFrame({
        'fixed_cost': [8.0, 10.0],
        'holding_cost': [0.225, 0.5],
        'demand_rate': [1300.0, 500.0],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.eoq', fromlist=['economic_order_quantity']).economic_order_quantity(
            r['fixed_cost'], r['holding_cost'], r['demand_rate']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['order_quantity', 'cost'])

    from stockpyl.pandas_utils import economic_order_quantity_df

    result = economic_order_quantity_df(df)

    assert np.allclose(result['order_quantity'].values, expected_df['order_quantity'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)


def test_newsvendor_normal_df():
    """Test DataFrame input for newsvendor_normal_df against scalar outputs."""
    df = pd.DataFrame({
        'holding_cost': [0.18, 0.25],
        'stockout_cost': [0.70, 1.0],
        'demand_mean': [50.0, 100.0],
        'demand_sd': [8.0, 12.0],
        'lead_time': [0, 1],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.newsvendor', fromlist=['newsvendor_normal']).newsvendor_normal(
            r['holding_cost'], r['stockout_cost'], r['demand_mean'], r['demand_sd'], lead_time=r['lead_time']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['base_stock_level', 'cost'])

    from stockpyl.pandas_utils import newsvendor_normal_df

    result = newsvendor_normal_df(df)

    assert np.allclose(result['base_stock_level'].values, expected_df['base_stock_level'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)


def test_poisson_loss_df():
    """Test DataFrame input for poisson_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 10.0],
        'mean': [15.0, 20.0],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['poisson_loss']).poisson_loss(
            r['x'], r['mean']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import poisson_loss_df

    result = poisson_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_newsvendor_poisson_df():
    """Test DataFrame input for newsvendor_poisson_df against scalar outputs."""
    df = pd.DataFrame({
        'holding_cost': [0.18, 0.20],
        'stockout_cost': [0.70, 0.50],
        'demand_mean': [50.0, 30.0],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.newsvendor', fromlist=['newsvendor_poisson']).newsvendor_poisson(
            r['holding_cost'], r['stockout_cost'], r['demand_mean']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['base_stock_level', 'cost'])

    from stockpyl.pandas_utils import newsvendor_poisson_df

    result = newsvendor_poisson_df(df)

    assert np.allclose(result['base_stock_level'].values, expected_df['base_stock_level'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)


def test_normal_second_loss_df():
    """Test DataFrame input for normal_second_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 60.0],
        'mean': [15.0, 50.0],
        'sd': [3.0, 8.0]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['normal_second_loss']).normal_second_loss(
            r['x'], r['mean'], r['sd']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n2', 'n2_bar'])

    from stockpyl.pandas_utils import normal_second_loss_df

    result = normal_second_loss_df(df)

    assert np.allclose(result['n2'].values, expected_df['n2'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n2_bar'].values, expected_df['n2_bar'].values, rtol=1e-9, atol=0)


def test_lognormal_loss_df():
    """Test DataFrame input for lognormal_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 60.0],
        'mu': [2.5, 4.0],
        'sigma': [0.5, 0.8]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['lognormal_loss']).lognormal_loss(
            r['x'], r['mu'], r['sigma']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import lognormal_loss_df

    result = lognormal_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_gamma_loss_df():
    """Test DataFrame input for gamma_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 60.0],
        'a': [10.0, 25.0],
        'b': [2.0, 3.0]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['gamma_loss']).gamma_loss(
            r['x'], r['a'], r['b']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import gamma_loss_df

    result = gamma_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_exponential_loss_df():
    """Test DataFrame input for exponential_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [18.0, 60.0],
        'mu': [0.1, 0.05]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['exponential_loss']).exponential_loss(
            r['x'], r['mu']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import exponential_loss_df

    result = exponential_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_uniform_loss_df():
    """Test DataFrame input for uniform_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [5.0, 15.0],
        'a': [0.0, 10.0],
        'b': [10.0, 20.0]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['uniform_loss']).uniform_loss(
            r['x'], r['a'], r['b']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import uniform_loss_df

    result = uniform_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_geometric_loss_df():
    """Test DataFrame input for geometric_loss_df against scalar outputs."""
    df = pd.DataFrame({
        'x': [5.0, 10.0],
        'p': [0.2, 0.3]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.loss_functions', fromlist=['geometric_loss']).geometric_loss(
            r['x'], r['p']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['n', 'n_bar'])

    from stockpyl.pandas_utils import geometric_loss_df

    result = geometric_loss_df(df)

    assert np.allclose(result['n'].values, expected_df['n'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['n_bar'].values, expected_df['n_bar'].values, rtol=1e-9, atol=0)


def test_economic_production_quantity_df():
    """Test DataFrame input for economic_production_quantity_df against scalar outputs."""
    df = pd.DataFrame({
        'fixed_cost': [8.0, 10.0],
        'holding_cost': [0.225, 0.5],
        'demand_rate': [1300.0, 500.0],
        'production_rate': [2000.0, 800.0]
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.eoq', fromlist=['economic_production_quantity']).economic_production_quantity(
            r['fixed_cost'], r['holding_cost'], r['demand_rate'], r['production_rate']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['order_quantity', 'cost'])

    from stockpyl.pandas_utils import economic_production_quantity_df

    result = economic_production_quantity_df(df)

    assert np.allclose(result['order_quantity'].values, expected_df['order_quantity'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)


def test_economic_order_quantity_with_backorders_df():
    """Test DataFrame input for economic_order_quantity_with_backorders_df against scalar outputs."""
    df = pd.DataFrame({
        'fixed_cost': [8.0, 10.0],
        'holding_cost': [0.225, 0.5],
        'stockout_cost': [0.5, 1.0],
        'demand_rate': [1300.0, 500.0],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.eoq', fromlist=['economic_order_quantity_with_backorders']).economic_order_quantity_with_backorders(
            r['fixed_cost'], r['holding_cost'], r['stockout_cost'], r['demand_rate']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['order_quantity', 'stockout_fraction', 'cost'])

    from stockpyl.pandas_utils import economic_order_quantity_with_backorders_df

    result = economic_order_quantity_with_backorders_df(df)

    assert np.allclose(result['order_quantity'].values, expected_df['order_quantity'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['stockout_fraction'].values, expected_df['stockout_fraction'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)


def test_myopic_df():
    """Test DataFrame input for myopic_df against scalar outputs."""
    df = pd.DataFrame({
        'holding_cost': [0.18, 0.25],
        'stockout_cost': [0.70, 1.0],
        'purchase_cost': [1.0, 1.5],
        'purchase_cost_next_per': [1.0, 1.4],
        'demand_mean': [50.0, 100.0],
        'demand_sd': [8.0, 12.0],
        'discount_factor': [0.95, 0.9],
    })

    expected = df.apply(
        lambda r: __import__('stockpyl.newsvendor', fromlist=['myopic']).myopic(
            r['holding_cost'], r['stockout_cost'], r['purchase_cost'], r['purchase_cost_next_per'],
            r['demand_mean'], r['demand_sd'], r['discount_factor']),
        axis=1,
    )
    expected_df = pd.DataFrame(list(expected), index=df.index, columns=['base_stock_level', 'cost'])

    from stockpyl.pandas_utils import myopic_df

    result = myopic_df(df)

    assert np.allclose(result['base_stock_level'].values, expected_df['base_stock_level'].values, rtol=1e-9, atol=0)
    assert np.allclose(result['cost'].values, expected_df['cost'].values, rtol=1e-9, atol=0)
