#!/usr/bin/env python3
"""Unit tests for utils.memoize"""

import unittest
from unittest.mock import patch
from utils import memoize


class TestMemoize(unittest.TestCase):
    """Test case for memoize decorator"""

    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            obj = TestClass()

            # Call twice
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)

            # Ensure a_method called only once
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
