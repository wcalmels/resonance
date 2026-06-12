from resonance.output_clean import clean_llm_output


def test_strips_python_fence():
    raw = "```python\ndef foo():\n    return 1\n```"
    assert clean_llm_output(raw) == "def foo():\n    return 1\n"


def test_strips_bare_fence():
    raw = "```\nimport os\n```"
    assert clean_llm_output(raw) == "import os\n"


def test_plain_code_unchanged():
    raw = "def bar():\n    pass\n"
    assert clean_llm_output(raw) == raw


def test_preserves_error_output():
    raw = "# Error: rate limit"
    assert clean_llm_output(raw) == raw


def test_live_fixture_pattern():
    raw = (
        "```python\n"
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "```"
    )
    cleaned = clean_llm_output(raw)
    assert cleaned.startswith("from fastapi")
    assert "```" not in cleaned
