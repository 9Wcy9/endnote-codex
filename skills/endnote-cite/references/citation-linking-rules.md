# Citation linking rules

Read this file before matching or inserting EndNote temporary citations.

## Library record requirements

Each candidate record should contain:

- EndNote Record Number;
- title;
- first author or group author;
- year;
- DOI when available.

Record Numbers belong to a particular EndNote library. Use the same library export for matching and for the final Word update. Do not reuse a Record Number taken from a different library.

## Match priority

1. One exact normalized DOI match: `matched`.
2. No DOI match and one exact normalized-title match: `matched`.
3. More than one candidate at the strongest available level: `ambiguous`.
4. No candidate: `missing`.

Author and year may confirm a DOI or title match but must not override a mismatch. Fuzzy title similarity may identify candidates for human review, but it must not produce an inserted temporary citation automatically.

Normalize DOI by removing resolver prefixes and leading `doi:`. Normalize titles only for comparison by applying Unicode normalization, case folding, whitespace collapse, and punctuation removal. Retain the EndNote record's display text in outputs.

## Temporary citation form

The base temporary citation is:

```text
{Author, Year #RecordNumber}
```

Use the first author's family name or the group author exactly as represented in the supplied record. For clusters, preserve the user's intended order and EndNote-compatible delimiters. Keep narrative author text outside the temporary citation when required by the sentence.

Do not represent plain temporary-citation text as a live EndNote field. After insertion, the user must open the same library in EndNote and use **Update Citations and Bibliography** in Word.

## Audit fields

At minimum retain:

`citation_id`, `location`, `requested_title`, `requested_doi`, `matched_title`, `record_number`, `temporary_citation`, `status`, and `notes`.

Keep every planned location in the audit, including missing and ambiguous items.
