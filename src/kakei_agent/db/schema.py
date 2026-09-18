SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    statement_month TEXT NOT NULL UNIQUE,
    statement_amount INTEGER NOT NULL,

    source_file TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    statement_id INTEGER NOT NULL,

    transaction_date TEXT NOT NULL,

    merchant_raw TEXT NOT NULL,
    merchant_normalized TEXT NOT NULL,
    merchant_name TEXT NOT NULL,

    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,

    amount INTEGER NOT NULL,

    payment_method TEXT NOT NULL,

    resolution_method TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (statement_id)
        REFERENCES statements(id)
);


CREATE INDEX IF NOT EXISTS idx_transactions_statement_id
    ON transactions(statement_id);


CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(transaction_date);


CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions(category);


CREATE INDEX IF NOT EXISTS idx_transactions_merchant
    ON transactions(merchant_name);
"""