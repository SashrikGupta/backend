"""
Session Manager for the Streamlit Chat Application.

Handles:
- Session creation and directory management
- Message persistence (history.json)
- Base64 image extraction and artifact saving
- Session listing and metadata retrieval
- Session state rehydration for LangGraph
"""

import json
import os
import re
import uuid
import time
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

from langchain.messages import HumanMessage, AIMessage


# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

BACKEND_ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = BACKEND_ROOT / "sessions"

# Regex to match Base64-encoded image strings (data URI format)
BASE64_IMAGE_PATTERN = re.compile(
    r"(data:image/(png|jpeg|jpg|gif|webp);base64,)([A-Za-z0-9+/\n\r=]+)"
)

# Also match raw base64 blocks that look like images (without data: prefix)
# This catches cases where the AI returns just the base64 string
RAW_BASE64_PATTERN = re.compile(
    r"(?<![A-Za-z0-9+/=])"  # negative lookbehind
    r"((?:[A-Za-z0-9+/]{4}){50,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)"
    r"(?![A-Za-z0-9+/=])"  # negative lookahead
)


# ──────────────────────────────────────────────────────────────────────
# Session Creation
# ──────────────────────────────────────────────────────────────────────


def create_session(product_id: int) -> str:
    """
    Create a new session directory with an empty history.json.

    Args:
        product_id: The product ID for this session.

    Returns:
        The generated session_id (UUID string).
    """
    session_id = str(uuid.uuid4())[:8]  # Short readable ID
    session_dir = SESSIONS_DIR / session_id
    artifacts_dir = session_dir / "artifacts"

    # Create directories
    session_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Initialize history.json
    history = {
        "session_id": session_id,
        "product_id": product_id,
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }

    history_path = session_dir / "history.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    return session_id


# ──────────────────────────────────────────────────────────────────────
# Run ID Generation
# ──────────────────────────────────────────────────────────────────────


def generate_run_id(session_id: str) -> int:
    """
    Generate a unique run_id from session_id + current timestamp.
    Used by LangGraph tools for temp directory naming.

    Returns:
        An integer run_id derived from hash of session_id + time.
    """
    raw = f"{session_id}_{time.time()}"
    hash_hex = hashlib.md5(raw.encode()).hexdigest()[:8]
    return int(hash_hex, 16)


# ──────────────────────────────────────────────────────────────────────
# Image Processing
# ──────────────────────────────────────────────────────────────────────


def _extract_and_save_images(session_id: str, content: str) -> str:
    """
    Detect Base64 image strings in AI response content.
    Extract, decode, and save them as files in the session's artifacts directory.
    Replace the Base64 strings with file paths.

    Args:
        session_id: The current session ID.
        content: The raw AI response content.

    Returns:
        The processed content with Base64 strings replaced by file paths.
    """
    artifacts_dir = SESSIONS_DIR / session_id / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    image_counter = _get_next_image_index(artifacts_dir)

    def replace_data_uri(match):
        nonlocal image_counter
        prefix = match.group(1)  # e.g., "data:image/png;base64,"
        ext = match.group(2)  # e.g., "png"
        b64_data = match.group(3).strip()

        try:
            image_bytes = base64.b64decode(b64_data)
        except Exception:
            return match.group(0)  # Return original if decode fails

        filename = f"image_{image_counter:03d}.{ext}"
        filepath = artifacts_dir / filename
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        image_counter += 1
        # Return a relative path that the Streamlit app can resolve
        return f"/artifacts/{filename}"

    processed = BASE64_IMAGE_PATTERN.sub(replace_data_uri, content)
    return processed


