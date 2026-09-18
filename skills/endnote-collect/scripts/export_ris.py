#!/usr/bin/env python3
"""Export verified bibliographic JSON records to UTF-8 RIS and an audit CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


TYPE_MAP = {
    "journal_article": "JOUR",
    "book": "BOOK",
    "book_chapter": "CHAP",
    "conference_paper": "CPAPER",
    "report": "RPRT",
    "thesis": "THES",
    "webpage": "ELEC",
    "dataset": "DATA",
    "preprint": "UNPB",
    "other": "GEN",
}

VALID_STATUSES = {"verified", "ambiguous", "unresolved"}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def normalize_doi(value: Any) -> str:
    doi = clean_text(value).lower()
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi)
    return doi.rstrip(" .")


def author_text(author: Any) -> str:
    if isinstance(author, str):
        return clean_text(author)
    if not isinstance(author, dict):
        raise ValueError(f"author must be a string or object, got {type(author).__name__}")
    literal = clean_text(author.get("literal"))
    if literal:
        return literal
    family = clean_text(author.get("family"))
    given = clean_text(author.get("given"))
    if not family:
        raise ValueError("structured author is missing 'family' or 'literal'")
    return f"{family}, {given}" if given else family


def add_tag(lines: list[str], tag: str, value: Any) -> None:
    text = clean_text(value)
    if text:
        lines.append(f"{tag}  - {text}")


def record_to_ris(record: dict[str, Any]) -> str:
    item_type = clean_text(record.get("type") or "other")
    if item_type not in TYPE_MAP:
        raise ValueError(f"unsupported type '{item_type}'")

    lines = [f"TY  - {TYPE_MAP[item_type]}"]
    add_tag(lines, "TI", record.get("title"))
    for author in record.get("authors") or []:
        add_tag(lines, "AU", author_text(author))
    add_tag(lines, "PY", record.get("year"))

    if item_type == "journal_article":
        add_tag(lines, "JO", record.get("journal"))
    else:
        add_tag(lines, "T2", record.get("book_title") or record.get("journal"))

    add_tag(lines, "VL", record.get("volume"))
    add_tag(lines, "IS", record.get("issue"))
    add_tag(lines, "SP", record.get("start_page"))
    add_tag(lines, "EP", record.get("end_page"))
    add_tag(lines, "C7", record.get("article_number"))
    add_tag(lines, "PB", record.get("publisher"))
    add_tag(lines, "CY", record.get("place"))
    add_tag(lines, "ET", record.get("edition"))
    add_tag(lines, "SN", record.get("isbn") or record.get("issn"))
    add_tag(lines, "DO", normalize_doi(record.get("doi")))
    add_tag(lines, "UR", record.get("url"))
    add_tag(lines, "AB", record.get("abstract"))
    for keyword in record.get("keywords") or []:
        add_tag(lines, "KW", keyword)
    lines.append("ER  -")
    return "\n".join(lines) + "\n"


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("input must be a JSON array or an object containing a 'records' array")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("every record must be a JSON object")
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_ris", type=Path)
    parser.add_argument("--audit-csv", type=Path)
    parser.add_argument(
        "--allow-unverified",
        action="store_true",
        help="also export ambiguous and unresolved records (not recommended)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        records = load_records(args.input_json)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    audit_rows: list[dict[str, Any]] = []
    ris_records: list[str] = []
    seen: dict[str, str] = {}

    for index, record in enumerate(records, start=1):
        title = clean_text(record.get("title"))
        status = clean_text(record.get("status")).lower()
        record_id = clean_text(record.get("id")) or f"R{index:03d}"
        doi = normalize_doi(record.get("doi"))
        key = f"doi:{doi}" if doi else f"title:{normalize_title(title)}"
        duplicate_of = seen.get(key) if title else ""
        exported = False
        error_note = ""

        if not title:
            error_note = "missing verified title"
        elif status not in VALID_STATUSES:
            error_note = "status must be verified, ambiguous, or unresolved"
        elif duplicate_of:
            error_note = f"duplicate of {duplicate_of}"
        elif status != "verified" and not args.allow_unverified:
            error_note = f"excluded because status is {status}"
        else:
            try:
                ris_records.append(record_to_ris(record))
                exported = True
                seen[key] = record_id
            except ValueError as exc:
                error_note = str(exc)

        if title and key not in seen and not duplicate_of:
            seen[key] = record_id

        notes = clean_text(record.get("notes"))
        if error_note:
            notes = f"{notes}; {error_note}".strip("; ")

        audit_rows.append(
            {
                "input_index": index,
                "id": record_id,
                "original_title": clean_text(record.get("original_title")),
                "verified_title": title,
                "status": status or "invalid",
                "first_occurrence": clean_text(record.get("first_occurrence")),
                "doi": doi,
                "verification_source": clean_text(record.get("verification_source")),
                "notes": notes,
                "exported": "yes" if exported else "no",
                "duplicate_of": duplicate_of,
            }
        )

    if args.audit_csv:
        args.audit_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.audit_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            fieldnames = [
                "input_index", "id", "original_title", "verified_title", "status",
                "first_occurrence", "doi", "verification_source", "notes", "exported",
                "duplicate_of",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(audit_rows)

    if not ris_records:
        print("error: no records were eligible for RIS export", file=sys.stderr)
        return 3

    args.output_ris.parent.mkdir(parents=True, exist_ok=True)
    args.output_ris.write_text("\n".join(ris_records), encoding="utf-8")
    skipped = len(records) - len(ris_records)
    print(f"exported {len(ris_records)} unique record(s); skipped {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
