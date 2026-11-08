"""
Single source of truth for model settings.

Google retires model names on its own schedule (gemini-2.0-flash started
returning 404 in 2026), so the model is read from the GEMINI_MODEL env var.
When the default is retired, change the env var on the host - no code change.
"""

import os

from dotenv import load_dotenv

# Load .env here so local overrides apply no matter which module is imported first.
load_dotenv()

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

EXTRACTION_TEMPERATURE = 0.1  # low: consistent, factual extraction
REWRITE_TEMPERATURE = 0.7  # higher: more creative rewriting
