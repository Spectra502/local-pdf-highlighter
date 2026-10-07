# Local PDF Semantic Search

A lightweight, offline-first Python desktop application that allows a user to select a PDF document, search it using natural language, and view the top-matching passages visually highlighted directly inside the PDF.

It uses Google's `EmbeddingGemma-2` embedding model on CPU to semantically search your PDF files with high privacy (no internet required).

## Features

- Local processing: Your files stay on your machine.
- High-quality embeddings using `EmbeddingGemma-2`.
- Matryoshka Representation Learning (MRL) truncation to 256 dimensions to save memory.
- UI built with Tkinter, minimal dependencies.
- Generates a highlighted copy of the PDF and automatically opens it in your default viewer.

## Requirements

- Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Start the GUI application:

```bash
python -m src.app
```

1. Click "Select PDF" and browse to your file.
2. Wait for the indexing process to complete.
3. Enter your natural language search query and hit "Search".
4. Review the top excerpts.
5. Click "Highlight & Open PDF" to view the annotated copy in your system's default PDF viewer.

## Testing

You can run the unit tests with `pytest`:

```bash
pip install pytest
pytest tests/
```
