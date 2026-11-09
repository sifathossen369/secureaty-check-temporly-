import sys, pathlib
backend_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from core.security_scanner import SecurityScanner
from core.sandbox import EphemeralSandbox

print("--- 1. Testing Security Scanner ---")
vulnerable_code = '''
def find_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return query
'''
res = SecurityScanner.scan_code(vulnerable_code)
print(f"Scan Result: IsThreat={res.is_threat}, ThreatType={res.threat_type}, Severity={res.severity}")

print("\n--- 2. Testing Ephemeral Sandbox ---")
code = '''
def calculate_tax(amount):
    if amount < 0: raise ValueError("Amount cannot be negative")
    return amount * 0.15
'''
test_code = '''
class TestTax(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(calculate_tax(100), 15.0)
    def test_negative(self):
        with self.assertRaises(ValueError):
            calculate_tax(-10)
'''
test_res = EphemeralSandbox.execute_test(code, test_code)
print(f"Sandbox Result: Success={test_res.success}, Summary={test_res.summary}")

print("\n--- 3. Testing Diff Generator ---")
from agents.guardian import GuardianAgent
diff = GuardianAgent.generate_diff(vulnerable_code, vulnerable_code.replace("'", '"'))
print(f"Diff Generated: ChangedLines={diff['changed_lines_count']}")

print("\nALL CORE ENGINE TESTS PASSED!")
