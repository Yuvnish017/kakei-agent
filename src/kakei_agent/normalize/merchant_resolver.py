from __future__ import annotations

import unicodedata

from kakei_agent.models.category import Category
from kakei_agent.normalize.rules import MERCHANT_RULES


def normalize_for_matching(value: str) -> str:
    """
    Normalize merchant text for deterministic rule matching.

    NFKC converts half-width Japanese characters such as:
        ﾏｲﾊﾞｽｹﾂﾄ
    into:
        マイバスケツト
    """

    value = unicodedata.normalize("NFKC", value)

    # Normalize whitespace.
    value = " ".join(value.split())

    return value.strip()


def resolve_merchant(
    merchant_normalized: str,
) -> tuple[str, Category, str]:
    """
    Resolve a merchant into:

        merchant_name
        category
        resolution_method

    resolution_method is either:
        "rule"
        "unresolved"
    """

    merchant_for_matching = normalize_for_matching(
        merchant_normalized
    )

    for rule in MERCHANT_RULES:
        pattern = normalize_for_matching(rule.pattern)

        if pattern in merchant_for_matching:
            return (
                rule.merchant_name,
                rule.category,
                "rule",
            )

    return (
        merchant_normalized,
        Category(
            name="Other",
            subcategory="Uncategorized",
        ),
        "unresolved",
    )