---
name: endnote-cite
description: Link manuscript citation locations to records already present in an EndNote library export, prepare EndNote temporary citations, and audit missing or ambiguous matches. Use when the user wants to place, migrate, or check EndNote citations in a DOCX or text manuscript. Do not use to discover or verify new literature, create RIS records, or claim that plain text is a live Cite While You Write field.
---

# EndNote + Codex (Cite)

Connect a manuscript to the user's existing EndNote library without guessing which source belongs at a citation location.

## Boundary

This skill prepares EndNote temporary citations and an audit trail. It does not manufacture EndNote Cite While You Write field codes. Final conversion and bibliography formatting occur in Word with the same EndNote library open.

Use only records supplied from the user's EndNote library. If a needed work is absent, report it and route collection or verification work to `$endnote-collect` only when that skill is available.

## Required inputs

- the manuscript or the user-designated passage;
- an export or table from the same EndNote library that includes each record's EndNote Record Number;
- explicit citation locations, existing citation markers, or a user-approved citation plan.

Do not infer that a general claim needs a particular source merely because the source appears topically similar. When the user asks for source recommendations, treat that as a separate literature-evidence task rather than silently inserting a citation.

## Workflow

1. Preserve the original manuscript and work on a copy.
2. Read [references/citation-linking-rules.md](references/citation-linking-rules.md).
3. Inventory existing formatted citations, temporary citations, placeholders, and bibliography entries.
4. Match each intended citation to the supplied EndNote records. Prefer exact normalized DOI, then exact normalized title. Use author-year only as supporting evidence, never as the sole basis when multiple records qualify.
5. Assign one status: `matched`, `ambiguous`, `missing`, or `already_linked`.
6. Insert a temporary citation only for `matched` records. Preserve requested cluster order and any prefix, suffix, locator, or narrative wording.
7. Do not insert or replace ambiguous and missing items. Mark their locations in the audit instead.
8. Save a revised manuscript copy plus a citation audit. Never overwrite the source file unless the user explicitly requests it.
9. Tell the user to open the same EndNote library in Word and run **Update Citations and Bibliography**. Do not claim the citations are live EndNote fields until EndNote performs that step.

For a structured citation plan, run:

```bash
python3 scripts/prepare_endnote_citations.py endnote_records.csv citation_plan.csv \
  citation_audit.csv
```

The script generates temporary citations only for unique DOI or title matches. Review the audit before editing the manuscript.

## Quality checks

- Confirm every inserted temporary citation contains a valid Record Number from the supplied library export.
- Confirm author and year agree with the matched record.
- Preserve citation-cluster order and narrative grammar.
- Keep page locators, prefixes, suffixes, and suppress-author choices intact.
- Confirm no ambiguous or missing item was silently inserted.
- Confirm the revised document opens normally before delivery.
- Report the number of matched, ambiguous, missing, and already linked locations.
