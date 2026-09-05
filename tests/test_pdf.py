from pathlib import Path

from kakei_agent.ingest.pdf import extract_text_from_pdf


def test_extract_rakuten_statement():
    pdf_path = Path("data/raw/statement_202608.pdf")

    text = extract_text_from_pdf(pdf_path)

    assert "ご利用代金請求明細書" in text
    assert "利用日" in text
    assert "利用店名" in text
    assert "利用金額" in text
    assert "2026/07/31" in text
    assert "GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ" in text