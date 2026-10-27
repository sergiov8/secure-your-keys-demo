"""Lets the model write and run Python in a Google-managed sandbox.

The generated code runs on Google's side, not in your app process, so it
cannot read your environment, your files or your database.

    export GOOGLE_CLOUD_PROJECT=my-startup-prod
    python -m bonus_sandboxed_code.run_in_sandbox
"""

from google import genai
from google.genai import types

from common.config import load_settings

PROMPT = (
    "Compute the Pearson correlation between monthly ad spend "
    "[1200, 1500, 900, 2100, 1800] and signups [310, 360, 250, 480, 430]. "
    "Run code to get the number."
)


def main() -> None:
    settings = load_settings()
    client = genai.Client(enterprise=True, project=settings.project, location=settings.location)
    resp = client.models.generate_content(
        model=settings.model,
        contents=PROMPT,
        config=types.GenerateContentConfig(
            tools=[types.Tool(code_execution=types.ToolCodeExecution())],
        ),
    )
    for part in resp.candidates[0].content.parts:
        if part.executable_code:
            print("--- code the model ran ---")
            print(part.executable_code.code)
        elif part.code_execution_result:
            print("--- sandbox output ---")
            print(part.code_execution_result.output)
        elif part.text:
            print(part.text)


if __name__ == "__main__":
    main()
