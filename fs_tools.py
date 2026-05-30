from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import mimetypes
import os
import re

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None

SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx'}


def _file_metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        'name': path.name,
        'path': str(path.resolve()),
        'extension': path.suffix.lower(),
        'size_bytes': stat.st_size,
        'modified_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'mime_type': mimetypes.guess_type(str(path))[0],
    }


def _extract_text_from_txt(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def _extract_text_from_pdf(path: Path) -> str:
    if PdfReader is None:
        raise ImportError("pypdf is required to read PDF files. Install it from requirements.txt")
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or '')
    return '\n'.join(pages).strip()


def _extract_text_from_docx(path: Path) -> str:
    if Document is None:
        raise ImportError("python-docx is required to read DOCX files. Install it from requirements.txt")
    doc = Document(str(path))
    paras = [p.text for p in doc.paragraphs]
    return '\n'.join(paras).strip()


def read_file(filepath: str) -> dict[str, Any]:
    path = Path(filepath)
    try:
        if not path.exists():
            return {'success': False, 'error': f'File not found: {filepath}'}
        if not path.is_file():
            return {'success': False, 'error': f'Path is not a file: {filepath}'}
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return {
                'success': False,
                'error': f'Unsupported file type: {ext}. Supported: {sorted(SUPPORTED_EXTENSIONS)}'
            }

        if ext == '.txt':
            content = _extract_text_from_txt(path)
        elif ext == '.pdf':
            content = _extract_text_from_pdf(path)
        else:
            content = _extract_text_from_docx(path)

        metadata = _file_metadata(path)
        metadata['character_count'] = len(content)
        metadata['line_count'] = len(content.splitlines()) if content else 0
        return {'success': True, 'content': content, 'metadata': metadata}
    except Exception as exc:
        return {'success': False, 'error': str(exc), 'metadata': {'path': str(path.resolve()) if path.exists() else filepath}}


def list_files(directory: str, extension: Optional[str] = None) -> list[dict[str, Any]]:
    base = Path(directory)
    if not base.exists() or not base.is_dir():
        return []

    ext = extension.lower() if extension else None
    if ext and not ext.startswith('.'):
        ext = f'.{ext}'

    results = []
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        if ext and path.suffix.lower() != ext:
            continue
        results.append(_file_metadata(path))
    return results


def write_file(filepath: str, content: str) -> dict[str, Any]:
    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return {'success': True, 'message': 'File written successfully', 'metadata': _file_metadata(path)}
    except Exception as exc:
        return {'success': False, 'error': str(exc), 'metadata': {'path': str(path)}}


def search_in_file(filepath: str, keyword: str) -> dict[str, Any]:
    if not keyword or not keyword.strip():
        return {'success': False, 'error': 'Keyword must not be empty'}

    file_result = read_file(filepath)
    if not file_result.get('success'):
        return file_result

    content = file_result['content']
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    matches = []
    context_window = 50
    for idx, match in enumerate(pattern.finditer(content), start=1):
        start, end = match.span()
        context_start = max(0, start - context_window)
        context_end = min(len(content), end + context_window)
        matches.append({
            'match_number': idx,
            'matched_text': match.group(0),
            'start_index': start,
            'end_index': end,
            'context': content[context_start:context_end].replace('\n', ' ')
        })

    return {
        'success': True,
        'keyword': keyword,
        'match_count': len(matches),
        'matches': matches,
        'metadata': file_result['metadata']
    }
