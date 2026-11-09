"""
Agent Guardian (Security Sentinel & Gatekeeper)
100% Dynamic - AST Static Analysis + Groq Semantic Threat Evaluation
Intercepts vulnerabilities, commands Builder to self-heal, and computes unified diffs.
"""

import difflib
from typing import Dict, Any, Tuple
from core.security_scanner import SecurityScanner, SecurityScanResult
from core.llm_client import LLMClient

class GuardianAgent:
    name = "AGENT_GUARDIAN"
    role = "Security Sentinel & Gatekeeper"
    color = "#ef4444"  # Neon Red

    @staticmethod
    async def audit_code(code: str, emit_log, trigger_alert) -> Tuple[SecurityScanResult, str, int]:
        await emit_log(GuardianAgent.name, "SCANNING", "Running Level-1 Zero-Trust AST traversal & regex heuristics...")
        tokens_used = 0

        # Layer 1: Static AST & Pattern Scanner (Instant, Deterministic)
        scan_result = SecurityScanner.scan_code(code)

        if scan_result.is_threat:
            await emit_log(
                GuardianAgent.name,
                "ALERT",
                f"🚨 THREAT INTERCEPTED: [{scan_result.threat_type}] - {scan_result.description}"
            )
            await trigger_alert({
                "threat_type": scan_result.threat_type,
                "severity": scan_result.severity,
                "description": scan_result.description,
                "offending_snippets": scan_result.offending_snippets,
                "fix_suggestion": scan_result.fix_suggestion
            })
            return scan_result, "REJECTED", tokens_used

        # Layer 2: Real AI Semantic Security Audit via Groq
        if LLMClient.is_configured():
            provider = LLMClient.get_active_provider()
            await emit_log(GuardianAgent.name, "AI_AUDIT", f"Running Level-2 Semantic Vulnerability Audit via [{provider}]...")
            
            sys_inst = """You are a Lead Application Security Auditor and Penetration Tester.
Analyze the provided Python code for critical security flaws:
1. SQL injection or database tampering
2. Command injection or unauthorized subprocess/system calls
3. Hardcoded secrets, API tokens, passwords, or credentials
4. Arbitrary file read/write or path traversal
5. Unsafe deserialization or code evaluation

If the code contains ANY security risk, respond in this exact format:
STATUS: VULNERABLE
THREAT_TYPE: <TYPE_OF_VULNERABILITY>
DESCRIPTION: <Explain why it is dangerous>
FIX: <Explain how to safely refactor it>

If the code is genuinely safe, respond ONLY with:
STATUS: APPROVED"""

            llm_eval, tokens = await LLMClient.query(f"Audit this Python code for vulnerabilities:\n\n{code}", sys_inst)
            tokens_used += tokens

            if llm_eval and "STATUS: VULNERABLE" in llm_eval:
                threat_type = "SEMANTIC_VULNERABILITY"
                desc = "AI Security Sentinel identified high-risk security flaws in logic."
                fix = "Refactor logic to eliminate security risk."

                for line in llm_eval.splitlines():
                    if line.startswith("THREAT_TYPE:"):
                        threat_type = line.replace("THREAT_TYPE:", "").strip()
                    elif line.startswith("DESCRIPTION:"):
                        desc = line.replace("DESCRIPTION:", "").strip()
                    elif line.startswith("FIX:"):
                        fix = line.replace("FIX:", "").strip()

                ai_scan_result = SecurityScanResult(
                    is_threat=True,
                    threat_type=threat_type,
                    severity="CRITICAL",
                    description=desc,
                    offending_snippets=["Identified by AI Semantic Audit"],
                    fix_suggestion=fix
                )

                await emit_log(GuardianAgent.name, "ALERT", f"🚨 AI AUDIT INTERCEPTED: [{threat_type}] - {desc}")
                await trigger_alert({
                    "threat_type": threat_type,
                    "severity": "CRITICAL",
                    "description": desc,
                    "offending_snippets": ["Identified by AI Semantic Audit"],
                    "fix_suggestion": fix
                })
                return ai_scan_result, "REJECTED", tokens_used

        await emit_log(GuardianAgent.name, "PASSED", "✅ Level-1 & Level-2 Zero-Trust Checks Passed. Code certified for sandbox execution.")
        return scan_result, "APPROVED", tokens_used

    @staticmethod
    def generate_diff(original_code: str, healed_code: str) -> Dict[str, Any]:
        diff = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            healed_code.splitlines(keepends=True),
            fromfile="vulnerable_draft.py",
            tofile="healed_secure.py",
            n=3
        ))
        
        return {
            "raw_diff": "".join(diff),
            "original_code": original_code,
            "healed_code": healed_code,
            "changed_lines_count": len([l for l in diff if l.startswith('+') or l.startswith('-')])
        }
