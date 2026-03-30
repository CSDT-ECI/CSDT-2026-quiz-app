"""Tests for utility functions in app/modules/utils.py."""
import string
from datetime import datetime, timezone

from bson import ObjectId

from app.modules.utils import (
    check_password,
    generate_code,
    generate_password,
    json_decoder,
)


class TestGenerateCode:
    def test_default_length(self):
        code = generate_code()
        assert len(code) == 6

    def test_custom_length(self):
        code = generate_code(10)
        assert len(code) == 10

    def test_zero_length_returns_empty_string(self):
        assert generate_code(0) == ""

    def test_length_one_from_allowed_charset(self):
        allowed = set(string.ascii_lowercase + string.digits)
        assert generate_code(1) in allowed

    def test_only_lowercase_and_digits(self):
        allowed = set(string.ascii_lowercase + string.digits)
        code = generate_code(100)
        assert all(c in allowed for c in code)

    def test_returns_string(self):
        assert isinstance(generate_code(), str)

    def test_different_codes(self):
        codes = {generate_code() for _ in range(50)}
        assert len(codes) > 1


class TestGeneratePassword:
    def test_returns_hash_not_plaintext(self):
        password = "mysecretpassword"
        hashed = generate_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

    def test_different_hashes_for_same_password(self):
        h1 = generate_password("test123")
        h2 = generate_password("test123")
        assert h1 != h2


class TestCheckPassword:
    def test_correct_password(self):
        password = "correcthorse"
        hashed = generate_password(password)
        assert check_password(hashed, password) is True

    def test_incorrect_password(self):
        hashed = generate_password("correcthorse")
        assert check_password(hashed, "wrongpassword") is False

    def test_empty_password(self):
        hashed = generate_password("something")
        assert check_password(hashed, "") is False


class TestJsonDecoder:
    def test_with_objectid(self):
        oid = ObjectId()
        data = {"_id": oid, "name": "test"}
        result = json_decoder(data)
        assert result["name"] == "test"
        assert isinstance(result["_id"], dict)

    def test_with_list(self):
        data = [{"a": 1}, {"b": 2}]
        result = json_decoder(data)
        assert len(result) == 2
        assert result[0]["a"] == 1

    def test_with_simple_dict(self):
        data = {"key": "value", "num": 42}
        result = json_decoder(data)
        assert result == data

    def test_with_nested_objectid(self):
        data = {"user": {"_id": ObjectId(), "name": "test"}}
        result = json_decoder(data)
        assert result["user"]["name"] == "test"

    def test_with_none(self):
        assert json_decoder(None) is None

    def test_with_empty_list(self):
        assert json_decoder([]) == []

    def test_with_empty_dict(self):
        assert json_decoder({}) == {}

    def test_with_datetime_uses_bson_extended_json(self):
        dt = datetime(2020, 6, 15, 12, 30, 0, tzinfo=timezone.utc)
        result = json_decoder({"created": dt})
        assert "created" in result
        assert isinstance(result["created"], dict)
        assert "$date" in result["created"]
