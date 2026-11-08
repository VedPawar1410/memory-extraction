"""Unit tests for MemoryEngine and PersonalityEngine (offline, via fake_gemini)."""

import pytest
from langchain_core.messages import AIMessage

import config
from memory_engine import MemoryEngine, UserProfile
from personality_engine import PersonalityEngine
from tests.conftest import SAMPLE_PROFILE


@pytest.mark.parametrize("bad_key", ["", "   ", None])
def test_engines_reject_missing_api_key(fake_gemini, bad_key):
    with pytest.raises(ValueError):
        MemoryEngine(api_key=bad_key)
    with pytest.raises(ValueError):
        PersonalityEngine(SAMPLE_PROFILE, api_key=bad_key)


def test_engines_use_configured_model(fake_gemini):
    MemoryEngine(api_key="test-key")
    PersonalityEngine(SAMPLE_PROFILE, api_key="test-key")
    extract_llm, rewrite_llm = fake_gemini.instances
    assert extract_llm.kwargs["model"] == config.GEMINI_MODEL
    assert rewrite_llm.kwargs["model"] == config.GEMINI_MODEL
    assert extract_llm.kwargs["temperature"] == config.EXTRACTION_TEMPERATURE
    assert rewrite_llm.kwargs["temperature"] == config.REWRITE_TEMPERATURE


def test_extract_returns_profile_and_sends_chat(fake_gemini):
    profile = MemoryEngine(api_key="test-key").extract_from_chat("User: I'm Sam from Pune")
    assert profile == SAMPLE_PROFILE
    assert "I'm Sam from Pune" in fake_gemini.instances[-1].prompts[0]


@pytest.mark.parametrize("chat", ["", "   \n  "])
def test_extract_rejects_empty_chat(fake_gemini, chat):
    with pytest.raises(ValueError):
        MemoryEngine(api_key="test-key").extract_from_chat(chat)


def test_extract_wraps_api_errors(fake_gemini):
    fake_gemini.error = RuntimeError("404 model not found")
    with pytest.raises(RuntimeError, match="Failed to extract memory"):
        MemoryEngine(api_key="test-key").extract_from_chat("User: hi")


def test_rewrite_returns_plain_string_from_content_blocks(fake_gemini):
    """Regression: Gemini 3 returns a list of content blocks; the UI showed the raw list."""
    out = PersonalityEngine(SAMPLE_PROFILE, api_key="test-key").rewrite_reply("Hello", "casual")
    assert isinstance(out, str)
    assert out == "Hey! Let's learn Python together."


def test_rewrite_still_works_with_plain_string_content(fake_gemini):
    fake_gemini.reply = AIMessage(content="plain text reply")
    out = PersonalityEngine(SAMPLE_PROFILE, api_key="test-key").rewrite_reply("Hello", "casual")
    assert out == "plain text reply"


def test_rewrite_prompt_includes_profile_and_persona(fake_gemini):
    PersonalityEngine(SAMPLE_PROFILE, api_key="test-key").rewrite_reply("Hello", "calm and patient")
    prompt = fake_gemini.instances[-1].prompts[0]
    assert "Lives in Portland" in prompt
    assert "Prefers visual tasks" in prompt
    assert "Anxious about learning to code" in prompt
    assert "calm and patient" in prompt


def test_rewrite_handles_empty_profile(fake_gemini):
    empty = UserProfile(facts=[], preferences=[], emotional_patterns=[])
    PersonalityEngine(empty, api_key="test-key").rewrite_reply("Hello", "casual")
    assert "None provided" in fake_gemini.instances[-1].prompts[0]


@pytest.mark.parametrize("text, persona", [("", "casual"), ("Hello", ""), ("  ", "casual")])
def test_rewrite_rejects_empty_inputs(fake_gemini, text, persona):
    with pytest.raises(ValueError):
        PersonalityEngine(SAMPLE_PROFILE, api_key="test-key").rewrite_reply(text, persona)
