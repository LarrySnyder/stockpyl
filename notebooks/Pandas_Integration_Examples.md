# Pandas Integration Usage Examples for Stockpyl

This document provides comprehensive examples of using the new pandas DataFrame wrappers in Stockpyl for batch inventory optimization.

## Setup

```python
import numpy as np
import pandas as pd
import time
from stockpyl import pandas_utils
```

## Basic Usage Examples

### Newsvendor Problems

```python
# Create DataFrame with multiple newsvendor scenarios
df_nv = pd.DataFrame({
    'holding_cost': [2, 3, 1.5, 4],
    'stockout_cost': [18, 25, 12, 30],
    'demand_mean': [120, 100, 80, 150],
    'demand_sd': [10, 15, 8, 20]
})

print("Input scenarios:")
print(df_nv)

# Solve all scenarios at once
results_nv = pandas_utils.newsvendor_normal_df(df_nv)
print("\nResults:")
print(results_nv)
```

### Loss Functions

```python
# Normal loss functions
df_loss = pd.DataFrame({
    'x': [100, 120, 80, 95],
    'mean': [110, 115, 85, 100],
    'sd': [10, 12, 9, 15]
})

loss_results = pandas_utils.normal_loss_df(df_loss)
print("Normal loss results:")
print(loss_results)

# Poisson loss functions
df_poisson = pd.DataFrame({
    'x': [5, 8, 3, 10],
    'mean': [6, 7, 4, 9]
})

poisson_results = pandas_utils.poisson_loss_df(df_poisson)
print("\nPoisson loss results:")
print(poisson_results)
```

### Economic Order Quantity

```python
df_eoq = pd.DataFrame({
    'fixed_cost': [100, 150, 80, 200],
    'holding_cost': [2, 2.5, 1.8, 3],
    'demand_rate': [1000, 800, 1200, 600]
})

eoq_results = pandas_utils.economic_order_quantity_df(df_eoq)
print("EOQ results:")
print(eoq_results)
```

## Advanced Examples

### Parameter Sweeps

```python
# Create parameter sweep for newsvendor problem
holding_costs = np.linspace(1, 5, 10)
stockout_costs = np.linspace(10, 50, 10)

# Create all combinations
H, P = np.meshgrid(holding_costs, stockout_costs)
df_sweep = pd.DataFrame({
    'holding_cost': H.flatten(),
    'stockout_cost': P.flatten(),
    'demand_mean': 100,
    'demand_sd': 15
})

sweep_results = pandas_utils.newsvendor_normal_df(df_sweep)
print(f"Parameter sweep completed for {len(df_sweep)} scenarios")
print("Sample results:")
print(sweep_results.head())
```

### Mixed Distribution Analysis

```python
# Compare different demand distributions
n_scenarios = 100
np.random.seed(42)

df_mixed = pd.DataFrame({
    'scenario_id': range(n_scenarios),
    'demand_type': np.random.choice(['normal', 'poisson', 'gamma'], n_scenarios),
    'mean': np.random.uniform(50, 200, n_scenarios),
    'sd': np.random.uniform(5, 30, n_scenarios),
    'holding_cost': np.random.uniform(1, 5, n_scenarios),
    'stockout_cost': np.random.uniform(10, 50, n_scenarios)
})

# For normal distributions
mask_normal = df_mixed['demand_type'] == 'normal'
if mask_normal.any():
    df_normal_subset = df_mixed[mask_normal][['holding_cost', 'stockout_cost', 'mean', 'sd']]
    normal_results = pandas_utils.newsvendor_normal_df(df_normal_subset)
    df_mixed.loc[mask_normal, 'optimal_stock'] = normal_results['base_stock_level'].values
    df_mixed.loc[mask_normal, 'expected_cost'] = normal_results['cost'].values

print("Mixed distribution analysis results:")
print(df_mixed.head())
```

## Performance Benchmarks

### Large Dataset Performance

```python
# Generate large dataset
n_large = 50000
np.random.seed(123)

df_large = pd.DataFrame({
    'holding_cost': np.random.uniform(1, 5, n_large),
    'stockout_cost': np.random.uniform(10, 50, n_large),
    'demand_mean': np.random.uniform(50, 200, n_large),
    'demand_sd': np.random.uniform(5, 30, n_large)
})

print(f"Testing performance on {n_large} scenarios...")

# Time the DataFrame approach
start_time = time.time()
large_results = pandas_utils.newsvendor_normal_df(df_large)
df_time = time.time() - start_time

print(".2f")
print(".2f")

# Compare with apply approach (much slower)
def scalar_newsvendor(row):
    from stockpyl.newsvendor import newsvendor_normal
    return newsvendor_normal(
        holding_cost=row['holding_cost'],
        stockout_cost=row['stockout_cost'],
        demand_mean=row['demand_mean'],
        demand_sd=row['demand_sd']
    )

start_time = time.time()
apply_results = df_large.apply(scalar_newsvendor, axis=1, result_type='expand')
apply_results.columns = ['base_stock_level', 'cost']
apply_time = time.time() - start_time

print(".2f")
print(".1f")
```

