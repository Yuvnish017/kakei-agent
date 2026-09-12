import re
from datetime import date
from decimal import Decimal
from pathlib import Path

from kakei_agent.ingest.pdf import extract_text_from_pdf
from kakei_agent.models import (
    RakutenParseResult,
    RakutenParseWarning,
    RakutenTransaction,
)
from kakei_agent.normalize.merchant import (
    normalize_merchant_name,
)


DATE_PATTERN = re.compile(r"^\d{4}/\d{2}/\d{2}$")

AMOUNT_PATTERN = re.compile(
    r"^[\d,]+(?:\.\d+)?$"
)

STATEMENT_AMOUNT_PATTERN = re.compile(
    r"^([\d,]+)円$"
)

STATEMENT_MONTH_PATTERN = re.compile(
    r"(\d{4})年(\d{2})月ご請求金額"
)


def parse_amount(value: str) -> Decimal:
    return Decimal(value.replace(",", ""))


def parse_date(value: str) -> date:
    return date.fromisoformat(
        value.replace("/", "-")
    )


def is_date(value: str) -> bool:
    return bool(
        DATE_PATTERN.fullmatch(value.strip())
    )


def is_amount(value: str) -> bool:
    return bool(
        AMOUNT_PATTERN.fullmatch(value.strip())
    )


def extract_statement_metadata(
    lines: list[str],
) -> tuple[str | None, Decimal | None]:
    """
    Extract statement month and billed amount.

    Example:

        2026年08月ご請求金額
        144,588円
    """

    statement_month = None
    statement_amount = None

    for index, line in enumerate(lines):
        month_match = STATEMENT_MONTH_PATTERN.search(line)

        if month_match:
            year, month = month_match.groups()
            statement_month = f"{year}-{month}"

            if index + 1 < len(lines):
                amount_match = STATEMENT_AMOUNT_PATTERN.match(
                    lines[index + 1]
                )

                if amount_match:
                    statement_amount = parse_amount(
                        amount_match.group(1)
                    )

            break

    return statement_month, statement_amount


def find_cardholder_index(
    lines: list[str],
    start_index: int,
    max_merchant_lines: int = 5,
) -> int | None:
    """
    Find the cardholder line associated with a possible
    transaction.

    Merchant names can span multiple lines, so we allow
    a small number of lines between the transaction date
    and the cardholder marker.
    """

    end_index = min(
        start_index + max_merchant_lines + 1,
        len(lines),
    )

    for index in range(
        start_index + 1,
        end_index,
    ):
        if lines[index].startswith("本人"):
            return index

    return None


