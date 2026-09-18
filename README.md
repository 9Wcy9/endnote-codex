# EndNote + Codex

Two complementary Codex skills for moving references between an academic manuscript and EndNote.

## Skills

| Skill | Purpose |
| --- | --- |
| `endnote-collect` | Extract references actually cited in a manuscript, deduplicate them in first-appearance order, verify bibliographic metadata, and export verified records to EndNote-compatible RIS. |
| `endnote-cite` | Match planned or existing manuscript citations against records from the same EndNote library, prepare EndNote temporary citations, and audit unresolved or ambiguous matches. |

## Workflow

1. Run `$endnote-collect` on a DOCX, PDF, or text manuscript.
2. Review the audit table and import the verified RIS file into EndNote.
3. Export a record list from that EndNote library that includes its EndNote Record Numbers.
4. Run `$endnote-cite` with the manuscript, the library record list, and the intended citation locations.
5. Open the resulting document with the same EndNote library and use **Update Citations and Bibliography** in Word.

`endnote-cite` prepares plain-text EndNote temporary citations such as `{Smith, 2025 #42}`. It does not imitate or manufacture EndNote Cite While You Write field codes. EndNote and its Word add-in perform the final conversion and formatting.

## Install

Install either skill from its subdirectory:

```text
skills/endnote-collect
skills/endnote-cite
```

Both folders are self-contained and can be installed separately.

## Data and verification policy

- Supplied titles are search anchors; other supplied bibliographic fields remain provisional until verified.
- Ambiguous or unresolved records are reported rather than silently completed.
- `endnote-cite` only links records already present in the supplied EndNote-library export. It does not discover new literature.
- Manuscripts, reference libraries, and generated audit files are not included in this repository.

## License and trademark

The code and skill instructions in this repository are available under the MIT License.

EndNote is a trademark of Clarivate. This independent project is not affiliated with or endorsed by Clarivate.
