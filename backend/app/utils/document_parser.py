"""Generic DOCX placeholder parser and in-place replacer.

Placeholder convention: ``{{variable_key}}`` where ``variable_key`` is a
lowercase snake_case identifier (letters, digits, underscore; must start
with a letter or underscore). This is the only construct treated as a
variable — blank signature lines, underscores (``____``) and other
decorative content are never inferred as variables.

Word can split a single ``{{variable_key}}`` token across multiple XML
runs (e.g. when the document was edited, spell-checked, or has mixed
formatting). Extraction reads the concatenated paragraph text so split
placeholders are still recognised; replacement rewrites the underlying
runs so the paragraph's original formatting is preserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class ExtractedVariable:
    key: str
    label: str
    type: str
    required: bool = True
    options: list[str] | None = field(default=None)


def _humanize(key: str) -> str:
    return " ".join(word.capitalize() for word in key.split("_") if word)


_NUMBER_HINTS = ("age", "amount", "number", "count", "years", "qty", "quantity", "no")
_DATE_HINTS = ("date", "dob", "dated")
_TEXTAREA_HINTS = ("address", "details", "description", "remarks", "statement", "declaration")


def _infer_type(key: str) -> str:
    lowered = key.lower()
    tokens = set(lowered.split("_"))
    if tokens & set(_DATE_HINTS) or lowered.endswith("date"):
        return "date"
    if tokens & set(_NUMBER_HINTS):
        return "number"
    if tokens & set(_TEXTAREA_HINTS):
        return "textarea"
    return "text"


def infer_variable(key: str) -> ExtractedVariable:
    return ExtractedVariable(key=key, label=_humanize(key), type=_infer_type(key), required=True)


def _iter_paragraphs_in_cell(cell: _Cell) -> Iterator[Paragraph]:
    yield from cell.paragraphs
    for nested_table in cell.tables:
        yield from _iter_paragraphs_in_table(nested_table)


def _iter_paragraphs_in_table(table: Table) -> Iterator[Paragraph]:
    for row in table.rows:
        for cell in row.cells:
            yield from _iter_paragraphs_in_cell(cell)


def iter_all_paragraphs(document: Document) -> Iterator[Paragraph]:
    """Yield every paragraph in the document body, all tables (including
    nested tables), and every section's headers/footers."""
    yield from document.paragraphs
    for table in document.tables:
        yield from _iter_paragraphs_in_table(table)

    for section in document.sections:
        for part in (
            section.header,
            section.footer,
            section.first_page_header,
            section.first_page_footer,
            section.even_page_header,
            section.even_page_footer,
        ):
            if part is None:
                continue
            yield from part.paragraphs
            for table in part.tables:
                yield from _iter_paragraphs_in_table(table)


def extract_placeholder_keys(document: Document) -> list[str]:
    """Return placeholder keys in first-seen order, deduplicated."""
    seen: dict[str, None] = {}
    for paragraph in iter_all_paragraphs(document):
        for match in PLACEHOLDER_PATTERN.finditer(paragraph.text):
            seen.setdefault(match.group(1), None)
    return list(seen.keys())


def extract_variables(document: Document) -> list[ExtractedVariable]:
    """Extract placeholders from a DOCX and infer a form field spec for each."""
    return [infer_variable(key) for key in extract_placeholder_keys(document)]


def extract_variables_from_file(file_path: str) -> list[ExtractedVariable]:
    return extract_variables(Document(file_path))


def _replace_in_paragraph(paragraph: Paragraph, values: dict[str, str]) -> None:
    runs = paragraph.runs
    if not runs:
        return

    full_text = "".join(run.text for run in runs)
    matches = list(PLACEHOLDER_PATTERN.finditer(full_text))
    if not matches:
        return

    run_offsets: list[tuple[int, int]] = []
    cursor = 0
    for run in runs:
        run_offsets.append((cursor, cursor + len(run.text)))
        cursor += len(run.text)

    def _run_index_for(pos: int) -> int:
        for idx, (start, end) in enumerate(run_offsets):
            if start <= pos < end:
                return idx
        return len(runs) - 1

    # Process right-to-left so earlier (still-unprocessed) matches keep
    # valid offsets into their own, untouched runs.
    for match in reversed(matches):
        key = match.group(1)
        if key not in values:
            continue
        replacement = values[key]
        start, end = match.start(), match.end()
        start_run_idx = _run_index_for(start)
        end_run_idx = _run_index_for(end - 1)

        if start_run_idx == end_run_idx:
            run = runs[start_run_idx]
            local_start = start - run_offsets[start_run_idx][0]
            local_end = end - run_offsets[start_run_idx][0]
            text = run.text
            run.text = text[:local_start] + replacement + text[local_end:]
        else:
            first_run = runs[start_run_idx]
            local_start = start - run_offsets[start_run_idx][0]
            first_run.text = first_run.text[:local_start] + replacement

            last_run = runs[end_run_idx]
            local_end = end - run_offsets[end_run_idx][0]
            last_run.text = last_run.text[local_end:]

            for idx in range(start_run_idx + 1, end_run_idx):
                runs[idx].text = ""


def replace_placeholders(document: Document, values: dict[str, str]) -> None:
    """Replace every ``{{key}}`` occurrence throughout the document (body
    paragraphs, tables — including nested tables — and headers/footers)
    with ``values[key]``, preserving each paragraph's run formatting.
    Placeholders whose key is not present in ``values`` are left as-is.
    """
    for paragraph in iter_all_paragraphs(document):
        _replace_in_paragraph(paragraph, values)


def find_unresolved_placeholders(document: Document) -> list[str]:
    """Return any placeholder keys still present after a replacement pass."""
    return extract_placeholder_keys(document)
