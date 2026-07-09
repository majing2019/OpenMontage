"""Seedream (Doubao) image generation via Volcengine Ark (火山引擎方舟).

Volcengine Ark hosts ByteDance's Seedream image generation models:
  - doubao-seedream-5-0-260128        (Seedream 5.0)
  - doubao-seedream-5-0-lite-260128   (Seedream 5.0 lite — fast, cost-effective)
  - doubao-seedream-4-5-251128        (Seedream 4.5)
  - doubao-seedream-4-0-250828        (Seedream 4.0)

Uses provider="volcengine" (same platform as seedance_volcengine video tool)
so both surface independently in preflight under the volcengine provider.
Shares the ARK_API_KEY — no additional key needed.

Performance (measured 2026-06-29):
  - Seedream 4.0, 1024² (2K), PNG: ~13s, ~$0.01, ~500KB output
  - Seedream 5.0: estimated 15-30s for 2K
  - Higher resolutions (3K, 4K) take longer (~25s+) and cost more

API docs: https://www.volcengine.com/docs/82379/1541523
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# Bypass system proxy for Volcengine Ark domains — macOS Clash/V2Ray proxy
# (127.0.0.1:7897) causes SSL handshake failures with these endpoints.
_VOLCENGINE_NO_PROXY_HOSTS = "ark.cn-beijing.volces.com,ark-acg-cn-beijing.tos-cn-beijing.volces.com"
for _k in ("NO_PROXY", "no_proxy"):
    _existing = os.environ.get(_k, "")
    if _VOLCENGINE_NO_PROXY_HOSTS not in _existing:
        os.environ[_k] = f"{_VOLCENGINE_NO_PROXY_HOSTS},{_existing}" if _existing else _VOLCENGINE_NO_PROXY_HOSTS

# Volcengine Ark image generation endpoint (synchronous)
_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

# Model IDs
_MODELS = {
    "5_0": "doubao-seedream-5-0-260128",
    "5_0_lite": "doubao-seedream-5-0-lite-260128",
    "4_5": "doubao-seedream-4-5-251128",
    "4_0": "doubao-seedream-4-0-250828",
}

# Approximate token cost per resolution level (CNY per image)
# Billing: output_tokens = sum(width * height) / 256 per image
_COST_PER_LEVEL_CNY = {
    "2K": 0.04,
    "3K": 0.06,
    "4K": 0.08,
}

# Default pixel dimensions for size keywords
_SIZE_DEFAULTS = {
    "2K": "1024x1024",
    "3K": "1536x1536",
    "4K": "2048x2048",
}


def _file_to_data_uri(path: str) -> str:
    """Convert a local image file to a base64 data URI for Volcengine API."""
    p = Path(path)
    suffix = p.suffix.lstrip(".")
    mime = f"image/{suffix.lower()}"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def _guess_extension(data: bytes) -> str:
    """Guess image format from magic bytes."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".png"


