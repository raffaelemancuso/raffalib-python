import pytest

requests = pytest.importorskip("requests")
pytest.importorskip("pyalex")

from raffalib import check_openalex_api_key as mod  # noqa: E402


class _Query:
    def __init__(self, on_get):
        self._on_get = on_get

    def filter(self, **kwargs):
        return self

    def get(self):
        return self._on_get()


def test_valid_key_returns_true(monkeypatch):
    monkeypatch.setattr(mod.pyalex, "Works", lambda: _Query(lambda: [{"id": "W1"}]))
    assert mod.check_openalex_api_key() is True


def test_forbidden_key_returns_false(monkeypatch):
    err = requests.exceptions.HTTPError()

    class _Resp:
        status_code = 403

    err.response = _Resp()

    def boom():
        raise err

    monkeypatch.setattr(mod.pyalex, "Works", lambda: _Query(boom))
    assert mod.check_openalex_api_key() is False


def test_other_http_error_reraised(monkeypatch):
    err = requests.exceptions.HTTPError()

    class _Resp:
        status_code = 500

    err.response = _Resp()

    def boom():
        raise err

    monkeypatch.setattr(mod.pyalex, "Works", lambda: _Query(boom))
    with pytest.raises(requests.exceptions.HTTPError):
        mod.check_openalex_api_key()
