"""
Stock Management Module

This module provides utilities for processing product stock data,
calculating inventory values, and identifying stock status.
"""

from .stock_processor import process_stock, StockData, StockResult

__version__ = "1.0.0"
__all__ = ["process_stock", "StockData", "StockResult"]