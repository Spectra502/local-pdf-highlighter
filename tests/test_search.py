import os
import fitz
import pytest
from src.indexer import Indexer
from src.search import Searcher

@pytest.fixture(scope="module")
def synthetic_pdf_path(tmp_path_factory):
    # Create a synthetic PDF using PyMuPDF
    pdf_path = str(tmp_path_factory.mktemp("data") / "test_doc.pdf")
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page()
    page1.insert_text((50, 50), "This is a simple test document.", fontsize=12)
    page1.insert_text((50, 100), "The warranty on this battery replacement is valid for three years.", fontsize=12)
    page1.insert_text((50, 150), "Short text.", fontsize=12) # Will be included because length >= 10

    # Page 2
    page2 = doc.new_page()
    page2.insert_text((50, 50), "How to clean the product: use a damp cloth and mild soap.", fontsize=12)
    page2.insert_text((50, 100), "Do not submerge the battery in water, it will damage the internal components.", fontsize=12)

    doc.save(pdf_path)
    doc.close()

    return pdf_path

def test_indexer_extraction(synthetic_pdf_path):
    indexer = Indexer()
    index, embeddings = indexer.index_pdf(synthetic_pdf_path)

    # We expect 5 blocks (length >= 10, "Short text." is 11 chars)
    assert len(index) == 5

    # Check if text is correctly extracted
    texts = [item["text"] for item in index]
    assert any("warranty on this battery replacement" in t for t in texts)

    # Check bbox extraction (4 coordinates)
    assert len(index[0]["bbox"]) == 4

def test_indexer_embeddings(synthetic_pdf_path):
    indexer = Indexer()
    index, embeddings = indexer.index_pdf(synthetic_pdf_path)

    # Check embedding shape
    assert embeddings is not None
    assert embeddings.shape == (5, 256) # 5 blocks, 256 dims (truncate_dim=256)

    # Check model device
    assert indexer.model.device.type == "cpu"

def test_searcher_logic(synthetic_pdf_path):
    indexer = Indexer()
    indexer.index_pdf(synthetic_pdf_path)

    searcher = Searcher(indexer)
    results = searcher.search("battery warranty conditions", k=2)

    assert len(results) == 2

    # The top result should ideally be the warranty text
    assert "warranty" in results[0]["text"].lower()

    # Check result structure
    assert "page_num" in results[0]
    assert "bbox" in results[0]
    assert "score" in results[0]
