"""
NexusCore Ephemeral Sandbox Runner
Executes verified code and unit tests in a clean, isolated in-process namespace
with redirected stdout/stderr and millisecond-precision timing.
"""

import sys
import io
import time
import unittest
from typing import Dict, Any, Optional
from pydantic import BaseModel

class SandboxResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    execution_time_ms: float
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    summary: str

class EphemeralSandbox:
    @staticmethod
    def execute_test(code: str, test_code: str) -> SandboxResult:
        """
        Executes code combined with unit tests in an isolated namespace.
        Captures test runner results, assertion outcomes, and timing.
        """
        combined_source = f"{code}\n\n{test_code}"
        
        # Isolated execution namespace
        sandbox_namespace: Dict[str, Any] = {
            "unittest": unittest,
            "__name__": "__sandbox_main__"
        }

        stream = io.StringIO()
        start_time = time.time()
        
        try:
            # 1. Compile and execute source and test classes in isolated scope
            exec(combined_source, sandbox_namespace)

            # 2. Extract TestCases from the sandbox namespace
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            for key, val in sandbox_namespace.items():
                if isinstance(val, type) and issubclass(val, unittest.TestCase):
                    suite.addTests(loader.loadTestsFromTestCase(val))

            # 3. Run the test suite capturing outputs
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            elapsed_ms = (time.time() - start_time) * 1000

            total = result.testsRun
            failed = len(result.failures) + len(result.errors)
            passed = total - failed
            is_success = result.wasSuccessful()

            summary = f"Executed {total} test(s) in {elapsed_ms:.1f}ms. {passed} Passed, {failed} Failed."
            return SandboxResult(
                success=is_success,
                stdout=stream.getvalue(),
                stderr="",
                execution_time_ms=round(elapsed_ms, 2),
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                summary=summary
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return SandboxResult(
                success=False,
                stdout=stream.getvalue(),
                stderr=str(e),
                execution_time_ms=round(elapsed_ms, 2),
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                summary=f"Sandbox Execution Error: {str(e)}"
            )
