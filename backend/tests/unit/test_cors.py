"""
Testes unitários para config/cors.py.
parse_allowed_origins() é lógica pura — sem I/O externo.
"""
from config.cors import parse_allowed_origins


def test_comma_separated():
    result = parse_allowed_origins("http://localhost:3000,https://example.com")
    assert result == ["http://localhost:3000", "https://example.com"]


def test_semicolon_separated():
    result = parse_allowed_origins("http://localhost:3000;https://example.com")
    assert result == ["http://localhost:3000", "https://example.com"]


def test_mixed_separators():
    result = parse_allowed_origins("http://localhost:3000,https://example.com;https://other.com")
    assert len(result) == 3


def test_strips_whitespace():
    result = parse_allowed_origins("  http://localhost:3000 , https://example.com  ")
    assert "http://localhost:3000" in result
    assert "https://example.com" in result


def test_strips_single_quotes():
    result = parse_allowed_origins("'http://localhost:3000','https://example.com'")
    assert "http://localhost:3000" in result
    assert "https://example.com" in result


def test_strips_double_quotes():
    result = parse_allowed_origins('"http://localhost:3000","https://example.com"')
    assert "http://localhost:3000" in result
    assert "https://example.com" in result


def test_strips_trailing_slash():
    result = parse_allowed_origins("http://localhost:3000/")
    assert result == ["http://localhost:3000"]


def test_single_origin():
    result = parse_allowed_origins("http://localhost:3000")
    assert result == ["http://localhost:3000"]


def test_ignores_empty_entries():
    result = parse_allowed_origins("http://localhost:3000,,https://example.com")
    assert len(result) == 2
    assert "" not in result


def test_returns_list():
    result = parse_allowed_origins("http://localhost:3000")
    assert isinstance(result, list)
