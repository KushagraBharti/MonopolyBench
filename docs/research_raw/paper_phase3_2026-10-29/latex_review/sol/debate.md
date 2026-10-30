# Sol LaTeX review exchanges

## Independent position

`initial_position.md` was saved before reading new peer findings. Opus confirmed the same ordering for his own initial position. Scope remains the full outline/exhibit conversion rather than divided section ownership.

## Accepted Opus challenges

Opus challenged the first proposed table notes, and I accepted these concrete improvements in `proposed_table_notes.tex`:

- T6 must define the initial-menu, accessible and full-access bounds, and identify the pre-action state for automatic eliminations. Displaying the raw header `avoidable` invites a broader interpretation than current-debt payment. Use a bounded displayed header while preserving the source key.
- T8 records post-event cash balances. The turn-zero initial balances used by F9 are separate from the table. They must not appear to be cash deltas or synthetic initial rows.
- T2 needs one explicit rounding rule. Gemini's 18/16 intensity is exactly 1.125. Half-even gives 1.12 at two decimals and half-up gives 1.13. Do not let a TeX formatter silently change a Python-generated display.
- Provider cost and latency notes should label USD and wall-clock seconds. Display Gemini (Argon) as the same participant across exhibits, without changing source identifiers.

I independently reopened the retained phase-2 `build_recovery_audit.json` structure after Opus questioned “quantity” in outline §4.2. The `uneven_rows` records encode `allocation_preserved_within_decision`, not a quantity-delta field. I sent Astra the bounded suggestion to display “allocation” or explicitly flag the inherited source wording. I did not compute a new quantity analysis, silently rewrite the source, or claim that quantities were preserved. The F7 frozen caption already uses purchase-multiset language.

Astra accepted the narrow “quantity” to “allocation” correction and will record it in the conversion log. Astra also accepted unnumbered front matter, outline sections 1–8, explicit math-glyph mapping, landscape treatment for wide figures, native long tables with repeated headers, T6 neutral current-debt language, T8 post-event levels in source order, T9 provenance/missingness, and half-even T2 display consistent with the original figure. These accepted decisions are the conversion acceptance criteria, not new scientific analysis.

## Shared baseline with both peers

I sent both reviewers the 837-row CSV/JSON consistency check, vector-PDF check, and unit/provenance proposals. These independent conversion checks do not replicate the underlying game or semantic audits. The full recorded source values remain authoritative.

I read Opus's initial position and proposed T6 snippet after my baseline, and agreed with the readable route-count display when the ordered source sequence remains linked. I attempted to send a verification challenge, but the tool returned `thread_not_sendable`, saying Opus had no running turn to steer. I did not restart him. The challenge remains recorded here: `table_fidelity.py` uses any-cell matching and searches any row, so it can miss swapped columns and reuse one output row for several source rows. It is appropriately documented as a detector. My shared-table check will compare ordered expected cells, keyed one-to-one to source rows, rather than cite that detector as a cell-fidelity proof. Astra's accepted half-even rule supersedes the half-up proposal in Opus's initial position.

## Actual first-build cross-check

After Opus's own first-build review arrived, I confirmed the same visible T5 collision, canonical-code hyphenation, incomplete T2 response-condition note, missing source planning index and incomplete T6-bound definition. I checked all 837 displayed rows independently in exact column order with zero mismatches. I told Opus that T2's eligible-decision frequency is proposals divided by eligible decisions, and proposed the explicit displayed header. We agreed that zero text outside the physical page is insufficient: the visible T5 collision is inside the page, against a rotated running header. Correct bbox checks must apply the PDF page rotation matrix.

Opus reproduced the T1 append bug and identified Astra's subsequent guard. I inspected that guard directly and closed the finding rather than carrying a stale issue into the final review.

## Fable's stronger completeness and navigation challenge

Fable challenged my earlier permission to leave omitted T6/T9 columns only in a linked sidecar. I accepted the stronger reading of “all datasets represented as actual LaTeX tables” and independently verified her proposed native companions: 60 T6 rows, all 296 actions in exact order, and eight T9 provenance/attempt-outcome records, with zero mismatches. I now endorse including the companions and have removed “or source link” from the proposed notes for these fields.

I confirmed Fable's `/Launch` diagnosis in the first outline PDF: all 14 original file links use that action. I corrected my findings to distinguish filesystem target existence from working PDF navigation. Native internal references in the exhibit document and readable path notes in the outline avoid depending on launch behavior.

I accepted exact row-linked source condition strings for T2. I partly disagree with removing the explicit T6 formula merely because F6's caption does not spell it out. The formula is the already-retained source field definition in the phase-2 bound script's docstring. The revised note now uses the frozen caption's “generous full-access upper bound” and its maximality limit while retaining the necessary existing column definition. This is neither a new bound nor a new research result.
