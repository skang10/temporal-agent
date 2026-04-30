from src.config import PROJECT_ROOT, Settings


def test_cors_origins_default():
    s = Settings()
    assert "http://localhost:3000" in s.cors_origins


def test_cors_origins_configurable():
    s = Settings(cors_origins=["https://app.example.com"])
    assert s.cors_origins == ["https://app.example.com"]


def test_env_file_uses_project_root():
    assert Settings.model_config["env_file"] == PROJECT_ROOT / ".env"
