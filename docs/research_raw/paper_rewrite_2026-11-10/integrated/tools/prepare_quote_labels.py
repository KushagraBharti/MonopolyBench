"""Correct full-field labels without changing any quoted text."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
FABLE_FULL_FIELDS = {
    "fx-g15-offer", "fx-g15-refusal", "fx-g15-sweetener", "fx-g15-final-refusal",
    "fx-g11-offer", "fx-g11-reject", "fx-g11-concede", "fx-g11-reject-again",
}
TRANSCRIPT_FULL_FIELDS = {
    "g13-opening-insurance", "g13-seller-counter", "g13-seller-floor",
    "g13-acceptance", "g18-assurance", "g18-invocation", "g18-withdrawal",
    "g18-withdrawal-explanation", "g20-coordination-appeal",
    "g20-sale-response", "g20-concrete-refusal", "g7_d43_public",
    "g19_d135_false_public", "g19_d136_correction_accept",
    "g12_d249_public_bankruptcy", "g20-received-and-applied-public",
    "g20-recipient-recognition",
}
FULL_FIELDS_BY_FILE = {
    "sections/fable_quotes.tex": FABLE_FULL_FIELDS,
    "sections/transcript_quotes.tex": TRANSCRIPT_FULL_FIELDS,
}
FULL_FIELDS = FABLE_FULL_FIELDS | TRANSCRIPT_FULL_FIELDS


def relabel(text, full_fields):
    rows, changed = [], set()
    for line in text.splitlines(keepends=True):
        for key in full_fields:
            if line.startswith("\\DeclareTranscriptQuote{" + key + "}"):
                assert " · excerpt}{" in line
                line = line.replace(" · excerpt}{", " · full field}{", 1)
                changed.add(key)
        rows.append(line)
    assert changed == full_fields
    return "".join(rows)


if __name__ == "__main__":
    manifest = json.loads((HERE / "source_manifest.json").read_text())
    changes = []
    for leaf, fields in FULL_FIELDS_BY_FILE.items():
        source = HERE.parent / manifest[leaf]["source"]
        (HERE / leaf).write_text(relabel(source.read_text(), fields))
        changes.append({"source": manifest[leaf]["source"], "target": leaf,
                        "full_field_labels": sorted(fields)})
    (HERE / "qa/quote_label_changes.json").write_text(json.dumps({
        "files": changes,
        "change": "Only metadata labels: excerpt -> full field; quote payloads unchanged. Trailing whitespace is not printed.",
    }, indent=2) + "\n")
