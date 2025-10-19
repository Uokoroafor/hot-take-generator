import pytest
import os
from unittest.mock import patch
from app.core.config import Settings, settings

class TestSettings:
    def test_default_settings(self):
        test_settings = Settings()
        assert test_settings.openai_api_key is None
        assert test_settings.anthropic_api_key is None
        assert test_settings.environment == "development"
        assert test_settings.debug is True

    def test_settings_with_env_vars(self):
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key',
            'ENVIRONMENT': 'production',
            'DEBUG': 'false'
        }):
            test_settings = Settings()
            assert test_settings.openai_api_key == 'test-openai-key'
            assert test_settings.anthropic_api_key == 'test-anthropic-key'
            assert test_settings.environment == 'production'
            assert test_settings.debug is False

    def test_settings_partial_env_vars(self):
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'only-openai-key',
        }, clear=True):
            test_settings = Settings()
            assert test_settings.openai_api_key == 'only-openai-key'
            assert test_settings.anthropic_api_key is None
            assert test_settings.environment == "development"  # default
            assert test_settings.debug is True  # default

    def test_debug_string_conversion(self):
        # Test various string representations of boolean values
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'DEBUG': env_value}, clear=True):
                test_settings = Settings()
                assert test_settings.debug == expected, f"Failed for {env_value}"

    def test_global_settings_instance(self):
        assert settings is not None
        assert isinstance(settings, Settings)

class TestConfigIntegration:
    def test_settings_in_agents(self):
        # Test that settings can be used for API key configuration
        test_settings = Settings(
            openai_api_key="test-openai",
            anthropic_api_key="test-anthropic"
        )

        assert test_settings.openai_api_key == "test-openai"
        assert test_settings.anthropic_api_key == "test-anthropic"

    def test_environment_specific_behavior(self):
        # Test production vs development settings
        prod_settings = Settings(environment="production", debug=False)
        dev_settings = Settings(environment="development", debug=True)

        assert prod_settings.environment == "production"
        assert prod_settings.debug is False

        assert dev_settings.environment == "development"
        assert dev_settings.debug is True

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_without_env_file(self):
        # Test settings when no .env file or environment variables exist
        test_settings = Settings()

        assert test_settings.openai_api_key is None
        assert test_settings.anthropic_api_key is None
        assert test_settings.environment == "development"
        assert test_settings.debug is True