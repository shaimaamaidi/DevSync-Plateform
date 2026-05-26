"""
Unit tests for password helper functions.
"""

from backend.src.shared.helpers.password_helper import hash_password, verify_password


def test_hash_password_and_verify_password_round_trip() -> None:
    """
    Test that a hashed password can be verified successfully.
    """
    hashed_password = hash_password("s3cret-password")

    assert hashed_password != "s3cret-password"
    assert verify_password("s3cret-password", hashed_password) is True


def test_verify_password_rejects_wrong_password() -> None:
    """
    Test that verify_password rejects a non-matching password.
    """
    hashed_password = hash_password("s3cret-password")

    assert verify_password("wrong-password", hashed_password) is False
