from decimal import Decimal
from pathlib import Path

from kakei_agent.ingest.rakuten_pdf import (
    parse_rakuten_pdf,
    parse_transaction_block,
)


PDF_PATH = Path(
    "data/raw/statement_202608.pdf"
)


def test_parse_single_transaction():

    block = [
        "2026/07/31",
        "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ",
        "本人*",
        "1回払い",
        "5,000",
        "0",
        "5,000",
        "5,000",
        "0",
        "5,000",
    ]

    transaction = parse_transaction_block(block)

    assert (
        transaction.transaction_date.isoformat()
        == "2026-07-31"
    )

    assert (
        transaction.merchant_raw
        == "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ"
    )

    assert transaction.cardholder == "本人*"

    assert (
        transaction.payment_method
        == "1回払い"
    )

    assert (
        transaction.transaction_amount
        == Decimal("5000")
    )

    assert (
        transaction.fee_or_interest
        == Decimal("0")
    )

    assert (
        transaction.total_amount
        == Decimal("5000")
    )

    assert (
        transaction.billed_amount
        == Decimal("5000")
    )

    assert (
        transaction.carried_forward_balance
        == Decimal("0")
    )

    assert (
        transaction.current_payment
        == Decimal("5000")
    )


def test_parse_statement():

    result = parse_rakuten_pdf(PDF_PATH)

    assert result.statement_month == "2026-08"

    assert (
        result.statement_amount
        == Decimal("144588")
    )

    assert len(result.transactions) == 72


def test_statement_reconciles():

    result = parse_rakuten_pdf(PDF_PATH)

    assert result.warnings == []


def test_first_transaction():

    result = parse_rakuten_pdf(PDF_PATH)

    first = result.transactions[0]

    assert (
        first.transaction_date.isoformat()
        == "2026-07-31"
    )

    assert (
        first.merchant_raw
        == "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ"
    )

    assert (
            first.merchant_normalized
            == "GPモバイルパスモチヤ-ジ"
    )

    assert (
        first.transaction_amount
        == Decimal("5000")
    )


def test_statement_metadata_is_not_parsed_as_transaction():

    result = parse_rakuten_pdf(PDF_PATH)

    first = result.transactions[0]

    assert (
        first.transaction_date.isoformat()
        == "2026-07-31"
    )

    assert (
        first.merchant_raw
        == "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ"
    )

    # Statement-level payment date must not appear
    # as a transaction.
    assert all(
        transaction.transaction_date.isoformat()
        != "2026-08-24"
        for transaction in result.transactions
    )
