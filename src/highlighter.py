import fitz
import os
import subprocess
import platform

def highlight_pdf(input_path, results):
    if not results:
        return None

    # Determine output path
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_highlighted{ext}"

    doc = fitz.open(input_path)

    for result in results:
        page_num = result['page_num']
        bbox = result['bbox']
        score = result['score']

        page = doc[page_num]

        # Create a fitz.Rect from the bbox
        rect = fitz.Rect(bbox)

        # Add highlight annotation
        annot = page.add_highlight_annot(rect)
        annot.set_colors(stroke=[1, 1, 0])  # Yellow
        info = annot.info
        info["content"] = f"Confidence: {score:.2f}"
        annot.set_info(info)
        annot.update()

    doc.save(output_path)
    doc.close()

    return output_path

def open_pdf(file_path):
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux and other Unix-like
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        print(f"Failed to open PDF: {e}")
