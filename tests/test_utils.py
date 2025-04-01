import pytest
from link.router import generate_short_code

def test_generate_short_code():
    short_code = generate_short_code()
    assert isinstance(short_code, str)
    assert len(short_code) == 6  # Длина должна быть 6 символов

def test_generate_unique_short_code():
    codes = {generate_short_code() for _ in range(100)}
    assert len(codes) == 100  # Все коды уникальны