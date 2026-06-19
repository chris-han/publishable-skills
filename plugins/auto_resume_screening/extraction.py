from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

SUPPORTED_EXTENSIONS = (".docx", ".pdf", ".md", ".txt")
_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_SECTION_OR_FIELD_TERMS = {
    "个人简历",
    "简历",
    "求职意向",
    "工作经历",
    "项目经历",
    "教育背景",
    "专业背景",
    "技能证书",
    "自我评价",
    "联系方式",
    "个人信息",
    "基本信息",
    "证书",
    "姓名",
    "电话",
    "邮箱",
    "现居",
    "生日",
    "性别",
    "民族",
    "籍贯",
    "政治面貌",
    "skill certificate",
    "self evaluation",
    "work experience",
    "professional background",
    "education",
    "experience",
    "resume",
    "curriculum vitae",
    "contact",
}
_ROLE_TERMS = (
    "工程师",
    "技术员",
    "开发",
    "经理",
    "主管",
    "专员",
    "实习",
    "java",
    "python",
    "backend",
    "frontend",
    "engineer",
    "developer",
    "manager",
    "intern",
)


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_text(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _collapse_repeated_name(value: str) -> str:
    compact = re.sub(r"\s+", "", value.strip())
    if compact and len(compact) % 2 == 0:
        half = len(compact) // 2
        if compact[:half] == compact[half:]:
            return compact[:half]
    return value.strip()


def _clean_candidate_name(value: str) -> str:
    cleaned = re.sub(r"^(?:姓名|name|candidate)\s*[:：]\s*", "", value.strip(), flags=re.I)
    cleaned = re.split(r"(?:电话|手机|邮箱|email|现居|生日|求职意向)[:：]?", cleaned, maxsplit=1, flags=re.I)[0]
    cleaned = re.sub(r"[\t\r\n|/\\]+", " ", cleaned).strip(" ：:，,。.;；")
    return _collapse_repeated_name(cleaned)


def _looks_like_person_name(value: str) -> bool:
    name = _clean_candidate_name(value)
    if not name:
        return False
    normalized = name.lower()
    if normalized in _SECTION_OR_FIELD_TERMS:
        return False
    if any(term in normalized for term in _SECTION_OR_FIELD_TERMS if len(term) > 1):
        return False
    if any(term in normalized for term in _ROLE_TERMS):
        return False
    if re.search(r"[@\d]", name):
        return False
    if _CJK_RE.search(name):
        compact = re.sub(r"\s+", "", name)
        return 2 <= len(compact) <= 4 and all(
            "\u4e00" <= char <= "\u9fff" for char in compact
        )
    if re.fullmatch(r"[A-Za-z][A-Za-z.'-]*(?: [A-Za-z][A-Za-z.'-]*){0,2}", name):
        return len(name) <= 40
    return False


def extract_candidate_name(text: str) -> str | None:
    normalized = _normalize_text(text)
    lines = normalized.splitlines()

    label_patterns = (
        re.compile(
            r"(?:^|\b)(?:姓名|name|candidate)\s*[:：]\s*"
            r"([A-Za-z][A-Za-z.' -]{0,39}|[\u4e00-\u9fff]{2,4})",
            re.I,
        ),
    )
    for line in lines:
        for pattern in label_patterns:
            match = pattern.search(line)
            if match:
                candidate = _clean_candidate_name(match.group(1))
                if _looks_like_person_name(candidate):
                    return candidate

    previous = ""
    for line in lines[:80]:
        candidate = _clean_candidate_name(line)
        if _looks_like_person_name(candidate):
            return candidate
        if line == previous:
            collapsed = _clean_candidate_name(line)
            if _looks_like_person_name(collapsed):
                return collapsed
        previous = line

    return None


def _read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        raw = archive.read("word/document.xml")
    root = ElementTree.fromstring(raw)
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{_WORD_NS}p"):
        chunks = [node.text or "" for node in paragraph.iter(f"{_WORD_NS}t")]
        text = "".join(chunks).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _read_pdf(path: Path) -> str:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError(
            "PDF_EXTRACTION_DEPENDENCY_MISSING: pypdfium2 is required for PDF extraction"
        ) from exc

    doc = pdfium.PdfDocument(str(path))
    try:
        pages: list[str] = []
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_textpage().get_text_range().strip()
            if text:
                pages.append(text)
        return "\n".join(pages)
    finally:
        close = getattr(doc, "close", None)
        if callable(close):
            close()


def extract_text_from_resume(path: Path) -> dict[str, Any]:
    resolved = path.expanduser()
    if not resolved.exists():
        return {
            "status": "error",
            "error_code": "RESUME_FILE_MISSING",
            "message": f"Resume file not found: {path}",
        }
    extension = resolved.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return {
            "status": "error",
            "error_code": "UNSUPPORTED_RESUME_FORMAT",
            "message": f"Supported resume formats: {', '.join(SUPPORTED_EXTENSIONS)}",
            "extension": extension,
        }
    try:
        if extension == ".docx":
            raw_text = _read_docx(resolved)
        elif extension == ".pdf":
            raw_text = _read_pdf(resolved)
        else:
            raw_text = resolved.read_text(encoding="utf-8")
    except RuntimeError as exc:
        code = str(exc).split(":", 1)[0]
        return {
            "status": "error",
            "error_code": code,
            "message": str(exc),
            "extension": extension,
        }
    text = _normalize_text(raw_text)
    candidate_name = extract_candidate_name(text)
    return {
        "status": "ok",
        "source_path": str(resolved),
        "filename": resolved.name,
        "extension": extension,
        "extraction_method": "pypdfium2_text" if extension == ".pdf" else "native_text",
        "char_count": len(text),
        "text_sha256": _sha256_text(text),
        "candidate_name": candidate_name,
        "text": text,
    }


def extract_text_json(path: str) -> str:
    return json.dumps(extract_text_from_resume(Path(path)), ensure_ascii=False)
