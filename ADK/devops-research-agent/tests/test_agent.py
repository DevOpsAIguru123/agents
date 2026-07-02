import unittest

from patterns.simple_tool_calling.agent import calculate


class CalculateToolTests(unittest.TestCase):
    def test_adds_two_numbers(self):
        result = calculate("add", 2, 3)

        self.assertEqual(
            result,
            {
                "status": "success",
                "operation": "add",
                "left": 2,
                "right": 3,
                "result": 5,
            },
        )

    def test_multiplies_two_numbers(self):
        result = calculate("multiply", 4, 5)

        self.assertEqual(
            result,
            {
                "status": "success",
                "operation": "multiply",
                "left": 4,
                "right": 5,
                "result": 20,
            },
        )


if __name__ == "__main__":
    unittest.main()
