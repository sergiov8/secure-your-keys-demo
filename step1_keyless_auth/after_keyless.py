"""Production: no key in the code at all.

The client finds Application Default Credentials (ADC) on its own. On a
laptop those come from `gcloud auth application-default login`. On Cloud
Run, GKE or Compute Engine they are short-lived tokens for the service
account attached to the workload.

    gcloud auth application-default login
    export GOOGLE_CLOUD_PROJECT=my-startup-prod
    python -m step1_keyless_auth.after_keyless
"""

from google import genai

from common.config import load_settings


def main() -> None:
    settings = load_settings()
    # enterprise=True targets Gemini Enterprise Agent Platform.
    # Older SDK versions call the same flag vertexai=True.
    client = genai.Client(
        enterprise=True,
        project=settings.project,
        location=settings.location,
    )
    resp = client.models.generate_content(
        model=settings.model,
        contents="Reply with one word: ping",
    )
    print(resp.text)


if __name__ == "__main__":
    main()
