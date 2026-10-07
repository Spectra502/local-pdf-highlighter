import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from .indexer import Indexer
from .search import Searcher
from .highlighter import highlight_pdf, open_pdf

class PDFSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local PDF Semantic Search")
        self.root.geometry("800x600")

        self.indexer = Indexer()
        self.searcher = Searcher(self.indexer)

        self.current_pdf = None
        self.current_results = []

        self.setup_ui()

    def setup_ui(self):
        # Top Bar
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        self.btn_select_pdf = ttk.Button(top_frame, text="Select PDF", command=self.select_pdf)
        self.btn_select_pdf.pack(side=tk.LEFT, padx=5)

        self.lbl_pdf_path = ttk.Label(top_frame, text="No PDF selected", foreground="gray")
        self.lbl_pdf_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_clear = ttk.Button(top_frame, text="Clear / Load New Document", command=self.clear_document)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)

        # Progress Bar
        progress_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        progress_frame.pack(fill=tk.X)

        self.lbl_status = ttk.Label(progress_frame, text="Ready")
        self.lbl_status.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Search Bar
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        self.entry_search = ttk.Entry(search_frame, font=("Arial", 12))
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_search.bind("<Return>", lambda event: self.perform_search())

        self.btn_search = ttk.Button(search_frame, text="Search", command=self.perform_search)
        self.btn_search.pack(side=tk.LEFT, padx=5)

        # Configuration options (k and threshold)
        config_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        config_frame.pack(fill=tk.X)

        ttk.Label(config_frame, text="Top K:").pack(side=tk.LEFT, padx=(5, 2))
        self.spin_k = ttk.Spinbox(config_frame, from_=1, to=20, width=5)
        self.spin_k.set(3)
        self.spin_k.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(config_frame, text="Threshold:").pack(side=tk.LEFT, padx=(5, 2))
        self.spin_threshold = ttk.Spinbox(config_frame, from_=0.0, to=1.0, increment=0.05, width=5)
        self.spin_threshold.set(0.0)
        self.spin_threshold.pack(side=tk.LEFT)

        # Results View
        results_frame = ttk.Frame(self.root, padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget for results
        self.txt_results = tk.Text(results_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 11))

        scrollbar = ttk.Scrollbar(results_frame, command=self.txt_results.yview)
        self.txt_results.configure(yscrollcommand=scrollbar.set)

        self.txt_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action Buttons
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X)

        self.btn_highlight = ttk.Button(action_frame, text="Highlight & Open PDF", command=self.highlight_and_open)
        self.btn_highlight.pack(side=tk.RIGHT, padx=5)

        self.update_ui_state()

    def update_ui_state(self):
        has_pdf = self.current_pdf is not None
        has_results = len(self.current_results) > 0

        self.btn_search.state(['!disabled'] if has_pdf else ['disabled'])
        self.entry_search.state(['!disabled'] if has_pdf else ['disabled'])
        self.btn_highlight.state(['!disabled'] if has_results else ['disabled'])

    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        self.current_pdf = file_path
        self.lbl_pdf_path.config(text=file_path, foreground="black")
        self.btn_select_pdf.state(['disabled'])
        self.btn_clear.state(['disabled'])
        self.lbl_status.config(text="Indexing...")
        self.progress['value'] = 0

        # Run indexing in a background thread to keep UI responsive
        threading.Thread(target=self._index_pdf_thread, args=(file_path,), daemon=True).start()

    def _index_pdf_thread(self, file_path):
        try:
            self.indexer.index_pdf(file_path, progress_callback=self._update_progress)
            self.root.after(0, self._indexing_complete)
        except Exception as e:
            self.root.after(0, lambda: self._indexing_error(str(e)))

    def _update_progress(self, value):
        self.root.after(0, lambda: self._set_progress(value))

    def _set_progress(self, value):
        self.progress['value'] = value
        if value < 50:
            self.lbl_status.config(text="Extracting text...")
        elif value < 100:
            self.lbl_status.config(text="Encoding embeddings...")
        else:
            self.lbl_status.config(text="Ready")

    def _indexing_complete(self):
        self.lbl_status.config(text=f"Indexed {len(self.indexer.index)} blocks.")
        self.progress['value'] = 100
        self.btn_select_pdf.state(['!disabled'])
        self.btn_clear.state(['!disabled'])
        self.update_ui_state()

    def _indexing_error(self, error_msg):
        messagebox.showerror("Indexing Error", f"Failed to index PDF:\n{error_msg}")
        self.clear_document()

    def clear_document(self):
        self.current_pdf = None
        self.current_results = []
        self.lbl_pdf_path.config(text="No PDF selected", foreground="gray")
        self.lbl_status.config(text="Ready")
        self.progress['value'] = 0
        self.entry_search.delete(0, tk.END)
        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete(1.0, tk.END)
        self.txt_results.config(state=tk.DISABLED)
        self.indexer.clear()
        # Searcher relies on the indexer instance, which now just has empty data
        self.update_ui_state()

    def perform_search(self):
        if not self.current_pdf:
            return

        query = self.entry_search.get().strip()
        if not query:
            return

        try:
            k = int(self.spin_k.get())
            threshold = float(self.spin_threshold.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid K or Threshold value.")
            return

        self.lbl_status.config(text="Searching...")
        self.root.update_idletasks()

        # Run search
        self.current_results = self.searcher.search(query, k=k, threshold=threshold)

        self._display_results()
        self.lbl_status.config(text=f"Found {len(self.current_results)} matches.")
        self.update_ui_state()

    def _display_results(self):
        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete(1.0, tk.END)

        if not self.current_results:
            self.txt_results.insert(tk.END, "No results found.\n")
        else:
            for i, result in enumerate(self.current_results, 1):
                page = result['page_num'] + 1 # 1-based indexing for UI
                score = result['score'] * 100
                text = result['text']
                excerpt = text[:120] + "..." if len(text) > 120 else text

                header = f"Result {i} (Page {page}) - Match: {score:.1f}%\n"

                self.txt_results.insert(tk.END, header, "header")
                self.txt_results.insert(tk.END, f"{excerpt}\n\n")

        self.txt_results.config(state=tk.DISABLED)

    def highlight_and_open(self):
        if not self.current_pdf or not self.current_results:
            return

        self.lbl_status.config(text="Generating highlighted PDF...")
        self.root.update_idletasks()

        try:
            output_path = highlight_pdf(self.current_pdf, self.current_results)
            if output_path:
                self.lbl_status.config(text="Opening PDF...")
                open_pdf(output_path)
                self.lbl_status.config(text="Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to highlight PDF:\n{e}")
            self.lbl_status.config(text="Ready")

def main():
    root = tk.Tk()
    app = PDFSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
