"""Render Mermaid diagrams to images via mermaid.ink.

This module provides zero-dependency diagram rendering by encoding Mermaid
markup and sending it to the free mermaid.ink API, which returns SVG/PNG images.

Configuration via environment variables:
    SWE_ARCHITECT_MCP_DIAGRAM_RENDERER or SE_MCP_DIAGRAM_RENDERER:
    "mermaid_ink" (default), or "none" to skip rendering.
"""

from __future__ import annotations

import base64
import logging
import os
import zlib
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────
MERMAID_INK_BASE = "https://mermaid.ink"
RENDER_TIMEOUT_SECONDS = 15
MAX_DIAGRAM_BYTES = 50_000  # mermaid.ink limit is ~64KB encoded


def get_renderer_mode() -> str:
    """Return the configured renderer mode from environment."""
    mode = (
        os.getenv("SWE_ARCHITECT_MCP_DIAGRAM_RENDERER", "").strip()
        or os.getenv("SE_MCP_DIAGRAM_RENDERER", "").strip()
        or "mermaid_ink"
    )
    return mode.lower()


# ── Encoding ──────────────────────────────────────────────────────────────

def _pako_deflate_base64(mermaid_code: str) -> str:
    """Encode Mermaid code using pako-compatible deflate + base64url.

    This matches the encoding used by mermaid.live and mermaid.ink:
    1. UTF-8 encode the Mermaid text
    2. Deflate compress (raw deflate, no zlib header)
    3. Base64url encode (URL-safe, no padding)
    """
    raw = mermaid_code.encode("utf-8")
    # wbits=-15 gives raw deflate (no zlib/gzip header) — pako compatible
    compressed = zlib.compress(raw, level=9)[2:-4]  # strip zlib header/checksum
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return encoded.rstrip("=")


def _simple_base64(mermaid_code: str) -> str:
    """Simple base64 encoding fallback for mermaid.ink."""
    raw = mermaid_code.encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


# ── URL Generation ────────────────────────────────────────────────────────

def get_mermaid_ink_url(
    mermaid_code: str,
    *,
    fmt: str = "svg",
    theme: str = "default",
    bg_color: str = "white",
) -> str:
    """Generate a mermaid.ink URL that renders the given diagram.

    Args:
        mermaid_code: Raw Mermaid diagram text.
        fmt: Output format — "svg", "img" (png), or "pdf".
        theme: Mermaid theme — "default", "dark", "forest", "neutral".
        bg_color: Background color name or hex (e.g. "white", "!F5F5F5").

    Returns:
        The full mermaid.ink URL.
    """
    encoded = _simple_base64(mermaid_code)
    endpoint = "svg" if fmt == "svg" else "img"
    url = f"{MERMAID_INK_BASE}/{endpoint}/base64/{encoded}"

    params: list[str] = []
    if theme != "default":
        params.append(f"theme={theme}")
    if bg_color != "white":
        params.append(f"bgColor={bg_color}")
    if fmt == "img":
        params.append("type=png")

    if params:
        url += "?" + "&".join(params)

    return url


def get_mermaid_live_url(mermaid_code: str) -> str:
    """Generate a mermaid.live editor URL for interactive editing."""
    encoded = _simple_base64(mermaid_code)
    return f"https://mermaid.live/edit#base64:{encoded}"


# ── Rendering ─────────────────────────────────────────────────────────────

def render_mermaid_to_file(
    mermaid_code: str,
    output_path: str | Path,
    *,
    fmt: str = "svg",
    theme: str = "default",
) -> bool:
    """Render a Mermaid diagram to an image file via mermaid.ink.

    Args:
        mermaid_code: Raw Mermaid diagram text.
        output_path: Where to save the rendered image.
        fmt: "svg" or "png".
        theme: Mermaid theme name.

    Returns:
        True if rendering succeeded, False otherwise.
    """
    if get_renderer_mode() == "none":
        logger.debug("Diagram rendering disabled (SWE_ARCHITECT_MCP_DIAGRAM_RENDERER=none)")
        return False

    if len(mermaid_code.encode("utf-8")) > MAX_DIAGRAM_BYTES:
        logger.warning("Diagram too large for mermaid.ink (%d bytes)", len(mermaid_code))
        return False

    url = get_mermaid_ink_url(mermaid_code, fmt=fmt, theme=theme)

    try:
        request = Request(url, headers={"User-Agent": "swe-architect-mcp/1.0"})
        with urlopen(request, timeout=RENDER_TIMEOUT_SECONDS) as response:
            image_data = response.read()

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(image_data)
        logger.info("Rendered %s diagram to %s", fmt, out)
        return True

    except (URLError, TimeoutError, OSError) as exc:
        logger.warning("mermaid.ink rendering failed: %s", exc)
        return False
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unexpected error during diagram rendering: %s", exc)
        return False
