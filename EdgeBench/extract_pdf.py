# -*- coding: utf-8 -*-
import pdfplumber
import sys

pdf_path = "EdgeBench.pdf"
out_path = "EdgeBench_text.txt"

with pdfplumber.open(pdf_path) as pdf:
    with open(out_path, "w", encoding="utf-8") as f:
        for i, page in enumerate(pdf.pages):
            f.write(f"\n\n========== PAGE {i+1} ==========\n\n")
            text = page.extract_text() or ""
            f.write(text)
print(f"Saved to {out_path}")