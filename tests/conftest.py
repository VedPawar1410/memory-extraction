"""
Shared test fixtures.

The tests never call Google. `fake_gemini` swaps ChatGoogleGenerativeAI for a
small fake that records every prompt and returns canned output, so the suite
runs offline, needs no API key and finishes in about a second.
"""

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda

import memory_engine
import personality_engine
from memory_engine import UserProfile

SAMPLE_PROFILE = UserProfile(
    facts=["Works as a graphic designer", "Lives in Portland"],
    preferences=["Prefers visual tasks"],
    emotional_patterns=["Anxious about learning to code"],
)


class FakeGemini(Runnable):
    """Stands in for ChatGoogleGenerativeAI. Configure per test via class attributes."""

    profile = SAMPLE_PROFILE  # what structured extraction returns
    # Gemini 3 returns content as a list of blocks - this is what broke .content
    reply = AIMessage(content=[{"type": "text", "text": "Hey! Let's learn Python together."}])
    error = None  # set to an Exception to simulate an API failure
    instances = []  # every model the engines created, newest last

    def __init__(self, **kwargs):
        self.kwargs = kwargs  # model name, temperature, api key the engine passed
        self.prompts = []  # prompt text sent to the model
        type(self).instances.append(self)

    def _respond(self, prompt_value, output):
        self.prompts.append(prompt_value.to_string())
        if self.error:
            raise self.error
        return output

    def with_structured_output(self, schema):
        return RunnableLambda(lambda prompt: self._respond(prompt, self.profile))

    def invoke(self, input, config=None, **kwargs):
        return self._respond(input, self.reply)


@pytest.fixture
def fake_gemini(monkeypatch):
    """Patch both engines to use a fresh FakeGemini subclass (so tests don't share state)."""

    class Fake(FakeGemini):
        instances = []

    monkeypatch.setattr(memory_engine, "ChatGoogleGenerativeAI", Fake)
    monkeypatch.setattr(personality_engine, "ChatGoogleGenerativeAI", Fake)
    return Fake
