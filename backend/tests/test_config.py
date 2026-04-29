import pytest
from pydantic import ValidationError

from src.config import PROJECT_ROOT, Settings


def test_rejects_default_secret_key():
    with pytest.raises(ValidationError, match="secret_key"):
        Settings(secret_key="change-me", jwt_secret="secure-value-abc123")


def test_rejects_default_jwt_secret():
    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(secret_key="secure-value-abc123", jwt_secret="change-me")


def test_accepts_valid_secrets():
    s = Settings(secret_key="secure-value-abc123", jwt_secret="another-secure-value")
    assert s.secret_key == "secure-value-abc123"
    assert s.jwt_secret == "another-secure-value"


def test_cors_origins_default():
    s = Settings(secret_key="secure-value-abc123", jwt_secret="another-secure-value")
    assert "http://localhost:3000" in s.cors_origins


def test_cors_origins_configurable():
    s = Settings(
        secret_key="secure-value-abc123",
        jwt_secret="another-secure-value",
        cors_origins=["https://app.example.com"],
    )
    assert s.cors_origins == ["https://app.example.com"]


def test_env_file_uses_project_root():
    assert Settings.model_config["env_file"] == PROJECT_ROOT / ".env"
