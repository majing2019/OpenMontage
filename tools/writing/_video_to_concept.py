"""Video-to-concept extractor — turns video URLs/files into story concepts.

Orchestrates existing OpenMontage analysis tools to extract a transcript,
then feeds it through _text_analyzer to produce a TextAnalysisResult
ready for the Story Factory's what-if engine.

Three-tier graceful degradation for transcript extraction:
  1. TranscriptFetcher (fast — YouTube captions only)
  2. VideoAnalyzer with transcript_only depth
  3. VideoDownloader + Transcriber (Whisper — slow but universal)
"""

from __future__ import annotations

from ._text_analyzer import TextAnalysisResult, analyze_text


def extract_concept_from_video(
    video_source: str,
    output_dir: str | None = None,
) -> TextAnalysisResult:
    """Extract a story concept from a video URL or local file.

    Args:
        video_source: URL (YouTube, etc.) or local file path.
        output_dir: Optional output directory for downloaded files.

    Returns:
        TextAnalysisResult with core_concept ready for Story Factory.
        Falls back gracefully if all extraction methods fail.
    """
    is_url = video_source.startswith("http://") or video_source.startswith("https://")

    transcript_text: str | None = None
    metadata: dict = {}

    # ── Tier 1: TranscriptFetcher (YouTube captions, instant) ──────────
    if is_url:
        transcript_text = _try_transcript_fetcher(video_source)
        if transcript_text:
            return analyze_text(transcript_text)

    # ── Tier 2: VideoAnalyzer (full analysis pipeline) ──────────────────
    transcript_text, metadata = _try_video_analyzer(video_source, output_dir)
    if transcript_text:
        result = analyze_text(transcript_text)
        # Enrich with metadata if available
        if metadata.get("title"):
            result.original_length = len(transcript_text)
        return result

    # ── Tier 3: Download + Transcribe (Whisper, slow) ───────────────────
    if is_url:
        transcript_text = _try_download_and_transcribe(video_source, output_dir)
        if transcript_text:
            return analyze_text(transcript_text)

    # ── Fallback: use video title from metadata or URL itself ───────────
    fallback = metadata.get("title") or _extract_title_from_url(video_source)
    return TextAnalysisResult(
        core_concept=fallback[:60] if fallback else video_source[:60],
        original_length=0,
    )


# ── Tier 1 ──────────────────────────────────────────────────────────────

def _try_transcript_fetcher(video_source: str) -> str | None:
    """Try YouTube transcript via TranscriptFetcher. Fast, no download needed."""
    try:
        from tools.analysis.transcript_fetcher import TranscriptFetcher
    except ImportError:
        return None

    try:
        fetcher = TranscriptFetcher()
        result = fetcher.execute({
            "url_or_video_id": video_source,
            "languages": ["zh-Hans", "zh", "en"],
            "include_auto_generated": True,
        })
        if result.success and result.data:
            return _extract_transcript_text(result.data)
    except Exception:
        pass

    return None


# ── Tier 2 ──────────────────────────────────────────────────────────────

def _try_video_analyzer(video_source: str, output_dir: str | None
                        ) -> tuple[str | None, dict]:
    """Try VideoAnalyzer with transcript_only depth."""
    try:
        from tools.analysis.video_analyzer import VideoAnalyzer
    except ImportError:
        return None, {}

    try:
        analyzer = VideoAnalyzer()
        inputs: dict = {
            "source": video_source,
            "analysis_depth": "transcript_only",
        }
        if output_dir:
            inputs["output_dir"] = output_dir

        result = analyzer.execute(inputs)
        if result.success and result.data:
            text = _extract_transcript_text(result.data)
            meta = result.data.get("metadata", {})
            return text, meta
    except Exception:
        pass

    return None, {}


# ── Tier 3 ──────────────────────────────────────────────────────────────

def _try_download_and_transcribe(video_source: str, output_dir: str | None
                                  ) -> str | None:
    """Download video then transcribe with Whisper."""
    try:
        from tools.analysis.video_downloader import VideoDownloader
        from tools.analysis.transcriber import Transcriber
    except ImportError:
        return None

    try:
        downloader = VideoDownloader()
        dl_inputs: dict = {
            "url": video_source,
            "format": "audio_only",
        }
        if output_dir:
            dl_inputs["output_dir"] = output_dir

        dl_result = downloader.execute(dl_inputs)
        if not dl_result.success:
            return None

        audio_path = dl_result.data.get("audio_path") or dl_result.data.get("output_path")
        if not audio_path:
            return None

        transcriber = Transcriber()
        tr_result = transcriber.execute({
            "input_path": audio_path,
            "model_size": "base",
            "language": None,  # auto-detect
        })

        if tr_result.success and tr_result.data:
            return _extract_transcript_text(tr_result.data)
    except Exception:
        pass

    return None


# ── Helpers ──────────────────────────────────────────────────────────────

def _extract_transcript_text(data: dict) -> str | None:
    """Extract full transcript text from various tool result formats."""
    # Direct full text
    if data.get("full_text"):
        return data["full_text"]

    # Transcript segments
    segments = data.get("segments") or data.get("transcript") or []
    if segments:
        texts = []
        for seg in segments:
            if isinstance(seg, dict):
                t = seg.get("text") or seg.get("content") or ""
                texts.append(t)
            elif isinstance(seg, str):
                texts.append(seg)
        joined = " ".join(texts).strip()
        if joined:
            return joined

    # Nested transcript
    transcript = data.get("transcript")
    if isinstance(transcript, dict):
        return _extract_transcript_text(transcript)

    return None


def _extract_title_from_url(url: str) -> str:
    """Extract a human-readable title from a URL."""
    # YouTube
    if "youtube.com/watch" in url or "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0][:40]
    # TikTok
    if "tiktok.com" in url or "douyin.com" in url:
        return url.split("/")[-1].split("?")[0][:40]
    # Generic
    parts = url.rstrip("/").split("/")
    return parts[-1][:40] if parts else url[:40]
