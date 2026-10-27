"""The prototype: a raw AI Studio API key.

Fine on your own laptop. Anyone who copies this key can spend your money
until you delete it, so don't ship this pattern to production.

    export GEMINI_API_KEY=your-key   # from https://aistudio.google.com/apikey
    python -m step1_keyless_auth.before_api_key
"""

import os

from google import genai

from common.config import DEFAULT_MODEL


def main() -> None:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
        contents="Reply with one word: ping",
    )
    print(resp.text)


if __name__ == "__main__":
    main()
