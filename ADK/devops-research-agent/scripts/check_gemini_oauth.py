import os
from pathlib import Path

from google import genai
from dotenv import load_dotenv


def _is_true(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes"}


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    load_dotenv(
        Path(__file__).resolve().parents[1]
        / "patterns"
        / "simple_tool_calling"
        / ".env"
    )

    use_agent_platform = _is_true(os.getenv("GOOGLE_GENAI_USE_VERTEXAI")) or _is_true(
        os.getenv("GOOGLE_GENAI_USE_ENTERPRISE")
    )
    model = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")

    if use_agent_platform:
        client = genai.Client(
            vertexai=True,
            project=_required_env("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    else:
        client = genai.Client()

    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: oauth-ok",
    )
    print(response.text)


if __name__ == "__main__":
    main()