### Memory Efficiency

```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

# Test memory usage scaling
sizes = [1000, 10000, 50000, 100000]

for n in sizes:
    df_test = pd.DataFrame({
        'holding_cost': np.random.uniform(1, 5, n),
        'stockout_cost': np.random.uniform(10, 50, n),
        'demand_mean': np.random.uniform(50, 200, n),
        'demand_sd': np.random.uniform(5, 30, n)
    })

    mem_before = get_memory_usage()
    results = pandas_utils.newsvendor_normal_df(df_test)
    mem_after = get_memory_usage()

    print(f"Size {n}: Memory usage {mem_after - mem_before:.1f} MB")
```

## Integration with Existing Workflows

### Combining with Simulation

```python
# Example: Use DataFrame optimization results in simulation
from stockpyl.sim import simulation

# Optimize base stock levels for multiple products
products_df = pd.DataFrame({
    'product_id': ['A', 'B', 'C'],
    'holding_cost': [2, 3, 1.5],
    'stockout_cost': [18, 25, 12],
    'demand_mean': [120, 100, 80],
    'demand_sd': [10, 15, 8]
})

opt_results = pandas_utils.newsvendor_normal_df(products_df)

# Create supply chain network for simulation
network = {
    'nodes': [
        {'name': 'supplier', 'initial_inventory': 1000},
        {'name': 'retailer', 'initial_inventory': opt_results.loc[0, 'base_stock_level']}
    ],
    'edges': [('supplier', 'retailer')]
}

# Run simulation with optimized inventory levels
sim_results = simulation.single_period_simulation(
    network=network,
    demand_distribution='normal',
    demand_params={'mean': 120, 'sd': 10},
    num_periods=100
)

print("Simulation results with optimized inventory:")
print(f"Average inventory level: {sim_results['avg_inventory']:.1f}")
print(f"Stockout probability: {sim_results['stockout_prob']:.3f}")
```

### Exporting Results

```python
# Save results to various formats
results_df = pandas_utils.newsvendor_normal_df(df_large.head(1000))

# To CSV
results_df.to_csv('optimization_results.csv', index=False)

# To Excel
results_df.to_excel('optimization_results.xlsx', index=False)

# To JSON
results_df.to_json('optimization_results.json', orient='records')

print("Results exported to multiple formats")
```

## Error Handling and Validation

```python
# Test error handling
try:
    # Invalid input (negative holding cost)
    bad_df = pd.DataFrame({
        'holding_cost': [-1, 2],
        'stockout_cost': [10, 15],
        'demand_mean': [100, 120],
        'demand_sd': [10, 12]
    })
    pandas_utils.newsvendor_normal_df(bad_df)
except ValueError as e:
    print(f"Caught expected error: {e}")

# Test missing columns
try:
    incomplete_df = pd.DataFrame({
        'holding_cost': [2, 3],
        'stockout_cost': [10, 15]
        # Missing demand_mean and demand_sd
    })
    pandas_utils.newsvendor_normal_df(incomplete_df)
except KeyError as e:
    print(f"Caught expected error: {e}")
```

## Best Practices

1. **Use vectorized operations**: Always prefer DataFrame wrappers over apply() for performance
2. **Validate inputs**: Check data types and ranges before processing large datasets
3. **Batch processing**: Group similar scenarios together for efficient processing
4. **Memory management**: For very large datasets (>1M rows), consider chunking
5. **Result storage**: Save results to disk for large computations to avoid memory issues

## Available Functions

The following DataFrame wrapper functions are available in `stockpyl.pandas_utils`:

### Loss Functions
- `normal_loss_df()` - Normal distribution loss functions
- `poisson_loss_df()` - Poisson distribution loss functions
- `normal_second_loss_df()` - Normal second-order loss functions
- `lognormal_loss_df()` - Lognormal distribution loss functions
- `gamma_loss_df()` - Gamma distribution loss functions
- `exponential_loss_df()` - Exponential distribution loss functions
- `uniform_loss_df()` - Uniform distribution loss functions
- `geometric_loss_df()` - Geometric distribution loss functions

### EOQ Functions
- `economic_order_quantity_df()` - Economic Order Quantity
- `economic_production_quantity_df()` - Economic Production Quantity
- `economic_order_quantity_with_backorders_df()` - EOQ with backorders

### Newsvendor Functions
- `newsvendor_normal_df()` - Newsvendor with normal demand
- `newsvendor_poisson_df()` - Newsvendor with Poisson demand
- `myopic_df()` - Myopic inventory optimization

All functions maintain identical APIs and results to their scalar counterparts while providing significant performance improvements for batch processing.