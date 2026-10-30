"""Select versioned drafting references from the coauthors' checked libraries.

This is bibliography assembly, not a new source-verification pass. Inspection
depth and originating records remain explicit in reference_registry.json.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VERSIONS = {
    "2502.15840": "v1",
    "2608.14825": "v3",
    "2610.29330": "v2",
    "2605.27896": "v1",
    "2610.35773": "v1",
    "2605.14537": "v1",
    "2310.11667": "v2",
    "2312.03664": "v2",
    "2412.14161": "v3",
    "2308.03688": "v3",
    "2307.13854": "v4",
    "2404.07972": "v2",
    "2406.12045": "v1",
    "2406.13352": "v3",
    "2410.07095": "v6",
    "2503.14499": "v4",
    "2401.13178": "v2",
    "2510.11977": "v1",
    "2304.03279": "v4",
    "2503.03750": "v3",
    "2407.21792": "v3",
    "2609.24967": "v2",
    "2402.05863": "v1",
    "2604.04782": "v1",
    "2607.05132": "v2",
    "2610.01045": "v2",
    "2610.21203": "v1",
    "2305.04388": "v2",
    "2307.13702": "v1",
    "2507.11473": "v2",
}
METHODS = {
    "2502.15840": "Astra methods 2–3; peer methods readings.",
    "2608.14825": "Astra sections 2, 4, 5 and limitations; all peers' methods checks.",
    "2610.29330": "Astra sections 3–4, limitations and appendix; peers also inspected repository.",
    "2605.27896": "Astra sections 3–4; Fable and Opus also inspected rule appendices.",
    "2610.35773": "Astra section 3.2; Sol/Opus/Fable sections 3–5 and appendix as logged.",
    "2610.01045": "Astra v2 abstract/introduction; Sol v2 sections 2–5 and Appendix E after Fable's version objection.",
    "2610.21203": "Astra abstract; Sol sections 2–6 and Appendix D.",
}
PAGES = {
    "andon2026arena": "https://andonlabs.com/evals/vending-bench-arena",
    "andon2026vb2": "https://andonlabs.com/evals/vending-bench-2",
    "metr2026page": "https://metr.org/time-horizons/",
    "agentmonopoly2026repo": "https://github.com/SuELS-Group/Agent_Monopoly/tree/2434f4278bf2970237ba82399db191e0116f3d35",
}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def entries(text: str) -> list[tuple[str, str]]:
    """Read balanced BibTeX records, preserving nested title/URL braces."""
    records = []
    for match in re.finditer(r"(?m)^@\w+\{([^,]+),", text):
        depth = 0
        for end in range(text.index("{", match.start()), len(text)):
            if end and text[end - 1] == "\\":
                continue
            depth += (text[end] == "{") - (text[end] == "}")
            if depth == 0:
                records.append((match[1], text[match.start() : end + 1]))
                break
        else:
            raise AssertionError(f"Unclosed entry: {match[1]}")
    return records


def main() -> None:
    opus_path = BASE / "opus/references.bib"
    sol_path = BASE / "sol/references.bib"
    opus = entries(opus_path.read_text())
    sol = dict(entries(sol_path.read_text()))
    indexed = {}
    for key, entry in opus:
        match = re.search(r"eprint\s*=\s*\{(\d{4}\.\d{4,5})(?:v\d+)?\}", entry)
        if match:
            indexed[match[1]] = (key, entry, opus_path)
    indexed["2610.01045"] = (
        "empty_commitments_v2",
        sol["empty_commitments_v2"],
        sol_path,
    )
    indexed["2610.21203"] = (
        "commitment_standing",
        sol["commitment_standing"],
        sol_path,
    )
    output, registry = [], []
    for arxiv, version in VERSIONS.items():
        key, original, origin = indexed[arxiv]
        entry = re.sub(
            r"(eprint\s*=\s*\{)[^}]+", lambda m: m[1] + arxiv + version, original
        )
        url = f"https://arxiv.org/abs/{arxiv}{version}"
        entry = re.sub(r"(url\s*=\s*\{)[^}]+", lambda m: m[1] + url, entry)
        output.append(entry)
        registry.append(
            {
                "key": key,
                "arxiv_version": arxiv + version,
                "url": url,
                "origin": str(origin.relative_to(BASE)),
                "original_entry_sha256": sha(original),
                "selected_entry_sha256": sha(entry),
                "inspection": METHODS.get(
                    arxiv,
                    "Astra primary abstract/metadata; any deeper peer inspection is attributed in the linked literature ledgers, not implied here.",
                ),
                "accessed": "2026-10-29",
            }
        )
    for key, url in PAGES.items():
        original = dict(opus)[key]
        entry = original[:-1].rstrip() + f",\n  url = {{{url}}}\n}}"
        output.append(entry)
        registry.append(
            {
                "key": key,
                "url": url,
                "origin": "opus/references.bib",
                "original_entry_sha256": sha(original),
                "selected_entry_sha256": sha(entry),
                "inspection": "First-party page or repository documentation; see coauthor literature ledgers. Not a paper or an independent benchmark validation.",
                "accessed": "2026-10-29",
            }
        )
    assert len(output) == 34 and len({x["key"] for x in registry}) == 34
    bib = (
        "% Selected phase-3 drafting library. Versions and provenance: reference_registry.json.\n\n"
        + "\n\n".join(output)
        + "\n"
    )
    assert len(entries(bib)) == 34
    (BASE / "references.bib").write_text(bib)
    (BASE / "reference_registry.json").write_text(
        json.dumps(
            {
                "scope": "30 selected papers plus 4 first-party pages/repository records. Coauthor broader libraries remain separate. Assembly does not upgrade inspection depth or establish novelty by absence.",
                "references": registry,
                "source_sha256": {
                    str(p.relative_to(BASE)): sha(p.read_text())
                    for p in (opus_path, sol_path)
                },
                "script_sha256": sha(Path(__file__).read_text()),
                "bibliography_sha256": sha(bib),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Built {len(registry)} versioned/provenance-linked references")


if __name__ == "__main__":
    main()
