# Metadata and output rules

Read this file when producing an EndNote/RIS deliverable or an auditable structured reference set.

## Source priority

Use the strongest source that identifies the same work:

1. publisher page or DOI landing page;
2. Crossref registration metadata;
3. authoritative discipline index, institutional repository, library catalogue, or issuing organization;
4. an aggregator only to locate a stronger record.

Do not let author, year, or journal similarity override a title mismatch. If authoritative sources disagree and the conflict cannot be resolved, use `ambiguous`.

## Normalization and identity

Normalization is for matching only. Retain verified display text in outputs.

- Compare titles case-insensitively after Unicode normalization, whitespace collapse, and removal of surrounding punctuation.
- Ignore a terminal period and harmless punctuation differences, but preserve substantive subtitle, language, edition, part, correction, or retraction distinctions.
- Normalize DOI values by removing a resolver URL or leading `doi:` and storing the remaining DOI in lowercase.
- Prefer verified DOI identity over normalized-title identity.

## Intermediate JSON

Pass either a top-level array or an object with a `records` array to `scripts/export_ris.py`. Preserve first-appearance order.

```json
{
  "records": [
    {
      "id": "R001",
      "type": "journal_article",
      "status": "verified",
      "original_title": "Title as found in the manuscript",
      "title": "Verified article title",
      "authors": [
        {"family": "Smith", "given": "Jane Q."},
        {"literal": "World Health Organization"}
      ],
      "year": "2025",
      "journal": "Verified Journal Title",
      "volume": "12",
      "issue": "3",
      "start_page": "101",
      "end_page": "119",
      "article_number": "104266",
      "doi": "10.1234/example.2025.1",
      "url": "https://doi.org/10.1234/example.2025.1",
      "first_occurrence": "p. 3, paragraph 2",
      "verification_source": "https://publisher.example/article",
      "notes": "Optional verification note"
    }
  ]
}
```

Required fields are `title` and `status`. Supported `type` values are `journal_article`, `book`, `book_chapter`, `conference_paper`, `report`, `thesis`, `webpage`, `dataset`, `preprint`, and `other`.

Use structured author objects when possible. Use `literal` for an organization. Do not put manuscript-specific occurrence or verification notes into RIS bibliographic fields.

## Output conventions

- Save RIS as UTF-8 with one `ER  -` terminator per record.
- Export only `verified` records by default.
- Retain input order unless the user asks for another order.
- Keep page ranges in `SP` and `EP`; keep article numbers in `C7`.
- Use one `AU` tag per author and one `KW` tag per keyword.
- Keep DOI in `DO` without a resolver prefix.
- Use an authoritative landing page in `UR` when available.

The audit CSV contains: `input_index`, `id`, `original_title`, `verified_title`, `status`, `first_occurrence`, `doi`, `verification_source`, `notes`, `exported`, and `duplicate_of`. It retains ambiguous, unresolved, skipped, and duplicate records even when excluded from RIS.
