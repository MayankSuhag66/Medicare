import json
import os
import unittest
from unittest.mock import patch

import backend


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


class ProviderTests(unittest.TestCase):
    def test_default_models_and_provider_shapes(self):
        cases = [
            ("gemini", "generativelanguage.googleapis.com", "gemini-2.5-flash", {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}),
            ("groq", "api.groq.com", "llama-3.3-70b-versatile", {"choices": [{"message": {"content": "Hello"}}]}),
            ("openrouter", "openrouter.ai", "openrouter/free", {"choices": [{"message": {"content": "Hello"}}]}),
            ("cohere", "api.cohere.com", "command-r7b-12-2024", {"message": {"content": [{"type": "text", "text": "Hello"}]}}),
        ]
        for name, domain, model, response in cases:
            with self.subTest(name=name), patch.dict(os.environ, {backend.PROVIDERS[name][0]: "test-key"}, clear=True):
                requests = []

                def fake_open(request, timeout):
                    requests.append(request)
                    return FakeResponse(response)

                with patch.object(backend, "urlopen", fake_open):
                    answer = backend.query_provider(name, [{"role": "system", "content": "Safety"}, {"role": "user", "content": "Hi"}], json_mode=True)
                self.assertEqual(answer, "Hello")
                self.assertIn(domain, requests[0].full_url)
                self.assertEqual(json.loads(requests[0].data)["model"] if name != "gemini" else model, model)
                self.assertNotIn("test-key", str(json.loads(requests[0].data)))

    def test_json_wrappers(self):
        self.assertEqual(backend.parse_json('```json\n{"summary":"clear"}\n```')["summary"], "clear")
        with self.assertRaises(ValueError):
            backend.parse_json("not structured")

    def test_openrouter_rejects_paid_model(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test", "OPENROUTER_MODEL": "openai/gpt-4o"}):
            with self.assertRaises(ValueError):
                backend.query_provider("openrouter", [{"role": "user", "content": "Hello"}])

    def test_anonymous_token_rejected(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_ANON_KEY": "anon"}):
            self.assertFalse(backend.verify_user(""))


if __name__ == "__main__":
    unittest.main()
