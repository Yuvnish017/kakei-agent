from __future__ import annotations

from pathlib import Path

from kakei_agent.db.database import get_connection
from kakei_agent.normalize.merchant_resolver import resolve_merchant


def import_statement(
    statement,
    source_file: Path,
    db_path: Path | None = None,
) -> int:
    """
    Store a parsed Rakuten statement and its classified
    transactions in SQLite.

    Returns the number of transactions inserted.
    """

    connection = get_connection(
        db_path if db_path is not None else Path("data/kakei.db")
    )

    try:
        # -----------------------------------------------------
        # Check whether this statement was already imported
        # -----------------------------------------------------
        existing = connection.execute(
            """
            SELECT id
            FROM statements
            WHERE statement_month = ?
            """,
            (statement.statement_month,),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                f"Statement {statement.statement_month} "
                "already exists in the database."
            )

        # -----------------------------------------------------
        # Insert statement
        # -----------------------------------------------------
        cursor = connection.execute(
            """
            INSERT INTO statements (
                statement_month,
                statement_amount,
                source_file
            )
            VALUES (?, ?, ?)
            """,
            (
                statement.statement_month,
                int(statement.statement_amount),
                str(source_file),
            ),
        )

        statement_id = cursor.lastrowid

        # -----------------------------------------------------
        # Insert transactions
        # -----------------------------------------------------
        inserted = 0

        for transaction in statement.transactions:

            (
                merchant_name,
                category,
                resolution_method,
            ) = resolve_merchant(
                transaction.merchant_normalized
            )

            connection.execute(
                """
                INSERT INTO transactions (
                    statement_id,
                    transaction_date,
                    merchant_raw,
                    merchant_normalized,
                    merchant_name,
                    category,
                    subcategory,
                    amount,
                    payment_method,
                    resolution_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    statement_id,
                    transaction.transaction_date.isoformat(),
                    transaction.merchant_raw,
                    transaction.merchant_normalized,
                    merchant_name,
                    category.name,
                    category.subcategory,
                    int(transaction.transaction_amount),
                    transaction.payment_method,
                    resolution_method,
                ),
            )

            inserted += 1

        connection.commit()

        return inserted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()