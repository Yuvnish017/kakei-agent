import unicodedata


def normalize_merchant_name(
    merchant: str,
) -> str:
    """
    Perform deterministic, non-destructive normalization
    of a merchant name.

    This does NOT translate Japanese names or attempt
    to identify the business.
    """

    # Normalize Unicode representation.
    normalized = unicodedata.normalize(
        "NFKC",
        merchant,
    )

    # Normalize whitespace.
    normalized = " ".join(
        normalized.split()
    )

    return normalized.strip()