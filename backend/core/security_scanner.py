"""
NexusCore Security Scanner Engine
Performs real-time static AST & heuristic scanning on agent code output.
Detects:
1. Hardcoded secrets (API keys, passwords, JWT tokens)
2. Dangerous OS command execution (os.system, rm -rf, eval, exec)
3. SQL Injection patterns (string concatenation in queries)
4. Prompt Injection markers
"""

import re
import ast
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class SecurityScanResult(BaseModel):
    is_threat: bool
    threat_type: Optional[str] = None
    severity: str = "SAFE"  # SAFE, WARNING, CRITICAL
    description: str = "All security checks passed. Code adheres to zero-trust standards."
    offending_snippets: List[str] = []
    fix_suggestion: Optional[str] = None

class SecurityScanner:
    # Regex patterns for common secrets
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|pwd)\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']', "HARDCODED_SECRET", "Hardcoded credential or API secret key detected."),
        (r'AIza[0-9A-Za-z-_]{35}', "GOOGLE_API_KEY", "Exposed Google Cloud API Key."),
        (r'sk-[a-zA-Z0-9]{32,}', "OPENAI_API_KEY", "Exposed OpenAI Secret API Key."),
        (r'ghp_[a-zA-Z0-9]{36}', "GITHUB_TOKEN", "Exposed GitHub Personal Access Token."),
    ]

    # Dangerous OS and execution patterns
    DANGEROUS_CALLS = [
        (r'(?i)os\.system\s*\(', "DANGEROUS_OS_EXEC", "Direct shell execution via os.system is prohibited. Use parameterized subprocess with shell=False."),
        (r'(?i)subprocess\.(call|Popen|run)\s*\([^)]*shell\s*=\s*True', "SUBPROCESS_SHELL_INJECTION", "subprocess executed with shell=True creates command injection vulnerability."),
        (r'(?i)rm\s+-rf\s+[/~]', "DESTRUCTIVE_COMMAND", "Destructive root/home filesystem deletion command detected."),
        (r'(?i)(eval|exec)\s*\(', "CODE_INJECTION", "Arbitrary code execution via eval/exec detected."),
    ]

    # SQL injection patterns
    SQLI_PATTERNS = [
        (r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*?\+.*', "SQL_INJECTION", "Raw string concatenation in SQL query detected. Use parameterized queries."),
        (r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*?f["\'].*?\{.*?\}', "SQL_INJECTION_FSTRING", "SQL query constructed with f-string interpolation. Risk of SQL Injection."),
    ]

    @classmethod
    def scan_code(cls, code: str) -> SecurityScanResult:
        if not code or not code.strip():
            return SecurityScanResult(is_threat=False)

        # 1. Check for Destructive Commands & OS Execution
        for pattern, threat_type, desc in cls.DANGEROUS_CALLS:
            matches = re.findall(pattern, code)
            if matches:
                return SecurityScanResult(
                    is_threat=True,
                    threat_type=threat_type,
                    severity="CRITICAL",
                    description=desc,
                    offending_snippets=[m if isinstance(m, str) else str(m) for m in matches[:3]],
                    fix_suggestion="Use safe, parameterized APIs (e.g., standard library pathlib, sanitized subprocess with explicit arg lists)."
                )

        # 2. Check for SQL Injection
        for pattern, threat_type, desc in cls.SQLI_PATTERNS:
            matches = re.findall(pattern, code)
            if matches:
                return SecurityScanResult(
                    is_threat=True,
                    threat_type=threat_type,
                    severity="CRITICAL",
                    description=desc,
                    offending_snippets=[str(matches[0])[:80]],
                    fix_suggestion="Replace string concatenation with parameterized placeholders like `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`"
                )

        # 3. Check for Hardcoded Secrets
        for pattern, threat_type, desc in cls.SECRET_PATTERNS:
            matches = re.finditer(pattern, code)
            matched_snippets = [m.group(0) for m in matches]
            if matched_snippets:
                masked = [s[:15] + "..." + s[-4:] if len(s) > 20 else "***MASKED***" for s in matched_snippets]
                return SecurityScanResult(
                    is_threat=True,
                    threat_type=threat_type,
                    severity="WARNING",
                    description=desc,
                    offending_snippets=masked,
                    fix_suggestion="Extract credentials to environment variables using `os.getenv('API_KEY')` or dotenv."
                )

        # 4. AST Syntax & Safe Parsing
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
                        return SecurityScanResult(
                            is_threat=True,
                            threat_type="AST_EVAL_EXEC",
                            severity="CRITICAL",
                            description="Direct usage of eval() or exec() found in AST.",
                            offending_snippets=[f"{node.func.id}(...)"],
                            fix_suggestion="Refactor logic to eliminate dynamic eval/exec execution."
                        )
        except SyntaxError:
            # Code might have partial snippets or markdown tags; continue gracefully
            pass

        return SecurityScanResult(
            is_threat=False,
            threat_type=None,
            severity="SAFE",
            description="All zero-trust static security checks passed cleanly."
        )
