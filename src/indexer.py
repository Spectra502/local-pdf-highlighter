import fitz
from sentence_transformers import SentenceTransformer
import numpy as np

class Indexer:
    def __init__(self):
        self.model = None
        self.pdf_path = None
        self.index = []
        self.embeddings = None

    def load_model(self):
        if self.model is None:
            self.model = SentenceTransformer("google/embeddinggemma-2", device="cpu", truncate_dim=256)

    def clear(self):
        self.pdf_path = None
        self.index = []
        self.embeddings = None

    def index_pdf(self, pdf_path, progress_callback=None):
        self.load_model()
        self.pdf_path = pdf_path
        self.index = []
        self.embeddings = None

        doc = fitz.open(pdf_path)
        blocks_to_encode = []

        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            for block in blocks:
                # block: (x0, y0, x1, y1, "text", block_no, block_type)
                # block_type 0 is text
                if len(block) >= 7 and block[6] == 0:
                    text = block[4].strip()
                    if len(text) >= 10:
                        bbox = block[:4]

                        self.index.append({
                            "page_num": page_num,
                            "text": text,
                            "bbox": bbox
                        })
                        blocks_to_encode.append(text)

            if progress_callback:
                progress_callback(int((page_num + 1) / total_pages * 50)) # 50% for extraction

        if blocks_to_encode:
            # Batch encode
            # To show some progress during encoding, we could chunk it,
            # but for simplicity, we encode all and update to 100%
            self.embeddings = self.model.encode(
                blocks_to_encode,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        else:
            self.embeddings = np.array([])

        if progress_callback:
            progress_callback(100) # 100% done

        doc.close()

        return self.index, self.embeddings
