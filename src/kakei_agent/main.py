import argparse
from pathlib import Path
from decimal import Decimal

from kakei_agent.ingest.pdf import extract_text_from_pdf
from kakei_agent.ingest.rakuten_pdf import parse_rakuten_pdf, validate_transactions
from kakei_agent.normalize.merchant_resolver import (
    resolve_merchant,
)
from kakei_agent.db.importer import import_statement
from kakei_agent.analytics.spending import (
    get_statement_summary,
    get_category_breakdown,
    get_top_level_category_totals,
    get_merchant_totals,
    get_unresolved_transactions,
)


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

    classify_parser = subparsers.add_parser(
        "classify",
        help="Classify Rakuten transactions",
    )

    classify_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import a Rakuten statement into SQLite",
    )

    import_parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF statement",
    )

    analytics_parser = subparsers.add_parser(
        "analytics",
        help="Analyze spending for a statement month",
    )

    analytics_parser.add_argument(
        "statement_month",
        help="Statement month, e.g. 2026-08",
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

    elif args.command == "classify":

        result = parse_rakuten_pdf(args.pdf)

        for index, transaction in enumerate(
                result.transactions,
                start=1,
        ):
            (
                merchant,
                category,
                method,
            ) = resolve_merchant(
                transaction.merchant_normalized
            )

            print(
                f"[{index:02d}] "
                f"{transaction.transaction_date} | "
                f"{transaction.merchant_raw} | "
                f"→ {merchant} | "
                f"{category.name} / "
                f"{category.subcategory} | "
                f"¥{transaction.transaction_amount:,.0f} | "
                f"{method}"
            )

    elif args.command == "import":

        result = parse_rakuten_pdf(args.pdf)

        inserted = import_statement(
            statement=result,
            source_file=args.pdf,
        )

        print(
            f"Imported statement: "
            f"{result.statement_month}"
        )

        print(
            f"Statement amount: "
            f"¥{result.statement_amount:,.0f}"
        )

        print(
            f"Transactions inserted: "
            f"{inserted}"
        )

    elif args.command == "analytics":

        statement_month = args.statement_month

        summary = get_statement_summary(
            statement_month
        )

        categories = get_category_breakdown(statement_month)
        top_level_categories = get_top_level_category_totals(statement_month)

        merchants = get_merchant_totals(
            statement_month
        )

        unresolved = get_unresolved_transactions(
            statement_month
        )

        print(
            f"Statement month: "
            f"{summary['statement_month']}"
        )

        print(
            f"Statement amount: "
            f"¥{summary['statement_amount']:,.0f}"
        )

        print(
            f"Transactions: "
            f"{summary['transaction_count']}"
        )

        print(
            f"Transaction total: "
            f"¥{summary['transaction_total']:,.0f}"
        )

        print(
            f"Average transaction: "
            f"¥{summary['average_transaction']:,.0f}"
        )

        print(
            f"Smallest transaction: "
            f"¥{summary['smallest_transaction']:,.0f}"
        )

        print(
            f"Largest transaction: "
            f"¥{summary['largest_transaction']:,.0f}"
        )

        print("\nTop-level categories:")
        for category in top_level_categories:
            print(
                f"  {category['category']} | "
                f"¥{category['total_amount']:,.0f} | "
                f"{category['transaction_count']} transactions"
            )

        print("\nCategories:")

        for category in categories:
            print(
                f"  {category['category']} / "
                f"{category['subcategory']} | "
                f"¥{category['total_amount']:,.0f} | "
                f"{category['percentage']:.1f}% | "
                f"{category['transaction_count']} transactions"
            )

        print("\nTop merchants:")

        for merchant in merchants[:10]:
            print(
                f"  {merchant['merchant_name']} | "
                f"¥{merchant['total_amount']:,.0f} | "
                f"{merchant['transaction_count']} transactions"
            )

        print(
            f"\nUnresolved transactions: "
            f"{len(unresolved)}"
        )

        if unresolved:

            for transaction in unresolved:
                print(
                    f"  {transaction['transaction_date']} | "
                    f"{transaction['merchant_raw']} | "
                    f"¥{transaction['amount']:,.0f}"
                )


if __name__ == "__main__":
    main()
