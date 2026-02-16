from bte_wage_extraction.linking import normalize_join_value, parse_eur_amount


def test_normalize_join_value_roman() -> None:
    assert normalize_join_value("IV") == "4"


def test_parse_eur_amount_pt_format() -> None:
    assert parse_eur_amount("1.366,10 €") == 1366.10


def test_parse_eur_amount_invalid() -> None:
    assert parse_eur_amount("abc") is None
