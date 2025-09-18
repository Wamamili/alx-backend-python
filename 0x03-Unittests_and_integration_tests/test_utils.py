class TestMemoize(unittest.TestCase):
    """Tests for utils.memoize"""

    def test_memoize(self):
        """Test that memoize caches method results and avoids repeated calls"""

        class TestClass:
            """Simple class for testing memoize"""

            def a_method(self):
                """Return fixed value"""
                return 42

            @memoize
            def a_property(self):
                """Return result of a_method with memoization"""
                return self.a_method()

        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_method.assert_called_once()
