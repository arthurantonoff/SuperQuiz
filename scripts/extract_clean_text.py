#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import unicodedata
from collections import Counter
from typing import List
import pdfplumber

def _extract_text_pdf(pdf_path: str, x_tol: float = 2.0, y_tol: float = 2.0) -> List[str]:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            t = p.extract_text(x_tolerance=x_tol, y_tolerance=y_tol) or ""
            if not t:
                t = p.extract_text() or ""
            pages.append(t)
    return pages

def _norm_line(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).strip()
    s = re.sub(r"\bP[aá]gina\s+\d+\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "", s)
    s = re.sub(r"\b\d+\s*/\s*\d+\b", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _find_repeated_lines(pages_text: List[str], min_ratio: float = 0.6) -> set:
    total = max(1, len(pages_text))
    bag = Counter()
    for t in pages_text:
        lines = [_norm_line(l) for l in t.splitlines() if l.strip()]
        lines = [l for l in set(lines) if 3 <= len(l) <= 120]
        bag.update(lines)
    return {l for l, c in bag.items() if c >= int(total * min_ratio)}

_WATERMARK_PAT = re.compile(r"(uso\s+pessoal|intransferivel|plurall)", re.IGNORECASE)

def _clean_page_text(text: str, repeated: set) -> str:
    t = unicodedata.normalize("NFKC", text)
    kept = []
    for raw in t.splitlines():
        ln = _norm_line(raw)
        if not ln:
            continue
        if ln in repeated or _WATERMARK_PAT.search(ln):
            continue
        kept.append(ln)
    t = "\n".join(kept)
    t = re.sub(r"-\s*\n\s*", "", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"(?<![.!?:;])\n(?!\n)", " ", t)
    t = re.sub(r"[^\S\n]+", " ", t)
    t = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", "", t)
    t = re.sub(r"\n\s*\n", "\n\n", t).strip()
    return t

def extract_clean_text(pdf_path: str) -> str:
    pages = _extract_text_pdf(pdf_path)
    repeated = _find_repeated_lines(pages, min_ratio=0.6)
    cleaned = [_clean_page_text(p, repeated) for p in pages]
    return "\n\n".join([c for c in cleaned if c.strip()])
