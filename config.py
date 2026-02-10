"""Shared config — loads Azure OpenAI creds from .env"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT_URL")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")


def get_client() -> AzureOpenAI:
    """Create client using Entra ID token auth (falls back to API key if set)."""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version=API_VERSION,
    )


def chat(prompt: str, system: str = "You are a helpful AI assistant.", temperature: float = 0.7) -> str:
    """One-shot chat helper — returns the assistant message as a string."""
    client = get_client()
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content
