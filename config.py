"""
Shared config — unified LLM backend with local-first design.

Backend priority:
  1. Ollama (local) — DEFAULT, no API keys needed
  2. Azure OpenAI — if AZURE_OPENAI_ENDPOINT is configured
  3. OpenAI — if OPENAI_API_KEY is configured

Override with LLM_BACKEND=ollama|azure|openai environment variable.
"""

from __future__ import annotations

import os
from typing import Literal

import httpx
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Backend selection: explicit override or auto-detect
LLM_BACKEND: Literal["ollama", "azure", "openai", "auto"] = os.getenv("LLM_BACKEND", "auto").lower()  # type: ignore

# Ollama config (local-first default)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Azure OpenAI config (optional)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("ENDPOINT_URL")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("DEPLOYMENT_NAME", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# OpenAI config (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------


def _ollama_available() -> bool:
    """Check if Ollama is running and responsive."""
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


def _get_backend() -> str:
    """Determine which backend to use based on config and availability."""
    if LLM_BACKEND in ("ollama", "azure", "openai"):
        return LLM_BACKEND
    
    # Auto-detect: prefer local, fall back to cloud
    if _ollama_available():
        return "ollama"
    if AZURE_ENDPOINT:
        return "azure"
    if OPENAI_API_KEY:
        return "openai"
    
    # Default to Ollama even if not running (will error with helpful message)
    return "ollama"


# ---------------------------------------------------------------------------
# Chat implementations
# ---------------------------------------------------------------------------


def _chat_ollama(prompt: str, system: str, temperature: float) -> str:
    """Chat via local Ollama instance."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": temperature},
    }
    
    try:
        resp = httpx.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    except httpx.ConnectError:
        raise ConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}.\n"
            f"Start Ollama with: ollama serve\n"
            f"Pull model with: ollama pull {OLLAMA_MODEL}\n"
            f"Install from: https://ollama.com"
        )


def _chat_azure(prompt: str, system: str, temperature: float) -> str:
    """Chat via Azure OpenAI."""
    try:
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError:
        raise ImportError(
            "Azure backend requires: pip install openai azure-identity"
        )
    
    if not AZURE_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT not configured")
    
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version=AZURE_API_VERSION,
    )
    
    resp = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _chat_openai(prompt: str, system: str, temperature: float) -> str:
    """Chat via OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI backend requires: pip install openai")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def chat(prompt: str, system: str = "You are a helpful AI assistant.", temperature: float = 0.7) -> str:
    """
    One-shot chat helper — returns the assistant message as a string.
    
    Automatically selects backend:
      1. Ollama (local) if available — no API keys needed
      2. Azure OpenAI if AZURE_OPENAI_ENDPOINT configured
      3. OpenAI if OPENAI_API_KEY configured
    
    Override with LLM_BACKEND environment variable.
    """
    backend = _get_backend()
    
    if backend == "ollama":
        return _chat_ollama(prompt, system, temperature)
    elif backend == "azure":
        return _chat_azure(prompt, system, temperature)
    elif backend == "openai":
        return _chat_openai(prompt, system, temperature)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def get_current_backend() -> str:
    """Return the currently active backend name."""
    return _get_backend()


# Legacy alias for backwards compatibility
def get_client():
    """
    Legacy function — returns Azure client if available.
    Prefer using chat() directly for backend-agnostic code.
    """
    backend = _get_backend()
    if backend != "azure":
        raise RuntimeError(
            f"get_client() only works with Azure backend. "
            f"Current backend: {backend}. Use chat() instead."
        )
    
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version=AZURE_API_VERSION,
    )
