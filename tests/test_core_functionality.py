"""Core functionality tests - minimum viable version"""

import os
import sys
from datetime import UTC, datetime, timedelta

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from schemas.login import CredentialsSchema, JWTPayload  # noqa: E402
from utils.jwt import create_token_pair, verify_token  # noqa: E402


class TestJWTCore:
    """JWT core functionality tests"""

    def test_token_creation_and_verification(self):
        """Test token creation and verification"""
        # Create token pair
        access_token, refresh_token = create_token_pair(user_id=1)

        # Verify access token
        access_payload = verify_token(access_token, "access")
        assert access_payload.user_id == 1
        assert access_payload.token_type == "access"

        # Verify refresh token
        refresh_payload = verify_token(refresh_token, "refresh")
        assert refresh_payload.user_id == 1
        assert refresh_payload.token_type == "refresh"

    def test_token_type_security(self):
        """Test token type security"""
        access_token, refresh_token = create_token_pair(1)

        # Verifying with wrong type should fail
        with pytest.raises(Exception):  # noqa: B017
            verify_token(access_token, "refresh")

        with pytest.raises(Exception):  # noqa: B017
            verify_token(refresh_token, "access")

    def test_expired_token_rejection(self):
        """Test expired token rejection"""
        from utils.jwt import create_access_token

        # Create expired token
        expired_payload = JWTPayload(
            user_id=1,
            exp=datetime.now(UTC) - timedelta(minutes=1),
            token_type="access",
        )

        expired_token = create_access_token(data=expired_payload)

        with pytest.raises(Exception):  # noqa: B017
            verify_token(expired_token, "access")


class TestDataValidation:
    """Data validation tests"""

    def test_credentials_schema_validation(self):
        """Test credentials data validation"""
        # Valid credentials
        valid_creds = CredentialsSchema(username="test_user", password="password123")

        assert valid_creds.username == "test_user"
        assert valid_creds.password == "password123"

    def test_jwt_payload_validation(self):
        """Test JWT payload validation"""
        payload = JWTPayload(
            user_id=123,
            exp=datetime.now(UTC) + timedelta(hours=1),
            token_type="access",
        )

        assert payload.user_id == 123
        assert payload.token_type == "access"


class TestPasswordSecurity:
    """Password security tests"""

    def test_password_hashing(self):
        """Test password hashing"""
        from utils.password import get_password_hash, verify_password

        password = "test_password_123"
        hashed = get_password_hash(password)

        # Hashed password should be different
        assert hashed != password
        assert len(hashed) > 20  # Hash should have reasonable length

        # Verify password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test different passwords produce different hashes"""
        from utils.password import get_password_hash

        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")

        assert hash1 != hash2

    def test_same_password_different_salts(self):
        """Test same password with different salts"""
        from utils.password import get_password_hash

        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Due to different salts, hashes should be different
        assert hash1 != hash2


class TestConfigurationSecurity:
    """Configuration security tests"""

    def test_secret_key_strength(self):
        """Test secret key strength"""
        from settings.config import settings

        # SECRET_KEY should be long enough
        assert len(settings.SECRET_KEY) >= 32

        # Should not be default value
        assert settings.SECRET_KEY != "your_secret_key_here"

    def test_jwt_configuration(self):
        """Test JWT configuration"""
        from settings.config import settings

        # Check JWT configuration
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS > 0

        # Access token should be shorter than refresh token
        access_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        refresh_minutes = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        assert access_minutes < refresh_minutes


class TestUtilityFunctions:
    """Utility function tests"""

    def test_sensitive_word_filter_basic(self):
        """Test basic sensitive word filtering functionality"""
        try:
            from utils.sensitive_word_filter import SensitiveWordFilter

            # Create filter instance
            filter_instance = SensitiveWordFilter()

            # Test basic detection
            text = "This is a normal text"
            contains_sensitive, found_word = filter_instance.contains_sensitive_word(
                text
            )

            # Normal text should not contain sensitive words
            assert isinstance(contains_sensitive, bool)

        except ImportError:
            # Skip test if dependencies are not available
            pytest.skip("Sensitive word filter dependencies not available")

    def test_cache_key_generation(self):
        """Test cache key generation"""
        try:
            from utils.cache import CacheManager

            cache_manager = CacheManager()

            # Test cache key generation
            key1 = cache_manager.cache_key("user", 123, action="profile")
            key2 = cache_manager.cache_key("user", 456, action="profile")
            key3 = cache_manager.cache_key("user", 123, action="settings")

            assert isinstance(key1, str)
            assert key1 != key2  # Different parameters should produce different keys
            assert key1 != key3  # Different operations should produce different keys

        except ImportError:
            pytest.skip("Cache manager dependencies not available")


if __name__ == "__main__":
    # Allow running this file directly for testing
    pytest.main([__file__, "-v"])
