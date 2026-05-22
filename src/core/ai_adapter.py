"""
AI Adapter — Gemini support with retries, backoff and robust parsing.
Reads GEMINI_API_KEY, GEMINI_MODEL, GEMINI_API_URL from environment.
Falls back to a local simulation when key is missing or errors persist.
"""
import os
import time
import random
import logging
import json
from typing import Optional
import requests
from requests import Response

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
DEFAULT_API_URL = os.getenv("GEMINI_API_URL", "https://api.gemini.example/v1")

class AIAdapter:
    def __init__(self, provider: str = None, model: Optional[str] = None,
                 api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.provider = provider or os.getenv("AI_PROVIDER", "gemini")
        self.model = model or model or DEFAULT_MODEL
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = api_url or os.getenv("GEMINI_API_URL", DEFAULT_API_URL)
        # Retry/backoff parameters
        self.max_retries = 3
        self.base_backoff = 0.5  # seconds
        logger.info(f"AIAdapter initialized: provider={self.provider} model={self.model}")

    def chat(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2, timeout: int = 15) -> str:
        if self.provider != "gemini":
            logger.warning("Unsupported provider, falling back to simulation")
            return self._simulate_response(prompt)

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set — using simulated response")
            return self._simulate_response(prompt)

        url = f"{self.api_url.rstrip('/')}/chat:generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            try:
                resp: Response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                if resp.status_code == 200:
                    return self._parse_response(resp)
                # Handle rate limiting or server errors with retry/backoff
                if resp.status_code in (429,) or 500 <= resp.status_code < 600:
                    wait = self._backoff_with_jitter(attempt)
                    logger.warning(f"Gemini returned {resp.status_code}, retry {attempt}/{self.max_retries} after {wait:.2f}s")
                    time.sleep(wait)
                    continue
                # Other client errors -> do not retry
                logger.error(f"Gemini API error {resp.status_code}: {resp.text}")
                return f"[Error from Gemini API: {resp.status_code}]"
            except requests.Timeout:
                wait = self._backoff_with_jitter(attempt)
                logger.warning(f"Timeout contacting Gemini, retry {attempt}/{self.max_retries} after {wait:.2f}s")
                time.sleep(wait)
                continue
            except requests.RequestException:
                logger.exception("Network error while contacting Gemini")
                wait = self._backoff_with_jitter(attempt)
                time.sleep(wait)
                continue

        logger.error("Gemini requests exhausted retries — falling back to simulation")
        return self._simulate_response(prompt)

    def _parse_response(self, resp: Response) -> str:
        try:
            data = resp.json()
        except Exception:
            logger.exception("Failed to parse Gemini JSON, returning raw text")
            return resp.text or ""

        # Try common shapes:
        # 1) { "candidates": [ { "content": "..." } ] }
        if isinstance(data, dict):
            candidates = data.get("candidates")
            if isinstance(candidates, list) and candidates:
                first = candidates[0]
                if isinstance(first, dict) and "content" in first:
                    content = first["content"]
                    return self._extract_text(content)
                if isinstance(first, str):
                    return first

            # 2) { "output": { ... } } -> stringify reasonable parts
            output = data.get("output")
            if output:
                # try to extract text in nested formats
                if isinstance(output, dict):
                    # common: output['text'] or output['content']
                    for key in ("text", "content", "message"):
                        if key in output and isinstance(output[key], str):
                            return output[key]
                    # fallback to JSON dump but limited size
                    try:
                        return json.dumps(output)[:4000]
                    except Exception:
                        pass
                else:
                    return str(output)

            # 3) direct text in 'text' or 'reply' fields
            for key in ("text", "reply", "result"):
                if key in data and isinstance(data[key], str):
                    return data[key]

        # fallback
        return resp.text or ""

    def _extract_text(self, content) -> str:
        # content could be structured; extract strings
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            # try common keys
            for k in ("text", "content", "message"):
                v = content.get(k)
                if isinstance(v, str):
                    return v
            # fallback to stringify
            try:
                return json.dumps(content)[:4000]
            except Exception:
                return str(content)
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(self._extract_text(item))
            return "\n".join(parts)[:4000]
        return str(content)

    def _backoff_with_jitter(self, attempt: int) -> float:
        base = self.base_backoff * (2 ** (attempt - 1))
        jitter = random.uniform(0, base * 0.1)
        return base + jitter

    def _simulate_response(self, prompt: str) -> str:
        snippet = prompt.strip()[:200]
        return f"[SIMULATED GEMINI RESPONSE] Обработано: {snippet}"