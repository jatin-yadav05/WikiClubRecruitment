"""
Comprehensive test suite for the stock processing module.
"""

import unittest
from typing import List, Tuple, Union
import sys
import os

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock import process_stock, StockResult


class TestStockProcessing(unittest.TestCase):
    """Test cases for stock processing functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_products = [
            ("p001", 150.00, 5),
            ("p002", 200.00, 0),
            ("p003", 50.50, 10),
            ("p004", "99.99", 3),
            ("p005", 300.00, 0),
        ]
    
    def test_basic_stock_processing(self):
        """Test 1: Basic stock processing with valid data."""
        products = [
            ("p001", 100.00, 5),
            ("p002", 50.00, 3),
            ("p003", 200.00, 0),
        ]
        
        result = process_stock(products)
        
        # Expected: (100*5) + (50*3) + (200*0) = 650
        self.assertEqual(result.total_value, 650.00)
        self.assertEqual(result.out_of_stock_items, ["p003"])
        self.assertEqual(result.low_stock_items, ["p002"])
        self.assertEqual(result.negative_stock_items, [])
    
    def test_string_price_conversion(self):
        """Test 2: Handling string prices that need conversion."""
        products = [
            ("p001", "150.50", 4),
            ("p002", "99.99", 2),
            ("p003", 75.25, 6),
        ]
        
        result = process_stock(products)
        
        # Expected: (150.50*4) + (99.99*2) + (75.25*6) = 602 + 199.98 + 451.50 = 1253.48
        expected_value = 150.50 * 4 + 99.99 * 2 + 75.25 * 6
        self.assertAlmostEqual(result.total_value, expected_value, places=2)
        self.assertEqual(result.out_of_stock_items, [])
        self.assertEqual(result.low_stock_items, ["p002"])
    
    def test_negative_stock_handling(self):
        """Test 3: Proper handling of negative stock quantities."""
        products = [
            ("p001", 100.00, -5),  # Negative stock
            ("p002", 50.00, 3),
            ("p003", 200.00, -2),  # Negative stock
        ]
        
        result = process_stock(products)
        
        # Expected: (0) + (50*3) + (0) = 150 (negative stock treated as 0 for value)
        self.assertEqual(result.total_value, 150.00)
        self.assertEqual(result.negative_stock_items, ["p001", "p003"])
        self.assertEqual(result.low_stock_items, ["p002"])
    
    def test_empty_and_edge_cases(self):
        """Test 4: Empty lists and edge cases."""
        # Test empty list
        result = process_stock([])
        self.assertEqual(result.total_value, 0.0)
        self.assertEqual(result.out_of_stock_items, [])
        
        # Test single item
        result = process_stock([("p001", 99.99, 1)])
        self.assertEqual(result.total_value, 99.99)
        self.assertEqual(result.low_stock_items, ["p001"])
        
        # Test zero price
        result = process_stock([("p001", 0.00, 10)])
        self.assertEqual(result.total_value, 0.0)
    
    def test_comprehensive_stock_categories(self):
        """Test 5: Comprehensive test covering all stock categories."""
        products = [
            ("p001", 100.00, 10),  # Normal stock
            ("p002", 50.00, 0),    # Out of stock
            ("p003", 75.00, 3),    # Low stock (≤5)
            ("p004", "200.50", 5), # Low stock boundary (≤5)
            ("p005", 150.00, -3),  # Negative stock
            ("p006", 300.00, 0),   # Another out of stock
            ("p007", 25.25, 15),   # Normal stock
        ]
        
        result = process_stock(products)
        
        # Expected value: 100*10 + 0 + 75*3 + 200.50*5 + 0 + 0 + 25.25*15
        # = 1000 + 0 + 225 + 1002.50 + 0 + 0 + 378.75 = 2606.25
        expected_value = 100*10 + 75*3 + 200.50*5 + 25.25*15
        self.assertAlmostEqual(result.total_value, expected_value, places=2)
        
        # Check categorization
        self.assertCountEqual(result.out_of_stock_items, ["p002", "p006"])
        self.assertCountEqual(result.low_stock_items, ["p003", "p004"])
        self.assertEqual(result.negative_stock_items, ["p005"])
    
    def test_invalid_data_handling(self):
        """Test 6: Handling of invalid data types and malformed input."""
        products = [
            ("p001", 100.00, 5),      # Valid
            ("p002", "invalid", 3),   # Invalid price
            ("p003", 50.00, "text"),  # Invalid quantity - will be skipped
            ("p004", 75.00, 2),       # Valid
        ]
        
        # Should not crash and should process valid items
        try:
            result = process_stock(products)
            # Should process p001 and p004 only
            expected_value = 100.00 * 5 + 75.00 * 2
            self.assertEqual(result.total_value, expected_value)
        except ValueError:
            # If it raises ValueError for invalid price, that's also acceptable
            pass
    
    def test_result_data_structure(self):
        """Test 7: Verify the result data structure and types."""
        products = [("p001", 100.00, 5)]
        result = process_stock(products)
        
        # Check that result is a StockResult named tuple
        self.assertIsInstance(result, StockResult)
        self.assertIsInstance(result.total_value, float)
        self.assertIsInstance(result.out_of_stock_items, list)
        self.assertIsInstance(result.low_stock_items, list)
        self.assertIsInstance(result.negative_stock_items, list)
    
    def test_precision_and_rounding(self):
        """Test 8: Verify proper handling of floating-point precision."""
        products = [
            ("p001", 33.333, 3),
            ("p002", 66.666, 2),
        ]
        
        result = process_stock(products)
        
        # Expected: 33.333*3 + 66.666*2 = 99.999 + 133.332 = 233.331
        # Should be rounded to 2 decimal places
        expected_value = round(33.333 * 3 + 66.666 * 2, 2)
        self.assertEqual(result.total_value, expected_value)


class TestInputValidation(unittest.TestCase):
    """Test input validation and error handling."""
    
    def test_invalid_input_types(self):
        """Test handling of completely invalid input types."""
        with self.assertRaises(TypeError):
            process_stock("not a list")
    
    def test_malformed_tuples(self):
        """Test handling of malformed product tuples."""
        products = [
            ("p001", 100.00),          # Missing stock quantity
            ("p002", 50.00, 5, "extra"), # Extra element
            "not a tuple",             # Not a tuple
        ]
        
        # Should process gracefully and skip invalid items
        result = process_stock(products)
        self.assertEqual(result.total_value, 0.0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)