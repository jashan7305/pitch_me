from __future__ import annotations

import time

from google import genai

from config import GEMINI_API_KEY


MAX_RETRIES = 5
INITIAL_DELAY = 3.0
BACKOFF_FACTOR = 2.0


def create_client() -> genai.Client:
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_content_with_retry(
    client: genai.Client,
    *,
    model: str,
    contents,
    config=None,
):
    delay = INITIAL_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

        except Exception as exc:
            error_text = str(exc).lower()

            is_retryable = (
                "503" in error_text
                or "unavailable" in error_text
                or "deadline" in error_text
                or "timeout" in error_text
                or "temporarily" in error_text
            )

            if not is_retryable or attempt == MAX_RETRIES:
                raise

            print(
                f"Gemini request failed "
                f"(attempt {attempt}/{MAX_RETRIES}). "
                f"Retrying in {delay:.1f}s..."
            )

            time.sleep(delay)
            delay *= BACKOFF_FACTOR