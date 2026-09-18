from kakei_agent.db.database import get_connection


def test_num_statements_and_transactions():
    c = get_connection()

    statements = c.execute("SELECT COUNT(*) AS count FROM statements").fetchone()["count"]

    transactions = c.execute("SELECT COUNT(*) AS count FROM transactions").fetchone()["count"]

    c.close()

    assert statements == 1
    assert transactions == 72
