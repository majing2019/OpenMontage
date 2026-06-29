"""Seedance 2.0 (ByteDance) video generation via Volcengine Ark (火山引擎方舟).

Volcengine Ark hosts ByteDance's Seedance 2.0 models directly:
  - doubao-seedance-2-0-260128        (standard)
  - doubao-seedance-2-0-fast-260128   (fast tier)

This is ByteDance's official API — supports Alipay payment, no international
credit card required. Supports 1080p output, draft preview mode, flex (offline)
pricing at 50% cost, and return_last_frame for video chaining.

Calling modes:
  1. Direct model name (default): ARK_API_KEY + model name string.
  2. Endpoint ID override: set ARK_ENDPOINT_STANDARD / ARK_ENDPOINT_FAST
     env vars to your ep-xxx IDs from the Volcengine Ark console to route
     through specific inference endpoints.

Uses provider="volcengine" (distinct from the fal.ai and Replicate seedance
gateways) so each gateway surfaces independently in preflight and
provider_menu_summary(). All three gateways access the same Seedance 2.0
model family; video_selector routes by capability and quality_score.

Model variant constraints (Seedance 2.0):
  - draft mode: standard only (fast returns 400)
  - max resolution: 1080p (standard), 720p (fast)
  - seed parameter: NOT supported in 2.0 (silently ignored by API)
  - service_tier "flex": NOT supported in 2.0 (silently ignored by API)
  - These are 1.x parameters that 2.0 rejects or ignores.

Performance (measured 2026-06-29):
  - Fast 720p 5s no-audio: ~100s, ~$0.18
  - Fast 720p 5s with-audio: ~167s, ~$0.32
  - Standard 1080p 5s: estimated 120-300s
  - Audio generation adds ~60s and roughly doubles cost.

Env var pitfall:
  - Empty ARK_ENDPOINT_* vars MUST NOT have inline # comments in .env.
    python-dotenv treats "KEY=  # comment" as value "# comment". Put
    comments on the preceding line or comment out the entire line.
  - The execute() method strips # comments and validates model_id format
    (must start with "doubao-" or "ep-") as defense-in-depth.

API docs: https://www.volcengine.com/docs/82379/1520757
SDK examples: https://www.volcengine.com/docs/82379/2298881
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

# Volcengine Ark API endpoints
_SUBMIT_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
_POLL_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"

# Model IDs (default — can be overridden by endpoint ID env vars)
_MODEL_STANDARD = "doubao-seedance-2-0-260128"
_MODEL_FAST = "doubao-seedance-2-0-fast-260128"
# Endpoint ID env var names (override model names with ep-xxx from Volcengine console)
_ENDPOINT_ENV = {
    "standard": "ARK_ENDPOINT_STANDARD",
    "fast": "ARK_ENDPOINT_FAST",
}


def _file_to_data_uri(path: str) -> str:
    """Convert a local image file to a base64 data URI for Volcengine API."""
    p = Path(path)
    suffix = p.suffix.lstrip(".")
    mime = f"image/{suffix.lower()}"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


class SeedanceVolcengine(BaseTool):
    name = "seedance_volcengine"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "volcengine"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set ARK_API_KEY to your Volcengine Ark API key.\n"
        "  在火山引擎方舟平台获取: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey\n"
        "  账户余额需 >= 200 元才能使用 Seedance 2.0 模型。\n"
        "Optional — override model names with endpoint IDs (ep-xxx):\n"
        "  ARK_ENDPOINT_STANDARD  ARK_ENDPOINT_FAST\n"
        "  在推理接入点页面获取: https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint"
    )
    agent_skills = ["seedance-2-0", "ai-video-gen", "volcengine-ark"]

    capabilities = [
        "text_to_video",
        "image_to_video",
        "native_audio",
        "draft_preview",
        "flex_pricing",
        "return_last_frame",
    ]
    supports = {
        "text_to_video": True,
        "image_to_video": True,
        "reference_image": True,
        "native_audio": True,
        "cinematic_quality": True,
        "camera_direction": True,
        "lip_sync": True,
        "multi_shot": True,
        "aspect_ratio": True,
        "seed": True,
        "draft_preview": True,
        "flex_pricing": True,
        "1080p": True,
        "return_last_frame": True,
    }
    best_for = [
        "preferred Seedance gateway for users with Volcengine Ark access (Alipay payment)",
        "1080p high-fidelity video generation",
        "draft preview mode for low-cost prompt validation",
        "flex (offline) pricing at 50% cost for non-urgent generation",
        "video chaining via return_last_frame",
    ]
    not_good_for = ["users without Volcengine Ark account"]
    fallback_tools = ["seedance_replicate", "seedance_video", "veo_video", "kling_video"]
    quality_score = 0.96

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string"},
            "operation": {
                "type": "string",
                "enum": ["text_to_video", "image_to_video"],
                "default": "text_to_video",
            },
            "model_variant": {
                "type": "string",
                "enum": ["standard", "fast"],
                "default": "standard",
                "description": "standard = doubao-seedance-2-0-260128, fast = doubao-seedance-2-0-fast-260128",
            },
            "duration": {
                "type": "string",
                "enum": [
                    "auto", "4", "5", "6", "7", "8", "9",
                    "10", "11", "12", "13", "14", "15",
                ],
                "default": "5",
                "description": "Video duration in seconds. 'auto' lets the model decide (4-15s).",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"],
                "default": "16:9",
                "description": "Output aspect ratio. 'adaptive' lets the model choose based on content.",
            },
            "resolution": {
                "type": "string",
                "enum": ["480p", "720p", "1080p"],
                "default": "720p",
                "description": "Output resolution. 1080p not supported on fast variant.",
            },
            "generate_audio": {
                "type": "boolean",
                "default": True,
                "description": "Generate synchronized audio with the video.",
            },
            "image_url": {
                "type": "string",
                "description": "First frame image URL for image_to_video.",
            },
            "image_path": {
                "type": "string",
                "description": "Local image path — auto-converted to base64 data URI.",
            },
            "end_image_url": {
                "type": "string",
                "description": "Last frame image URL for first+last frame mode.",
            },
            "seed": {"type": "integer", "description": "Seed for reproducibility."},
            "draft": {
                "type": "boolean",
                "default": False,
                "description": "Draft preview mode — 480p only, lower cost, for prompt validation.",
            },
            "return_last_frame": {
                "type": "boolean",
                "default": False,
                "description": "Return last frame image for chaining consecutive videos.",
            },
            "service_tier": {
                "type": "string",
                "enum": ["default", "flex"],
                "default": "default",
                "description": "'default' = online inference; 'flex' = offline at 50% cost (longer wait).",
            },
            "watermark": {
                "type": "boolean",
                "default": False,
                "description": "Add AI-generated watermark to video.",
            },
            "output_path": {"type": "string", "description": "Path to save the MP4 file."},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "model_variant", "operation", "duration", "seed"]
    side_effects = ["writes video file to output_path", "calls Volcengine Ark API"]
    user_visible_verification = [
        "Watch generated clip for motion coherence, audio sync, and visual quality"
    ]

    def _get_api_key(self) -> str | None:
        return os.environ.get("ARK_API_KEY")

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._get_api_key() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        duration = inputs.get("duration", "5")
        resolution = inputs.get("resolution", "720p")
        service_tier = inputs.get("service_tier", "default")
        draft = inputs.get("draft", False)

        secs = 5 if duration == "auto" else int(duration)
        if draft:
            secs = 5  # draft always produces a short preview

        # Approximate token-based pricing (CNY per token, converted to USD)
        # ~14,414 tokens/sec at 720p, ~20,592 tokens/sec at 1080p
        # Rates: ~32 CNY/MTok (720p), ~46 CNY/MTok (1080p), ~20 CNY/MTok (480p/draft)
        tokens_per_sec = {
            "480p": 9000,
            "720p": 14414,
            "1080p": 20592,
        }.get(resolution, 14414)

        rate_per_mtok = {
            "480p": 20,
            "720p": 32,
            "1080p": 46,
        }.get(resolution, 32)

        cost_cny = (tokens_per_sec * secs / 1_000_000) * rate_per_mtok
        if service_tier == "flex":
            cost_cny *= 0.5
        if draft:
            cost_cny *= 0.6

        # CNY to USD (approximate)
        cost_usd = cost_cny * 0.14
        return round(max(cost_usd, 0.01), 2)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        variant = inputs.get("model_variant", "standard")
        base = {"fast": 60.0}.get(variant, 120.0)
        if inputs.get("service_tier") == "flex":
            base *= 3  # offline inference is slower
        if inputs.get("draft"):
            base *= 0.6
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
        variant = inputs.get("model_variant", "standard")
        resolution = inputs.get("resolution", "720p")

        # Resolve model ID: endpoint ID env var > default model name
        default_models = {"standard": _MODEL_STANDARD, "fast": _MODEL_FAST}
        endpoint_env = _ENDPOINT_ENV.get(variant)
        model_id = os.environ.get(endpoint_env, "") if endpoint_env else ""
        # Strip inline comments and whitespace from env var value
        if model_id:
            model_id = model_id.split("#")[0].strip()
        # Validate: must look like a model ID (doubao-*) or endpoint ID (ep-*)
        if model_id and not (model_id.startswith("doubao-") or model_id.startswith("ep-")):
            model_id = ""
        if not model_id:
            model_id = default_models.get(variant, _MODEL_STANDARD)
        duration_str = inputs.get("duration", "5")
        draft = inputs.get("draft", False)

        # --- Validate constraints ---
        if variant == "fast" and resolution == "1080p":
            return ToolResult(
                success=False,
                error="1080p is not supported on the fast model variant. Use 'standard' or lower resolution.",
            )
        if draft and resolution != "480p":
            return ToolResult(
                success=False,
                error="Draft mode only supports 480p resolution.",
            )

        # --- Build content array ---
        content: list[dict[str, Any]] = [
            {"type": "text", "text": inputs["prompt"]}
        ]

        operation = inputs.get("operation", "text_to_video")

        # Handle image_url or local image_path
        image_url = inputs.get("image_url")
        image_path = inputs.get("image_path")
        end_image_url = inputs.get("end_image_url")

        if image_path:
            try:
                image_url = _file_to_data_uri(image_path)
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to read image file: {e}")

        if operation == "image_to_video" and image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
            if end_image_url:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": end_image_url},
                    "role": "last_frame",
                })

        # --- Build payload ---
        duration_val = -1 if duration_str == "auto" else int(duration_str)

        payload: dict[str, Any] = {
            "model": model_id,
            "content": content,
            "resolution": resolution,
            "ratio": inputs.get("aspect_ratio", "16:9"),
            "duration": duration_val,
            "generate_audio": inputs.get("generate_audio", True),
            "watermark": inputs.get("watermark", False),
        }

        # Optional fields — only include when non-default
        if inputs.get("seed") is not None:
            payload["seed"] = inputs["seed"]
        if draft:
            payload["draft"] = True
        if inputs.get("return_last_frame"):
            payload["return_last_frame"] = True
        if inputs.get("service_tier") == "flex":
            payload["service_tier"] = "flex"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            # --- Step 1: Submit task ---
            submit_resp = requests.post(
                _SUBMIT_URL, headers=headers, json=payload, timeout=60
            )
            submit_resp.raise_for_status()
            submit_data = submit_resp.json()

            task_id = submit_data.get("id")
            if not task_id:
                return ToolResult(
                    success=False,
                    error=f"Volcengine Ark returned no task ID: {submit_data}",
                )

            # --- Step 2: Poll for completion ---
            poll_data: dict[str, Any] = {}
            poll_interval = 10
            max_wait = 900  # 15 minutes
            deadline = time.time() + max_wait

            while time.time() < deadline:
                poll_resp = requests.get(
                    _POLL_URL.format(task_id=task_id),
                    headers=headers,
                    timeout=30,
                )
                poll_resp.raise_for_status()
                poll_data = poll_resp.json()

                status = poll_data.get("status")
                if status == "succeeded":
                    break
                elif status in ("failed", "expired", "cancelled"):
                    error_msg = poll_data.get("error", {})
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get("message", str(error_msg))
                    return ToolResult(
                        success=False,
                        error=f"Volcengine Ark task {status}: {error_msg}",
                    )
                else:
                    # queued, running — wait and retry
                    time.sleep(poll_interval)
            else:
                return ToolResult(
                    success=False,
                    error=f"Volcengine Ark task timed out after {max_wait}s (status: {poll_data.get('status')})",
                )

            # --- Step 3: Extract video URL ---
            result_content = poll_data.get("content", {})
            video_url = result_content.get("video_url")
            if not video_url:
                return ToolResult(
                    success=False,
                    error=f"No video_url in response: {poll_data}",
                )

            # --- Step 4: Download video ---
            video_response = requests.get(video_url, timeout=300)
            video_response.raise_for_status()

            output_path = Path(inputs.get("output_path", "seedance_volcengine_output.mp4"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(video_response.content)

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Volcengine Ark Seedance 2.0 generation failed: {e}",
            )

        # --- Step 5: Probe output ---
        from tools.video._shared import probe_output

        probed = probe_output(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": "seedance",
                "gateway": "volcengine",
                "model": model_id,
                "task_id": task_id,
                "prompt": inputs["prompt"],
                "variant": variant,
                "aspect_ratio": inputs.get("aspect_ratio", "16:9"),
                "resolution": resolution,
                "generate_audio": inputs.get("generate_audio", True),
                "draft": draft,
                "service_tier": inputs.get("service_tier", "default"),
                "seed": poll_data.get("seed"),
                "usage": poll_data.get("usage"),
                "actual_duration": poll_data.get("duration"),
                "actual_ratio": poll_data.get("ratio"),
                "output": str(output_path),
                "output_path": str(output_path),
                "format": "mp4",
                **probed,
            },
            artifacts=[str(output_path)],
            cost_usd=self.estimate_cost(inputs),
            duration_seconds=round(time.time() - start, 2),
            model=model_id,
        )