def extract_transaction_blocks(
    text: str,
) -> tuple[list[list[str]], list[RakutenParseWarning]]:
    """
    Extract transaction blocks from a Rakuten statement.

    Rakuten places statement metadata before the transaction table.
    The transaction table begins after the first occurrence of
    'ご利用明細'.

    A standard transaction looks like:

        date
        merchant
        cardholder
        payment method
        amount
        fee
        total
        billed
        carried-forward
        current-payment

    Merchant names may span multiple lines.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    blocks: list[list[str]] = []
    warnings: list[RakutenParseWarning] = []

    # ---------------------------------------------------------
    # Find the beginning of the transaction table.
    # ---------------------------------------------------------

    try:
        table_start = lines.index("ご利用明細") + 1
    except ValueError:
        return [], [
            RakutenParseWarning(
                message=(
                    "Could not find the Rakuten transaction "
                    "table marker: ご利用明細"
                )
            )
        ]

    # Only inspect lines after the transaction table begins.
    lines = lines[table_start:]

    i = 0

    while i < len(lines):

        # -----------------------------------------------------
        # A transaction must start with a date.
        # -----------------------------------------------------

        if not is_date(lines[i]):
            i += 1
            continue

        transaction_start = i

        # -----------------------------------------------------
        # The cardholder marker should occur very soon after
        # the date because merchant names may wrap, but we
        # should NOT search arbitrarily far into the document.
        #
        # Maximum of 4 merchant lines:
        #
        # date
        # merchant line 1
        # merchant line 2
        # merchant line 3
        # merchant line 4
        # 本人*
        # -----------------------------------------------------

        cardholder_index = find_cardholder_index(
            lines,
            i,
        )

        if cardholder_index is None:
            # A date does not necessarily mean that this is a
            # transaction. Rakuten's statement contains several
            # other dates in the header/metadata section.
            #
            # Therefore, simply skip it rather than generating
            # a warning.
            i += 1
            continue

        # -----------------------------------------------------
        # Payment method should immediately follow cardholder.
        # -----------------------------------------------------

        payment_index = cardholder_index + 1

        if payment_index >= len(lines):
            warnings.append(
                RakutenParseWarning(
                    message="Transaction has no payment method.",
                    line_number=table_start + transaction_start + 1,
                    context=tuple(
                        lines[
                            transaction_start:
                            min(transaction_start + 7, len(lines))
                        ]
                    ),
                )
            )

            i += 1
            continue

        payment_method = lines[payment_index]

        # -----------------------------------------------------
        # After payment method we expect exactly six monetary
        # values.
        # -----------------------------------------------------

        amount_start = payment_index + 1

        amounts: list[str] = []

        j = amount_start

        while (
            j < len(lines)
            and len(amounts) < 6
        ):
            if not is_amount(lines[j]):
                break

            amounts.append(lines[j])
            j += 1

        if len(amounts) != 6:
            warnings.append(
                RakutenParseWarning(
                    message=(
                        "Transaction does not contain "
                        "exactly six monetary fields."
                    ),
                    line_number=table_start + transaction_start + 1,
                    context=tuple(
                        lines[
                            transaction_start:
                            min(j + 3, len(lines))
                        ]
                    ),
                )
            )

            i += 1
            continue

        # -----------------------------------------------------
        # Everything between date and cardholder is merchant
        # information.
        # -----------------------------------------------------

        merchant_lines = lines[
            transaction_start + 1:
            cardholder_index
        ]

        if not merchant_lines:
            warnings.append(
                RakutenParseWarning(
                    message="Transaction has no merchant name.",
                    line_number=table_start + transaction_start + 1,
                )
            )

            i += 1
            continue

        merchant = " ".join(merchant_lines)

        block = [
            lines[transaction_start],
            merchant,
            lines[cardholder_index],
            payment_method,
            *amounts,
        ]

        blocks.append(block)

        # Move directly to the first line after this transaction.
        i = j

    return blocks, warnings


def parse_transaction_block(
    block: list[str],
) -> RakutenTransaction:

    if len(block) != 10:
        raise ValueError(
            "Expected 10 fields in transaction block, "
            f"got {len(block)}: {block}"
        )

    (
        transaction_date,
        merchant,
        cardholder,
        payment_method,
        transaction_amount,
        fee_or_interest,
        total_amount,
        billed_amount,
        carried_forward_balance,
        current_payment,
    ) = block

    return RakutenTransaction(
        transaction_date=parse_date(transaction_date),
        merchant_raw=merchant,
        merchant_normalized=normalize_merchant_name(
            merchant
        ),
        cardholder=cardholder,
        payment_method=payment_method,
        transaction_amount=parse_amount(
            transaction_amount
        ),
        fee_or_interest=parse_amount(
            fee_or_interest
        ),
        total_amount=parse_amount(
            total_amount
        ),
        billed_amount=parse_amount(
            billed_amount
        ),
        carried_forward_balance=parse_amount(
            carried_forward_balance
        ),
        current_payment=parse_amount(
            current_payment
        ),
    )


def parse_rakuten_pdf(
    pdf_path: str | Path,
) -> RakutenParseResult:

    text = extract_text_from_pdf(pdf_path)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    statement_month, statement_amount = (
        extract_statement_metadata(lines)
    )

    blocks, warnings = extract_transaction_blocks(text)

    transactions = [
        parse_transaction_block(block)
        for block in blocks
    ]

    result = RakutenParseResult(
        statement_month=statement_month,
        statement_amount=statement_amount,
        transactions=transactions,
        warnings=warnings,
    )

    reconciliation_warning = reconcile_transactions(result)

    reconciliation_warning = reconcile_transactions(result)

    if reconciliation_warning:
        result.warnings.append(
            reconciliation_warning
        )

    result.warnings.extend(
        validate_transactions(
            result.transactions
        )
    )

    return result


def reconcile_transactions(
    result: RakutenParseResult,
) -> RakutenParseWarning | None:
    """
    Compare the sum of transaction amounts against
    the statement billed amount.
    """

    if result.statement_amount is None:
        return RakutenParseWarning(
            message=(
                "Could not determine statement billed amount."
            )
        )

    transaction_total = sum(
        (
            transaction.transaction_amount
            for transaction in result.transactions
        ),
        Decimal("0"),
    )

    if transaction_total != result.statement_amount:
        return RakutenParseWarning(
            message=(
                "Transaction total does not match "
                "statement billed amount. "
                f"transactions={transaction_total}, "
                f"statement={result.statement_amount}"
            )
        )

    return None


def validate_transactions(
    transactions: list[RakutenTransaction],
) -> list[RakutenParseWarning]:
    """
    Perform structural validation on parsed transactions.

    This does not determine whether a transaction is
    financially correct. It only checks for suspicious
    structures that deserve inspection.
    """

    warnings: list[RakutenParseWarning] = []

    for index, transaction in enumerate(
        transactions,
        start=1,
    ):
        # -----------------------------------------------------
        # Check basic amount relationship.
        # -----------------------------------------------------

        expected_total = (
            transaction.transaction_amount
            + transaction.fee_or_interest
        )

        if expected_total != transaction.total_amount:
            warnings.append(
                RakutenParseWarning(
                    message=(
                        f"Transaction #{index}: "
                        "transaction amount + fee does not "
                        "equal total amount."
                    ),
                    context=(
                        transaction.merchant_raw,
                    ),
                )
            )

        # -----------------------------------------------------
        # Check billed amount.
        # -----------------------------------------------------

        if transaction.billed_amount > transaction.total_amount:
            warnings.append(
                RakutenParseWarning(
                    message=(
                        f"Transaction #{index}: "
                        "billed amount is greater than "
                        "total amount."
                    ),
                    context=(
                        transaction.merchant_raw,
                    ),
                )
            )

        # -----------------------------------------------------
        # Check negative values.
        #
        # Our current parser doesn't support negative values
        # yet, so this is mostly defensive.
        # -----------------------------------------------------

        monetary_fields = {
            "transaction_amount": (
                transaction.transaction_amount
            ),
            "fee_or_interest": (
                transaction.fee_or_interest
            ),
            "total_amount": (
                transaction.total_amount
            ),
            "billed_amount": (
                transaction.billed_amount
            ),
            "carried_forward_balance": (
                transaction.carried_forward_balance
            ),
            "current_payment": (
                transaction.current_payment
            ),
        }

        for field_name, value in monetary_fields.items():
            if value < 0:
                warnings.append(
                    RakutenParseWarning(
                        message=(
                            f"Transaction #{index}: "
                            f"{field_name} is negative."
                        ),
                        context=(
                            transaction.merchant_raw,
                        ),
                    )
                )

    return warnings
