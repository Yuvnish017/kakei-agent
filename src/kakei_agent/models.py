from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class RakutenTransaction:
    transaction_date: date
    merchant_raw: str
    cardholder: str
    payment_method: str

    transaction_amount: Decimal
    fee_or_interest: Decimal
    total_amount: Decimal
    billed_amount: Decimal
    carried_forward_balance: Decimal
    current_payment: Decimal


@dataclass(frozen=True)
class RakutenParseWarning:
    message: str
    line_number: int | None = None
    context: tuple[str, ...] = ()


@dataclass
class RakutenParseResult:
    statement_month: str | None
    statement_amount: Decimal | None

    transactions: list[RakutenTransaction] = field(
        default_factory=list
    )

    warnings: list[RakutenParseWarning] = field(
        default_factory=list
    )