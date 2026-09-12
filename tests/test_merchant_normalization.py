from kakei_agent.normalize.merchant import (
    normalize_merchant_name,
)


def test_normalize_whitespace():
    assert (
        normalize_merchant_name(
            "楽天ＳＰ　マクドナルドアプリ"
        )
        == "楽天SP マクドナルドアプリ"
    )


def test_normalize_regular_text():
    assert (
        normalize_merchant_name(
            "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ"
        )
        == "GPモバイルパスモチヤ-ジ"
    )


def test_normalize_does_not_remove_merchant_information():
    merchant = (
        "LINKEDIN*P3046857181利用国SG"
    )

    normalized = normalize_merchant_name(
        merchant
    )

    assert "LINKEDIN" in normalized
    assert "P3046857181" in normalized
    assert "SG" in normalized