"""UI tests: run the real Streamlit app headlessly with AppTest and the fake model."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app import parse_chat

APP_PATH = str(Path(__file__).parent.parent / "app.py")


@pytest.fixture
def app(fake_gemini):
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    return at.run()


def button(at, label):
    return next(b for b in at.button if label in b.label)


def set_key(at, key="test-key"):
    at.sidebar.text_input[0].input(key).run()


def test_without_key_buttons_are_disabled(app):
    assert not app.exception
    assert button(app, "Extract profile").disabled
    assert button(app, "Rewrite response").disabled


def test_server_env_key_is_never_used(monkeypatch, fake_gemini):
    """Bring-your-own-key: a GOOGLE_API_KEY on the server must not unlock the app."""
    monkeypatch.setenv("GOOGLE_API_KEY", "owner-key-on-server")
    at = AppTest.from_file(APP_PATH, default_timeout=30).run()
    assert button(at, "Extract profile").disabled


def test_full_flow_extract_then_rewrite(app, fake_gemini):
    set_key(app, "  visitor-key  ")
    assert not button(app, "Extract profile").disabled
    assert button(app, "Rewrite response").disabled  # no profile yet

    button(app, "Extract profile").click().run()
    assert not app.error
    assert app.session_state["user_profile"].facts == ["Works as a graphic designer", "Lives in Portland"]
    assert fake_gemini.instances[-1].kwargs["google_api_key"] == "visitor-key"  # whitespace stripped

    button(app, "Rewrite response").click().run()
    result = app.session_state["rewrite"]
    assert result["text"] == "Hey! Let's learn Python together."
    assert result["persona"] == "friendly and encouraging"


def test_rewrite_result_survives_rerun(app):
    set_key(app)
    button(app, "Extract profile").click().run()
    button(app, "Rewrite response").click().run()
    app.run()  # any widget change triggers a rerun
    assert app.session_state["rewrite"] is not None


def test_new_extraction_clears_old_rewrite(app):
    set_key(app)
    button(app, "Extract profile").click().run()
    button(app, "Rewrite response").click().run()
    button(app, "Extract profile").click().run()
    assert app.session_state["rewrite"] is None


def test_empty_chat_shows_error(app):
    set_key(app)
    app.text_area[0].set_value("").run()
    button(app, "Extract profile").click().run()
    assert "Please paste a conversation first." in [e.value for e in app.error]


def test_api_failure_is_shown_not_crashed(app, fake_gemini):
    fake_gemini.error = RuntimeError("API key not valid")
    set_key(app)
    button(app, "Extract profile").click().run()
    assert not app.exception
    assert any("API key not valid" in e.value for e in app.error)


def test_parse_chat_roles_and_continuation_lines():
    chat = "User: hi\nthere\n\nAI: hello\nAssistant: again\nrandom preamble"
    assert parse_chat(chat) == [
        ("user", "hi\nthere"),
        ("assistant", "hello"),
        ("assistant", "again\nrandom preamble"),
    ]
    assert parse_chat("no speakers here") == []