def _get_next_image_index(artifacts_dir: Path) -> int:
    """Get the next available image index in the artifacts directory."""
    existing = list(artifacts_dir.glob("image_*.png")) + \
               list(artifacts_dir.glob("image_*.jpg")) + \
               list(artifacts_dir.glob("image_*.jpeg")) + \
               list(artifacts_dir.glob("image_*.gif")) + \
               list(artifacts_dir.glob("image_*.webp"))
    if not existing:
        return 1

    indices = []
    for f in existing:
        try:
            idx = int(f.stem.split("_")[1])
            indices.append(idx)
        except (IndexError, ValueError):
            pass

    return max(indices, default=0) + 1


# ──────────────────────────────────────────────────────────────────────
# Message Persistence
# ──────────────────────────────────────────────────────────────────────


def save_message(session_id: str, role: str, content: str) -> None:
    """
    Append a message to the session's history.json.

    For AI messages, processes Base64 images before saving.

    Args:
        session_id: The session ID.
        role: "human" or "ai".
        content: The message content.
    """
    session_dir = SESSIONS_DIR / session_id
    history_path = session_dir / "history.json"

    # Process images in AI responses
    if role == "ai":
        content = _extract_and_save_images(session_id, content)

    # Load existing history
    with open(history_path, "r") as f:
        history = json.load(f)

    # Append message
    history["messages"].append({
        "role": role,
        "content": content,
    })

    # Write back
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)


def process_ai_response(session_id: str, content: str) -> str:
    """
    Process an AI response: extract images and replace with paths.
    Does NOT save to history — use save_message for that.

    Args:
        session_id: The session ID.
        content: Raw AI response content.

    Returns:
        Processed content with image paths instead of Base64.
    """
    return _extract_and_save_images(session_id, content)


# ──────────────────────────────────────────────────────────────────────
# Session Loading
# ──────────────────────────────────────────────────────────────────────


def load_session(session_id: str) -> Optional[dict]:
    """
    Load a session's history.json and return the full session data.

    Returns:
        Dict with session_id, product_id, created_at, messages.
        None if session doesn't exist.
    """
    history_path = SESSIONS_DIR / session_id / "history.json"
    if not history_path.exists():
        return None

    with open(history_path, "r") as f:
        return json.load(f)


def rehydrate_messages(session_data: dict) -> list:
    """
    Convert stored message dicts into LangChain message objects
    suitable for LangGraph state rehydration.

    Args:
        session_data: The loaded session dict from history.json.

    Returns:
        List of HumanMessage / AIMessage objects.
    """
    messages = []
    for msg in session_data.get("messages", []):
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))
    return messages


def get_artifact_path(session_id: str, relative_path: str) -> Optional[Path]:
    """
    Resolve a relative artifact path to an absolute path.

    Args:
        session_id: The session ID.
        relative_path: Path like "/artifacts/image_001.png"

    Returns:
        Absolute Path to the artifact file, or None if not found.
    """
    # Strip leading slash
    clean_path = relative_path.lstrip("/")
    full_path = SESSIONS_DIR / session_id / clean_path
    if full_path.exists():
        return full_path
    return None


# ──────────────────────────────────────────────────────────────────────
# Session Listing
# ──────────────────────────────────────────────────────────────────────


def list_sessions() -> list[dict]:
    """
    Scan the sessions directory and return metadata for all sessions.

    Returns:
        List of dicts with: session_id, product_id, created_at, message_count.
        Sorted by created_at descending (newest first).
    """
    sessions = []
    if not SESSIONS_DIR.exists():
        return sessions

    for session_dir in SESSIONS_DIR.iterdir():
        if not session_dir.is_dir():
            continue

        history_path = session_dir / "history.json"
        if not history_path.exists():
            continue

        try:
            with open(history_path, "r") as f:
                data = json.load(f)

            sessions.append({
                "session_id": data.get("session_id", session_dir.name),
                "product_id": data.get("product_id", "unknown"),
                "created_at": data.get("created_at", ""),
                "message_count": len(data.get("messages", [])),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    # Sort newest first
    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


def get_session_product_id(session_id: str) -> Optional[int]:
    """Get the product_id for a given session."""
    data = load_session(session_id)
    if data:
        return data.get("product_id")
    return None
