from __future__ import annotations

from pathlib import Path

from kakei_agent.db.database import get_connection


DEFAULT_DB_PATH = Path("data/kakei.db")


def get_statement_summary(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict:
    """
    Return high-level spending statistics for a statement month.
    """

    connection = get_connection(db_path)

    try:
        statement = connection.execute(
            """
            SELECT
                id,
                statement_month,
                statement_amount,
                source_file
            FROM statements
            WHERE statement_month = ?
            """,
            (statement_month,),
        ).fetchone()

        if statement is None:
            raise ValueError(
                f"Statement {statement_month} "
                "was not found."
            )

        transaction_stats = connection.execute(
            """
            SELECT
                COUNT(*) AS transaction_count,
                COALESCE(SUM(amount), 0) AS transaction_total,
                COALESCE(AVG(amount), 0) AS average_transaction,
                COALESCE(MIN(amount), 0) AS smallest_transaction,
                COALESCE(MAX(amount), 0) AS largest_transaction
            FROM transactions
            WHERE statement_id = ?
            """,
            (statement["id"],),
        ).fetchone()

        return {
            "statement_month": statement["statement_month"],
            "statement_amount": statement["statement_amount"],
            "transaction_count": transaction_stats[
                "transaction_count"
            ],
            "transaction_total": transaction_stats[
                "transaction_total"
            ],
            "average_transaction": transaction_stats[
                "average_transaction"
            ],
            "smallest_transaction": transaction_stats[
                "smallest_transaction"
            ],
            "largest_transaction": transaction_stats[
                "largest_transaction"
            ],
        }

    finally:
        connection.close()


def get_category_totals(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """
    Return spending totals grouped by category/subcategory.
    """

    connection = get_connection(db_path)

    try:
        rows = connection.execute(
            """
            SELECT
                t.category,
                t.subcategory,
                COUNT(*) AS transaction_count,
                SUM(t.amount) AS total_amount
            FROM transactions t
            JOIN statements s
                ON s.id = t.statement_id
            WHERE s.statement_month = ?
            GROUP BY
                t.category,
                t.subcategory
            ORDER BY
                total_amount DESC
            """,
            (statement_month,),
        ).fetchall()

        return [
            {
                "category": row["category"],
                "subcategory": row["subcategory"],
                "transaction_count": row["transaction_count"],
                "total_amount": row["total_amount"],
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_merchant_totals(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """
    Return spending totals grouped by canonical merchant.
    """

    connection = get_connection(db_path)

    try:
        rows = connection.execute(
            """
            SELECT
                merchant_name,
                category,
                subcategory,
                COUNT(*) AS transaction_count,
                SUM(amount) AS total_amount
            FROM transactions t
            JOIN statements s
                ON s.id = t.statement_id
            WHERE s.statement_month = ?
            GROUP BY
                merchant_name,
                category,
                subcategory
            ORDER BY
                total_amount DESC
            """,
            (statement_month,),
        ).fetchall()

        return [
            {
                "merchant_name": row["merchant_name"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "transaction_count": row["transaction_count"],
                "total_amount": row["total_amount"],
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_unresolved_transactions(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """
    Return transactions that were not resolved by a rule.
    """

    connection = get_connection(db_path)

    try:
        rows = connection.execute(
            """
            SELECT
                t.transaction_date,
                t.merchant_raw,
                t.merchant_normalized,
                t.amount
            FROM transactions t
            JOIN statements s
                ON s.id = t.statement_id
            WHERE
                s.statement_month = ?
                AND t.resolution_method = 'unresolved'
            ORDER BY
                t.transaction_date DESC
            """,
            (statement_month,),
        ).fetchall()

        return [
            {
                "transaction_date": row["transaction_date"],
                "merchant_raw": row["merchant_raw"],
                "merchant_normalized": row[
                    "merchant_normalized"
                ],
                "amount": row["amount"],
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_category_breakdown(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """
    Return category totals with percentage of statement spending.
    """

    categories = get_category_totals(
        statement_month,
        db_path,
    )

    total = sum(
        category["total_amount"]
        for category in categories
    )

    if total == 0:
        return categories

    for category in categories:
        category["percentage"] = (
            category["total_amount"] / total
        ) * 100

    return categories


def get_top_level_category_totals(
    statement_month: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    connection = get_connection(db_path)

    try:
        rows = connection.execute(
            """
            SELECT
                t.category,
                COUNT(*) AS transaction_count,
                SUM(t.amount) AS total_amount
            FROM transactions t
            JOIN statements s ON s.id = t.statement_id
            WHERE s.statement_month = ?
            GROUP BY t.category
            ORDER BY total_amount DESC
            """,
            (statement_month,),
        ).fetchall()

        return [
            {
                "category": row["category"],
                "transaction_count": row["transaction_count"],
                "total_amount": row["total_amount"],
            }
            for row in rows
        ]

    finally:
        connection.close()
