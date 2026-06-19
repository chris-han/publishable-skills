from __future__ import annotations

import html
import re
import urllib.request
from html.parser import HTMLParser
from typing import Any

from .extraction import _ROLE_TERMS

DEFAULT_ROLE_TERM_SOURCES = (
    "https://www.zhaopin.com/jobs/",
    "https://www.onetonline.org/find/all",
)

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ONET_CODE_RE = re.compile(r"^\d{2}-\d{4}(?:\.\d{2})?$")
_ENGLISH_STOPWORDS = {
    "a",
    "all",
    "and",
    "as",
    "by",
    "except",
    "for",
    "in",
    "of",
    "on",
    "or",
    "other",
    "postsecondary",
    "related",
    "the",
    "with",
}
_ENGLISH_ROLE_SUFFIXES = (
    "ant",
    "er",
    "ian",
    "ist",
    "or",
)
_ENGLISH_ROLE_NOUNS = {
    "actor",
    "actuary",
    "aide",
    "appraiser",
    "artist",
    "bailiff",
    "barber",
    "barista",
    "broker",
    "carpenter",
    "clergy",
    "chemist",
    "chiropractor",
    "dancer",
    "dentist",
    "dietitian",
    "drafter",
    "economist",
    "electrician",
    "firefighter",
    "guard",
    "host",
    "inspector",
    "judge",
    "laborer",
    "librarian",
    "machinist",
    "maid",
    "mediator",
    "optometrist",
    "painter",
    "pilot",
    "porter",
    "scientist",
    "secretary",
    "sheriff",
    "sociologist",
    "surgeon",
    "teller",
    "veterinarian",
}
_CJK_ROLE_HINTS = tuple(
    term for term in _ROLE_TERMS if _CJK_RE.search(term)
) + (
    "员",
    "师",
    "工",
    "长",
    "手",
    "医",
    "护",
    "岗",
    "职位",
)
_NON_ROLE_TEXT = {
    "about o*net",
    "advanced searches",
    "all occupations",
    "bright outlook",
    "career cluster",
    "find occupations",
    "go",
    "help",
    "home",
    "job zone",
    "save table",
    "share",
}


class _AnchorTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_anchor = False
        self._chunks: list[str] = []
        self.anchor_texts: list[tuple[str, str]] = []
        self._href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._in_anchor = True
            self._chunks = []
            self._href = dict(attrs).get("href") or ""

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._in_anchor:
            return
        text = _normalize_visible_text("".join(self._chunks))
        if text:
            self.anchor_texts.append((text, self._href))
        self._in_anchor = False
        self._chunks = []
        self._href = ""


def _normalize_visible_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _fetch_url(url: str, timeout_seconds: float) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Semantier auto_resume_screening role term extractor "
                "(maintenance tool)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def _looks_like_role_anchor(text: str, href: str, source_url: str) -> bool:
    lowered = text.lower()
    if lowered in _NON_ROLE_TEXT or _ONET_CODE_RE.fullmatch(text):
        return False
    if "onetonline.org" in source_url and "/link/summary/" not in href:
        return False
    if len(text) < 2 or len(text) > 120:
        return False
    return bool(_CJK_RE.search(text) or re.search(r"[A-Za-z]", text))


def _split_chinese_title(text: str) -> list[str]:
    pieces = re.split(r"[、,/|()（）\[\]【】;；:：]+", text)
    terms: list[str] = []
    for piece in pieces:
        normalized = re.sub(r"\s+", "", piece)
        if (
            2 <= len(normalized) <= 16
            and _CJK_RE.search(normalized)
            and any(hint in normalized for hint in _CJK_ROLE_HINTS)
        ):
            terms.append(normalized)
    return terms


def _singularize_english_token(token: str) -> str:
    if len(token) <= 3:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith("ers") or token.endswith("ors"):
        return token[:-1]
    if token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _split_english_title(text: str) -> list[str]:
    normalized = re.sub(r"[^A-Za-z/& -]+", " ", text).lower()
    normalized = normalized.replace("/", " ")
    terms: list[str] = []
    for raw_word in re.split(r"[\s,&-]+", normalized):
        if not raw_word or raw_word in _ENGLISH_STOPWORDS:
            continue
        word = _singularize_english_token(raw_word)
        if not 2 <= len(word) <= 32:
            continue
        if word in _ENGLISH_ROLE_NOUNS or word.endswith(_ENGLISH_ROLE_SUFFIXES):
            terms.append(word)
    return terms


def _is_blocked_document(document: str) -> bool:
    lowered = document.lower()
    return "security verification" in lowered or "captcha" in lowered


def _extract_terms_from_html(document: str, source_url: str) -> list[str]:
    parser = _AnchorTextParser()
    parser.feed(document)
    terms: list[str] = []
    for text, href in parser.anchor_texts:
        if not _looks_like_role_anchor(text, href, source_url):
            continue
        if _CJK_RE.search(text):
            terms.extend(_split_chinese_title(text))
        else:
            terms.extend(_split_english_title(text))
    return terms


def _dedupe_missing_terms(terms: list[str], existing_terms: tuple[str, ...]) -> list[str]:
    existing = {term.lower() for term in existing_terms}
    seen: set[str] = set()
    missing: list[str] = []
    for term in terms:
        key = term.lower()
        if key in existing or key in seen:
            continue
        seen.add(key)
        missing.append(term)
    return missing


def extract_missing_role_terms(
    source_urls: list[str] | None = None,
    *,
    timeout_seconds: float = 15.0,
    max_terms_per_source: int = 200,
) -> dict[str, Any]:
    urls = source_urls or list(DEFAULT_ROLE_TERM_SOURCES)
    sources: list[dict[str, Any]] = []
    combined: list[str] = []
    for url in urls:
        try:
            document = _fetch_url(url, timeout_seconds)
            if _is_blocked_document(document):
                sources.append(
                    {
                        "url": url,
                        "status": "error",
                        "error_code": "ROLE_TERM_SOURCE_BLOCKED",
                        "message": "Source returned a security verification page.",
                    }
                )
                continue
            terms = _dedupe_missing_terms(_extract_terms_from_html(document, url), _ROLE_TERMS)
            limited_terms = terms[:max_terms_per_source]
            sources.append(
                {
                    "url": url,
                    "status": "ok",
                    "extracted_count": len(terms),
                    "terms": limited_terms,
                    "truncated": len(terms) > len(limited_terms),
                }
            )
            combined.extend(limited_terms)
        except Exception as exc:  # pragma: no cover - exact network errors vary.
            sources.append(
                {
                    "url": url,
                    "status": "error",
                    "error_code": "ROLE_TERM_SOURCE_FETCH_FAILED",
                    "message": str(exc),
                }
            )

    return {
        "status": "ok" if any(source["status"] == "ok" for source in sources) else "error",
        "baseline_role_terms_count": len(_ROLE_TERMS),
        "missing_terms": _dedupe_missing_terms(combined, ()),
        "sources": sources,
    }
