import argparse
from pathlib import Path
from decimal import Decimal

from kakei_agent.ingest.pdf import extract_text_from_pdf
from kakei_agent.ingest.rakuten_pdf import parse_rakuten_pdf, validate_transactions


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Kakei Agent"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract raw text from a PDF",
    )

    extract_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    extract_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional output text file",
    )

    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse a Rakuten Card PDF",
    )

    parse_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect parsed Rakuten transactions",
    )

    inspect_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    summary_parser = subparsers.add_parser(
        "summary",
        help="Summarize parsed Rakuten transactions",
    )

    summary_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    args = parser.parse_args()

    if args.command == "extract":

        text = extract_text_from_pdf(args.pdf)

        if args.output:
            args.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            args.output.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"Extracted text written to: "
                f"{args.output}"
            )

        else:
            print(text)

    elif args.command == "parse":

        result = parse_rakuten_pdf(args.pdf)

        print(
            f"Statement month: "
            f"{result.statement_month}"
        )

        print(
            f"Statement amount: "
            f"¥{result.statement_amount:,.0f}"
        )

        print(
            f"Transactions: "
            f"{len(result.transactions)}"
        )

        print(
            f"Warnings: "
            f"{len(result.warnings)}"
        )

        if result.warnings:
            print("\nWarnings:")

            for warning in result.warnings:
                print(
                    f"- {warning.message}"
                )

                if warning.line_number:
                    print(
                        f"  line: "
                        f"{warning.line_number}"
                    )

                if warning.context:
                    for line in warning.context:
                        print(
                            f"    {line}"
                        )

    elif args.command == "inspect":

        result = parse_rakuten_pdf(args.pdf)

        print(
            f"Statement month: "
            f"{result.statement_month}"
        )

        print(
            f"Statement amount: "
            f"¥{result.statement_amount:,.0f}"
        )

        print(
            f"Transactions: "
            f"{len(result.transactions)}"
        )

        print()

        for index, transaction in enumerate(
                result.transactions,
                start=1,
        ):
            print(
                f"[{index:02d}] "
                f"{transaction.transaction_date} | "
                f"{transaction.merchant_raw} | "
                f"{transaction.payment_method} | "
                f"¥{transaction.transaction_amount:,.0f}"
            )

    elif args.command == "summary":

        result = parse_rakuten_pdf(args.pdf)

        transactions = result.transactions

        total = sum(
            (
                t.transaction_amount
                for t in transactions
            ),
            Decimal("0"),
        )

        payment_methods: dict[str, int] = {}

        for transaction in transactions:
            payment_methods[
                transaction.payment_method
            ] = (
                    payment_methods.get(
                        transaction.payment_method,
                        0,
                    ) + 1
            )

        print(
            f"Statement month: "
            f"{result.statement_month}"
        )

        print(
            f"Statement amount: "
            f"¥{result.statement_amount:,.0f}"
        )

        print(
            f"Transactions: "
            f"{len(transactions)}"
        )

        print(
            f"Transaction total: "
            f"¥{total:,.0f}"
        )

        print("\nPayment methods:")

        for method, count in sorted(
                payment_methods.items()
        ):
            print(
                f"  {method}: {count}"
            )

        validation_warnings = (
            validate_transactions(transactions)
        )

        print(
            f"\nValidation warnings: "
            f"{len(validation_warnings)}"
        )


if __name__ == "__main__":
    main()
