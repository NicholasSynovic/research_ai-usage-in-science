from types import SimpleNamespace

from aius.analyze import BACKEND_MAPPING
from aius.analyze.data_models import Document
from aius.analyze.openai import OpenAIBackend


class _FakeMessage:
    def __init__(self, content: str, reasoning_content: str | None = None) -> None:
        self.content = content
        self.reasoning_content = reasoning_content


class _FakeChoice:
    def __init__(self, message: _FakeMessage) -> None:
        self.message = message


class _FakeChatCompletions:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class _FakeOpenAIClient:
    def __init__(self, response: object) -> None:
        self.chat = SimpleNamespace(completions=_FakeChatCompletions(response))


class _FakeLogger:
    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_openai_backend_is_registered() -> None:
    assert BACKEND_MAPPING["openai"] is OpenAIBackend


def test_openai_backend_returns_model_response(monkeypatch) -> None:
    response = SimpleNamespace(
        choices=[_FakeChoice(_FakeMessage('{"result": true}', '{"reason": "ok"}'))]
    )
    backend = OpenAIBackend(logger=_FakeLogger(), auth_key="test-key")
    backend.openai_client = _FakeOpenAIClient(response=response)

    result = backend.inference_document(
        document=Document(doi="10.1234/example", content="paper text"),
        system_prompt="system prompt",
    )

    assert result.doi == "10.1234/example"
    assert result.model_response == '{"result": true}'
    assert result.model_reasoning == '{"reason": "ok"}'


def test_openai_backend_returns_empty_response_on_error() -> None:
    backend = OpenAIBackend(logger=_FakeLogger(), auth_key="test-key")
    backend.openai_client = _FakeOpenAIClient(response=RuntimeError("boom"))

    result = backend.inference_document(
        document=Document(doi="10.1234/example", content="paper text"),
        system_prompt="system prompt",
    )

    assert result.doi == "10.1234/example"
    assert result.model_response == ""
    assert result.model_reasoning == ""
