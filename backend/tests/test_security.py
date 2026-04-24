"""安全模块测试"""

from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPassword:
    """密码测试"""

    def test_hash_and_verify(self):
        """测试密码哈希和验证"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_different_hashes(self):
        """测试同一密码产生不同哈希"""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # bcrypt 每次产生不同的 salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWT:
    """JWT 测试"""

    def test_create_and_decode(self):
        """测试创建和解析 token"""
        data = {"sub": "user-123", "role": "user"}
        token = create_access_token(data)

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    def test_expired_token(self):
        """测试过期 token"""
        data = {"sub": "user-123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        decoded = decode_token(token)
        assert decoded is None  # 过期应返回 None

    def test_invalid_token(self):
        """测试无效 token"""
        assert decode_token("invalid.token.here") is None
        assert decode_token("") is None
