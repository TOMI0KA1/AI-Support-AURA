import json
from unittest import mock
import requests

from src.core.ai_adapter import AIAdapter

class DummyResp:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        if self._json is None:
            raise ValueError("No JSON")
        return self._json

def test_adapter_simulation_when_no_key(monkeypatch):
    adapter = AIAdapter()
    adapter.api_key = None
    r = adapter.chat("Hello")
    assert "[SIMULATED" in r

def test_adapter_parses_candidates(monkeypatch):
    adapter = AIAdapter(api_key="fakekey", api_url="https://api.fake")
    sample = {"candidates": [{"content": "Привет, я бот"}]}
    with mock.patch("requests.post", return_value=DummyResp(200, sample, text="")) as rp:
        out = adapter.chat("Tell me something")
        assert "Привет" in out

def test_adapter_retries_on_5xx(monkeypatch):
    adapter = AIAdapter(api_key="fakekey", api_url="https://api.fake")
    # First two calls 500, then 200
    resp500 = DummyResp(500, None, text="Server error")
    resp200 = DummyResp(200, {"candidates": [{"content": "OK"}]}, text="")
    side = [resp500, resp500, resp200]
    def post(url, headers=None, json=None, timeout=None):
        return side.pop(0)
    with mock.patch("requests.post", side_effect=post):
        out = adapter.chat("Will retry")
        assert "OK" in out