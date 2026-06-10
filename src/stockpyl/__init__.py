# Optional pandas integration
try:
    from stockpyl import pandas_utils
except ImportError:
    # pandas is optional; users without it can still use stockpyl
    pandas_utils = None
