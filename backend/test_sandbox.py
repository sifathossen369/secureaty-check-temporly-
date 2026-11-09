from core.sandbox import EphemeralSandbox

code = """
def add(a, b): return a + b
"""

test_code = """
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
"""

res = EphemeralSandbox.execute_test(code, test_code)
print("SUCCESS:", res.success)
print("SUMMARY:", res.summary)
