from resonance.bots import BOTS
from resonance.engine import BotResult, ProjectSpec


def test_all_bots_have_system_prompt():
    for name, bot in BOTS.items():
        assert "system" in bot
        assert len(bot["system"]) > 20, f"{name} system prompt too short"


def test_all_bots_have_filename_suffix():
    for name, bot in BOTS.items():
        assert bot["filename_suffix"].endswith(".py"), name


def test_expected_bots_exist():
    expected = {"CodeBot", "APIBot", "DatabaseBot", "TestBot"}
    assert expected.issubset(set(BOTS.keys()))


def test_bot_result_creation():
    result = BotResult(
        bot_name="CodeBot",
        task="Write a function",
        output="def foo(): pass",
        success=True,
        elapsed=2.1,
    )
    assert result.success is True


def test_project_spec_defaults():
    spec = ProjectSpec(name="Test", description="desc", requirements=["a"])
    assert spec.output_dir == "output"