class SeedreamVolcengine(BaseTool):
    name = "seedream_volcengine"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "volcengine"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set ARK_API_KEY to your Volcengine Ark API key.\n"
        "  在火山引擎方舟平台获取: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey\n"
        "  账户余额需 >= 200 元才能使用 Seedance 2.0 / Seedream 模型。\n"
        "  同一个 ARK_API_KEY 同时支持视频生成 (Seedance) 和图片生成 (Seedream)。"
    )
    agent_skills = ["volcengine-ark", "flux-best-practices"]

    capabilities = [
        "text_to_image",
        "image_to_image",
        "reference_images",
    ]
    supports = {
        "text_to_image": True,
        "image_to_image": True,
        "reference_images": True,
        "seed": True,
        "custom_size": True,
        "output_format": True,
        "watermark": True,
        "high_resolution": True,
    }
    best_for = [
        "Chinese-language prompts (native Mandarin understanding)",
        "users with Volcengine Ark access (Alipay payment, no international card needed)",
        "high-resolution output up to 4K (2048x2048)",
        "cost-effective image generation via Seedream 5.0 lite",
        "image-to-image with single or multiple reference images",
    ]
    not_good_for = [
        "users without Volcengine Ark account",
        "real-time generation (sync API, ~15-30s per image)",
    ]
    fallback_tools = ["flux_image", "openai_image", "google_imagen", "pexels_image"]
    quality_score = 0.88

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Text prompt describing the desired image. Max 300 Chinese chars or 600 English words.",
            },
            "model_variant": {
                "type": "string",
                "enum": ["5_0", "5_0_lite", "4_5", "4_0"],
                "default": "5_0",
                "description": "Model variant. 5_0 = best quality, 5_0_lite = fast & cheap.",
            },
            "size": {
                "type": "string",
                "description": "Output size: '2K' (1024x1024), '3K' (1536x1536), '4K' (2048x2048), or explicit 'WxH' (total pixels 3686400-16777216).",
                "default": "2K",
            },
            "output_format": {
                "type": "string",
                "enum": ["png", "jpeg"],
                "default": "png",
                "description": "Output image format. Only Seedream 5.0 and 5.0 lite support this.",
            },
            "response_format": {
                "type": "string",
                "enum": ["url", "b64_json"],
                "default": "url",
                "description": "API response format. url = temporary URL (24h expiry), b64_json = base64 data.",
            },
            "seed": {
                "type": "integer",
                "description": "Seed for reproducibility.",
            },
            "watermark": {
                "type": "boolean",
                "default": False,
                "description": "Add AI-generated watermark to image.",
            },
            "image_url": {
                "type": "string",
                "description": "Single reference image URL for image-to-image generation. Mutually exclusive with image_urls.",
            },
            "image_urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Multiple reference image URLs (2-14). Seedream merges features from all references into one image. Use for multi-character anchoring or style+identity fusion.",
            },
            "image_path": {
                "type": "string",
                "description": "Single local reference image path — auto-converted to base64 data URI. Mutually exclusive with image_paths.",
            },
            "image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Multiple local reference image paths (2-14). Auto-converted to base64 data URIs. Use for multi-character anchoring when multiple characters need identity preservation.",
            },
            "output_path": {
                "type": "string",
                "description": "Path to save the generated image. Extension inferred from format if not specified.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "model_variant", "size", "seed"]
    side_effects = [
        "writes image file to output_path",
        "calls Volcengine Ark API",
    ]
    user_visible_verification = [
        "Inspect generated image for prompt adherence, composition, and visual quality",
    ]

    def _get_api_key(self) -> str | None:
        return os.environ.get("ARK_API_KEY")

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._get_api_key() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        size = inputs.get("size", "2K")
        # Resolve keyword sizes
        size_key = size.upper() if size else "2K"
        if size_key not in _COST_PER_LEVEL_CNY:
            # Custom WxH size — estimate from pixel count
            try:
                parts = size.lower().split("x")
                w, h = int(parts[0]), int(parts[1])
                pixels = w * h
                # Approximate: 2K ≈ 1M pixels ≈ 0.04 CNY
                cost_cny = max(0.02, pixels / 1_048_576 * 0.04)
            except (ValueError, IndexError):
                cost_cny = 0.04  # default 2K cost
        else:
            cost_cny = _COST_PER_LEVEL_CNY[size_key]

        # CNY to USD (approximate)
        return round(max(cost_cny * 0.14, 0.01), 2)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        size = inputs.get("size", "2K")
        base = 15.0
        if size in ("3K", "4K") or "2048" in size:
            base = 25.0
        if inputs.get("model_variant", "5_0") == "5_0_lite":
            base *= 0.7  # lite is faster
        return base

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._get_api_key()
        if not api_key:
            return ToolResult(
                success=False,
                error="ARK_API_KEY not set. " + self.install_instructions,
            )

        import requests

        start = time.time()
        variant = inputs.get("model_variant", "5_0")
        model_id = _MODELS.get(variant)
        if not model_id:
            return ToolResult(
                success=False,
                error=f"Unknown model_variant '{variant}'. Must be one of: {list(_MODELS.keys())}",
            )

        size = inputs.get("size", "2K")
        output_format = inputs.get("output_format", "png")
        response_format = inputs.get("response_format", "url")
        watermark = inputs.get("watermark", False)

        # Resolve size keyword to pixel dimensions for the API
        resolved_size = _SIZE_DEFAULTS.get(size.upper(), size)

        # --- Build payload ---
        payload: dict[str, Any] = {
            "model": model_id,
            "prompt": inputs["prompt"],
            "size": resolved_size,
            "response_format": response_format,
            "watermark": watermark,
        }

        # output_format only supported by 5.0 and 5.0 lite
        if variant in ("5_0", "5_0_lite"):
            payload["output_format"] = output_format

        # Seed for reproducibility
        if inputs.get("seed") is not None:
            payload["seed"] = inputs["seed"]

        # Reference images for image-to-image
        # Supports single (image_url/image_path) and multi (image_urls/image_paths)
        image_url = inputs.get("image_url")
        image_urls = inputs.get("image_urls")
        image_path = inputs.get("image_path")
        image_paths = inputs.get("image_paths")

        # Convert local paths to data URIs
        reference_images = []

        # Single path → data URI
        if image_path:
            try:
                reference_images.append(_file_to_data_uri(image_path))
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to read reference image: {e}")

        # Multiple paths → data URIs
        if image_paths:
            try:
                reference_images.extend(_file_to_data_uri(p) for p in image_paths)
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to read reference images: {e}")

        # Single URL
        if image_url:
            reference_images.append(image_url)

        # Multiple URLs
        if image_urls:
            reference_images.extend(image_urls)

        # Set payload["image"]: string for single, array for multiple
        if len(reference_images) == 1:
            payload["image"] = reference_images[0]
        elif len(reference_images) >= 2:
            if len(reference_images) > 14:
                return ToolResult(
                    success=False,
                    error=f"Seedream supports max 14 reference images, got {len(reference_images)}.",
                )
            payload["image"] = reference_images

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(_API_URL, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                error="Volcengine Ark Seedream API timed out after 120s.",
            )
        except requests.exceptions.HTTPError as e:
            body = ""
            try:
                body = e.response.text[:500]
            except Exception:
                pass
            return ToolResult(
                success=False,
                error=f"Volcengine Ark Seedream API HTTP error {e.response.status_code}: {body}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Volcengine Ark Seedream generation failed: {e}",
            )

        # --- Parse response ---
        # Error shape: {"error": {"code": "...", "message": "..."}}
        if "error" in data:
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            return ToolResult(success=False, error=f"Seedream API error: {msg}")

        images = data.get("data", [])
        if not images:
            return ToolResult(
                success=False,
                error=f"No image data in response: {data}",
            )

        first = images[0]

        # --- Obtain image bytes ---
        if response_format == "b64_json" and "b64_json" in first:
            img_bytes = base64.b64decode(first["b64_json"])
        elif "url" in first:
            img_resp = requests.get(first["url"], timeout=60)
            img_resp.raise_for_status()
            img_bytes = img_resp.content
        else:
            return ToolResult(
                success=False,
                error=f"Unexpected response format — no 'url' or 'b64_json' in data[0]: {list(first.keys())}",
            )

        # --- Determine output path ---
        output_path = inputs.get("output_path")
        if not output_path:
            suffix = f".{output_format}" if output_format else _guess_extension(img_bytes)
            output_path = f"seedream_volcengine_output{suffix}"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(img_bytes)

        # --- Usage metadata from response ---
        usage = data.get("usage", {})
        actual_size = first.get("size", resolved_size)

        return ToolResult(
            success=True,
            data={
                "provider": "volcengine",
                "gateway": "volcengine_ark",
                "model": model_id,
                "prompt": inputs["prompt"],
                "variant": variant,
                "size": actual_size,
                "output_format": output_format,
                "response_format": response_format,
                "watermark": watermark,
                "seed": payload.get("seed"),
                "usage": usage,
                "output": str(output_path),
                "output_path": str(output_path),
                "format": output_format,
                "file_size_bytes": len(img_bytes),
            },
            artifacts=[str(output_path)],
            cost_usd=self.estimate_cost(inputs),
            duration_seconds=round(time.time() - start, 2),
            model=model_id,
            seed=payload.get("seed"),
        )
