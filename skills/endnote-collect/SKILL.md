---
name: endnote-collect
description: Extract, reconcile, verify, and export references actually cited in academic manuscripts. Use for first-appearance reference lists, citation-bibliography audits, metadata verification from titles, deduplication, or EndNote-compatible RIS creation. Do not use to insert EndNote citations into a manuscript or to discover literature for a new review.
---

# EndNote + Codex (Collect)

Build a traceable, EndNote-ready reference set from a manuscript without carrying forward plausible-looking but unverified metadata.

## Evidence rule

Treat the work title as the only trusted search anchor unless the user explicitly identifies another field as authoritative. Regard supplied authors, year, journal, volume, issue, pages, DOI, and URLs as clues that require verification.

- Do not use an earlier AI-generated bibliography as evidence.
- Do not complete a partial record from memory.
- Do not merge records merely because authors and years resemble one another.
- If no usable title is present, mark the item `unresolved` and state what is missing.

## Workflow

1. Read the whole manuscript or the user-designated scope while preserving the original file.
2. Extract in-text citations in document order and parse the supplied bibliography separately. Support author-year, numbered, and note-based systems.
3. Map each cited work to its first occurrence. Expand citation clusters while preserving their order.
4. Reconcile citations with bibliography entries and keep these categories separate: cited and matched; cited but absent; bibliography entry not cited; ambiguous mapping.
5. Deduplicate while retaining first-appearance order. Prefer verified DOI identity, then identical normalized titles, then a high-confidence title match supported by the same publication source. Preserve distinct editions, translations, corrections, conference papers, and journal versions unless identity is verified.
6. Verify each matched title using authoritative online sources. Prefer the publisher or DOI landing page, then Crossref or a discipline-specific index. Use authoritative catalogues, repositories, or issuing organizations for books, theses, reports, and datasets.
7. Capture complete, type-appropriate metadata and its verification source. Record conflicts rather than hiding them.
8. Assign exactly one status: `verified`, `ambiguous`, or `unresolved`.
9. Export only verified metadata as final references unless the user explicitly requests a provisional export.

Inspect relevant pages visually when OCR, broken line wrapping, tables, equations, or notes make extraction uncertain.

## Deliverables

Follow the requested output. For a broad request, provide:

1. a numbered verified bibliography ordered by first appearance;
2. an audit table containing the original and verified title, first occurrence, status, DOI or authoritative source, and notes;
3. separate cited-but-missing, uncited, ambiguous, and unresolved lists;
4. counts for citations found, unique works, verified works, and unresolved issues.

For RIS or structured output, read [references/metadata-and-output-rules.md](references/metadata-and-output-rules.md), create its intermediate JSON, and run:

```bash
python3 scripts/export_ris.py verified_records.json references.ris \
  --audit-csv reference_audit.csv
```

The exporter excludes non-verified records by default. Use `--allow-unverified` only when the user explicitly requests provisional records, and keep their status visible in the audit file.

## Quality checks

- Reconcile the final record count with the occurrence map.
- Confirm every numbered reference has an in-text occurrence.
- Confirm ordering follows first appearance rather than the supplied bibliography.
- Confirm DOI, title, author order, group authors, article numbers, and page ranges against authoritative records.
- Verify that the RIS imports as separate UTF-8 records.
- Report unresolved or conflicting items instead of estimating them.

Keep small requests proportionate while preserving the same evidence rules.
