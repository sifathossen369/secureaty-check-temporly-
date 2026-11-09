"""
NexusCore Production LLM Client
First-class support for Groq API (Llama 3.3 70B Versatile) for ultra-fast, production-grade reasoning.
Also supports Google Gemini and OpenAI as seamless alternatives.
"""

import os
import json
import urllib.request
import urllib.error
import asyncio
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class LLMClient:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Primary Groq Model
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    @classmethod
    def reload_keys(cls):
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        cls.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
        cls.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
        cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
        cls.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    @classmethod
    def is_configured(cls) -> bool:
        cls.reload_keys()
        return bool(cls.GROQ_API_KEY or cls.GEMINI_API_KEY or cls.OPENAI_API_KEY)

    @classmethod
    def get_active_provider(cls) -> str:
        cls.reload_keys()
        if cls.GROQ_API_KEY:
            return f"Groq Cloud ({cls.GROQ_MODEL})"
        if cls.GEMINI_API_KEY:
            return "Google Gemini (gemini-1.5-flash)"
        if cls.OPENAI_API_KEY:
            return "OpenAI (gpt-4o-mini)"
        return "NO_API_KEY_CONFIGURED"

    @classmethod
    async def query(cls, prompt: str, system_instruction: str = "") -> Tuple[Optional[str], int]:
        """
        Async query returning (response_text, token_usage).
        """
        cls.reload_keys()
        return await asyncio.to_thread(cls._sync_query, prompt, system_instruction)

    @classmethod
    def _sync_query(cls, prompt: str, system_instruction: str = "") -> Tuple[Optional[str], int]:
        # 1. Primary: Groq API (High Performance, 300+ tokens/sec)
        if cls.GROQ_API_KEY:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": cls.GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 3000
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {cls.GROQ_API_KEY}"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    usage = data.get("usage", {}).get("total_tokens", 0)
                    if choices:
                        raw_text = choices[0].get("message", {}).get("content", "")
                        return cls._clean_code_fence(raw_text), usage
            except Exception as e:
                print(f"[LLM_CLIENT] Groq API error: {e}")
                # If llama-3.3 failed, attempt fallback to llama-3.1-8b-instant
                try:
                    payload["model"] = "llama-3.1-8b-instant"
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {cls.GROQ_API_KEY}"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        choices = data.get("choices", [])
                        usage = data.get("usage", {}).get("total_tokens", 0)
                        if choices:
                            return cls._clean_code_fence(choices[0].get("message", {}).get("content", "")), usage
                except Exception as fallback_err:
                    print(f"[LLM_CLIENT] Groq fallback error: {fallback_err}")

        # 2. Alternative: Google Gemini
        if cls.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={cls.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 3000}
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    usage = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return cls._clean_code_fence(parts[0].get("text", "")), usage
            except Exception as e:
                print(f"[LLM_CLIENT] Gemini API error: {e}")

        # 3. Alternative: OpenAI
        if cls.OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.1
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {cls.OPENAI_API_KEY}"},
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    usage = data.get("usage", {}).get("total_tokens", 0)
                    if choices:
                        return cls._clean_code_fence(choices[0].get("message", {}).get("content", "")), usage
            except Exception as e:
                print(f"[LLM_CLIENT] OpenAI API error: {e}")

        return None, 0

    @staticmethod
    def _clean_code_fence(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text
