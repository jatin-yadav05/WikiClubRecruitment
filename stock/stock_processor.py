"""
Stock processing utilities for inventory management.

This module provides functions to process product stock data,
calculate total inventory value, and identify out-of-stock items.
"""

from typing import List, Tuple, Union, NamedTuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockData(NamedTuple):
    """Represents a product's stock data."""
    product_id: str
    price: Union[float, str]
    stock_quantity: int


class StockResult(NamedTuple):
    """Represents the result of stock processing."""
    total_value: float
    out_of_stock_items: List[str]
    low_stock_items: List[str]
    negative_stock_items: List[str]


def _convert_price_to_float(price: Union[float, str]) -> float:
    """
    Convert price to float, handling both string and numeric inputs.
    
    Args:
        price: The price as either a float or string
        
    Returns:
        float: The price as a float value
        
    Raises:
        ValueError: If the price cannot be converted to a valid float
    """
    try:
        return float(price)
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid price format: {price}")
        raise ValueError(f"Cannot convert price '{price}' to float") from e


def process_stock(
    product_list: List[Tuple[str, Union[float, str], int]]
) -> StockResult:
    """
    Process a list of products to calculate total stock value and identify stock issues.
    
    This function calculates the total value of all products in stock,
    identifies out-of-stock items, low-stock items, and handles negative stock quantities.
    
    Args:
        product_list: List of tuples containing (product_id, price, stock_quantity)
        
    Returns:
        StockResult: Named tuple containing:
            - total_value: Total monetary value of all stock
            - out_of_stock_items: List of product IDs with zero stock
            - low_stock_items: List of product IDs with stock <= 5
            - negative_stock_items: List of product IDs with negative stock
            
    Raises:
        ValueError: If price cannot be converted to float
        TypeError: If input data structure is invalid
        
    Example:
        >>> products = [("p001", 150.00, 5), ("p002", "200.00", 0)]
        >>> result = process_stock(products)
        >>> print(f"Total value: ${result.total_value:.2f}")
        Total value: $750.00
    """
    if not isinstance(product_list, list):
        raise TypeError("product_list must be a list")
    
    total_value: float = 0.0
    out_of_stock_items: List[str] = []
    low_stock_items: List[str] = []
    negative_stock_items: List[str] = []
    
    logger.info(f"Processing {len(product_list)} products")
    
    for i, product in enumerate(product_list):
        try:
            if not isinstance(product, tuple) or len(product) != 3:
                logger.warning(f"Skipping invalid product at index {i}: {product}")
                continue
                
            product_id, price, stock_quantity = product
            
            # Validate product_id
            if not isinstance(product_id, str) or not product_id.strip():
                logger.warning(f"Invalid product ID at index {i}: {product_id}")
                continue
                
            # Validate and convert price
            try:
                price_float = _convert_price_to_float(price)
                if price_float < 0:
                    logger.warning(f"Negative price for {product_id}: {price}")
                    price_float = 0.0
            except ValueError:
                logger.error(f"Skipping product {product_id} due to invalid price: {price}")
                continue
                
            # Validate stock quantity
            if not isinstance(stock_quantity, int):
                logger.warning(f"Invalid stock quantity for {product_id}: {stock_quantity}")
                continue
            
            # Handle negative stock
            if stock_quantity < 0:
                negative_stock_items.append(product_id)
                logger.warning(f"Negative stock quantity for {product_id}: {stock_quantity}")
                # Treat negative stock as zero for value calculation
                effective_stock = 0
            else:
                effective_stock = stock_quantity
            
            # Calculate stock value
            stock_value = price_float * effective_stock
            total_value += stock_value
            
            # Categorize stock status
            if stock_quantity == 0:
                out_of_stock_items.append(product_id)
            elif 0 < stock_quantity <= 5:  # Low stock threshold
                low_stock_items.append(product_id)
                
            logger.debug(f"Processed {product_id}: price={price_float}, "
                        f"stock={stock_quantity}, value={stock_value}")
                        
        except Exception as e:
            logger.error(f"Error processing product at index {i}: {product}. Error: {e}")
            continue
    
    logger.info(f"Processing complete. Total value: ${total_value:.2f}")
    
    return StockResult(
        total_value=round(total_value, 2),
        out_of_stock_items=out_of_stock_items,
        low_stock_items=low_stock_items,
        negative_stock_items=negative_stock_items
    )


# Legacy function name for backward compatibility
def process_stock_legacy(
    product_list: List[Tuple[str, Union[float, str], int]]
) -> Tuple[float, List[str]]:
    """
    Legacy version of process_stock for backward compatibility.
    
    Returns only total_value and out_of_stock_items as in the original function.
    """
    result = process_stock(product_list)
    return result.total_value, result.out_of_stock_items