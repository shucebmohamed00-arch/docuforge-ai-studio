"""
DocuForge AI - Live Multi-Provider LLM Client (Claude Sonnet 5.5 / 4.5, OpenAI, Gemini)
Handles live API calls via httpx, tracks token usage in BudgetEngine, and extracts structured JSON.
"""
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
import httpx

from .settings_manager import SettingsManager
from .budget_engine import BudgetEngine

logger = logging.getLogger("docuforge.llm_client")


class LLMClient:
    """
    Production HTTP client for Anthropic Claude (Sonnet 5.5 / 4.5 / 3.7), OpenAI, and Gemini.
    Automatically records token costs in the $50/month BudgetEngine ledger.
    """

    @classmethod
    def is_live_configured(cls) -> bool:
        s = SettingsManager.get_all(mask_secrets=False)
        provider = s.get("llm_provider", "anthropic")
        if provider == "anthropic" and s.get("anthropic_api_key"):
            return True
        if provider == "openai" and s.get("openai_api_key"):
            return True
        if provider == "gemini" and s.get("gemini_api_key"):
            return True
        # Check any available key
        return bool(s.get("anthropic_api_key") or s.get("openai_api_key") or s.get("gemini_api_key"))

    @classmethod
    def generate(
        cls,
        system_prompt: str,
        user_prompt: str,
        agent_name: str,
        operation: str,
        project_id: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.4
    ) -> Optional[str]:
        """
        Calls the configured live LLM provider and returns the text response.
        Returns None if no API key is configured or if the call fails.
        """
        s = SettingsManager.get_all(mask_secrets=False)
        provider = s.get("llm_provider", "anthropic")

        if provider == "anthropic" or s.get("anthropic_api_key"):
            api_key = s.get("anthropic_api_key")
            if api_key:
                return cls._call_anthropic(
                    api_key=api_key,
                    model=s.get("llm_model", "claude-sonnet-4-5-20250929"),
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    agent_name=agent_name,
                    operation=operation,
                    project_id=project_id,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

        if provider == "openai" or s.get("openai_api_key"):
            api_key = s.get("openai_api_key")
            if api_key:
                return cls._call_openai(
                    api_key=api_key,
                    model="gpt-4o",
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    agent_name=agent_name,
                    operation=operation,
                    project_id=project_id,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

        if provider == "gemini" or s.get("gemini_api_key"):
            api_key = s.get("gemini_api_key")
            if api_key:
                return cls._call_gemini(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    agent_name=agent_name,
                    operation=operation,
                    project_id=project_id
                )

        return None

    @classmethod
    def _call_anthropic(
        cls,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        agent_name: str,
        operation: str,
        project_id: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        """Calls Anthropic Messages API (/v1/messages) with automatic model fallback."""
        candidate_models = [
            model,
            "claude-sonnet-4-5-20250929",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest"
        ]
        # Deduplicate while preserving order
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        for target_model in models_to_try:
            payload = {
                "model": target_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            }
            try:
                with httpx.Client(timeout=90.0) as client:
                    resp = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
                    if resp.status_code == 404 and target_model != models_to_try[-1]:
                        # Try next model identifier if alias not found
                        continue
                    resp.raise_for_status()
                    data = resp.json()

                    content_blocks = data.get("content", [])
                    text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")

                    usage = data.get("usage", {})
                    in_tok = int(usage.get("input_tokens", 1500))
                    out_tok = int(usage.get("output_tokens", 1500))
                    # Claude Sonnet pricing: $3 / 1M input, $15 / 1M output
                    cost = round((in_tok * 0.000003) + (out_tok * 0.000015), 4)

                    BudgetEngine.record_cost(
                        agent_name=agent_name,
                        operation=operation,
                        model_or_service=f"ANTHROPIC_{target_model.upper()}",
                        cost_usd=max(0.001, cost),
                        project_id=project_id,
                        tokens_in=in_tok,
                        tokens_out=out_tok,
                        notes=f"Live Anthropic Claude execution ({target_model})"
                    )
                    return text
            except Exception as e:
                logger.warning("Anthropic API call with model %s failed: %s", target_model, e)
                continue

        return None

    @classmethod
    def _call_openai(
        cls,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        agent_name: str,
        operation: str,
        project_id: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        try:
            with httpx.Client(timeout=90.0) as client:
                resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                in_tok = int(usage.get("prompt_tokens", 1000))
                out_tok = int(usage.get("completion_tokens", 1000))
                cost = round((in_tok * 0.0000025) + (out_tok * 0.00001), 4)
                BudgetEngine.record_cost(
                    agent_name=agent_name,
                    operation=operation,
                    model_or_service=f"OPENAI_{model.upper()}",
                    cost_usd=max(0.001, cost),
                    project_id=project_id,
                    tokens_in=in_tok,
                    tokens_out=out_tok,
                    notes="Live OpenAI execution"
                )
                return text
        except Exception as e:
            logger.warning("OpenAI API call failed: %s", e)
            return None

    @classmethod
    def _call_gemini(
        cls,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
        agent_name: str,
        operation: str,
        project_id: Optional[str]
    ) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]
        }
        try:
            with httpx.Client(timeout=90.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                BudgetEngine.record_cost(
                    agent_name=agent_name,
                    operation=operation,
                    model_or_service="GEMINI_2_5_FLASH",
                    cost_usd=0.005,
                    project_id=project_id,
                    tokens_in=1500,
                    tokens_out=1500,
                    notes="Live Gemini execution"
                )
                return text
        except Exception as e:
            logger.warning("Gemini API call failed: %s", e)
            return None

    @classmethod
    def extract_json(cls, raw_text: Optional[str]) -> Optional[Any]:
        """Extracts and parses JSON object or array from an LLM response."""
        if not raw_text:
            return None
        cleaned = raw_text.strip()
        # Strip markdown code fences if present
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if fence_match:
            cleaned = fence_match.group(1).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Try finding first { or [
            start_obj = cleaned.find("{")
            end_obj = cleaned.rfind("}")
            if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
                try:
                    return json.loads(cleaned[start_obj:end_obj + 1])
                except Exception:
                    pass
            start_arr = cleaned.find("[")
            end_arr = cleaned.rfind("]")
            if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
                try:
                    return json.loads(cleaned[start_arr:end_arr + 1])
                except Exception:
                    pass
        return None
