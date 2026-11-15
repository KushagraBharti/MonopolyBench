#!/usr/bin/env python3
"""Single source for the proposed replacements.

Writes ../replacement_prose.tex. With --apply, it also copies the integrated static
sources into ../amended_build/, applies every replacement (each old string must occur
exactly once), and leaves the copy ready to compile there. The pinned integrated
package is only read, never written.
"""
import json, pathlib, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
REVIEW = HERE.parent
INT = REVIEW.parents[1] / 'integrated'

R = []
def rep(rid, tier, file, why, old, new):
    R.append(dict(id=rid, tier=tier, file=file, why=why, old=old, new=new))

# ---------------- material ----------------
rep('M1', 'material', 'sections/main.tex',
    'One of the 28 (G7 d318) was offered no building sale; "preference"/"choices" overstate a descriptive count.',
    "Asset selection shows a consistent preference in one defined population. Of the 62 episodes payable from cash and initially listed mortgages, thirty debtors own buildings. Twenty-eight pay without selling any; the other two, both Opus, sell one house each. These choices preserve development when mortgages already provide sufficient financing. They describe the assets retained, without establishing that the chosen route minimizes cost or maximizes future income.",
    "Asset selection shows a consistent pattern in one defined population. Of the 62 episodes payable from cash and initially listed mortgages, thirty debtors own buildings. Twenty-eight pay without selling any; the other two, both Opus, sell one house each. In one of the twenty-eight, G7 d318, the menu offers no building sale, so 27 of the 29 debtors offered a sale keep every building. The pattern describes the assets retained when mortgages already suffice, without establishing that the chosen route minimizes cost or maximizes future income.")

rep('M2', 'material', 'sections/main.tex',
    'Only Grok\'s content names a liquidation action (27/56); Sol 0/93, Gemini 0/89, Opus 0/100. "Much more observable" implies nonzero observability elsewhere.',
    "A broader scan finds nine named-action conflicts in 338 liquidation decisions, all Grok, but explicit action naming is much more observable in Grok's content; it is not an equivalent conflict-rate comparison across systems.",
    "A broader scan finds nine named-action conflicts in 338 liquidation decisions, all Grok. Only Grok's assistant content names a liquidation action (27 of its 56 decisions); the other systems' content is absent or names none, so the scan cannot observe their conflicts and supplies no cross-system conflict rate.")

rep('M2b', 'material', 'sections/final_supplement.tex',
    'Same observability precision in the supplement, with the exact denominators.',
    "The named-action scan across 338 decisions is narrower: direct prose action naming is observable in 27 of Grok's 56 liquidation responses and not equivalently exposed by other configurations.",
    "The named-action scan across 338 decisions is narrower: assistant content names a liquidation action in 27 of Grok's 56 liquidation responses and in none of the other configurations' 282. Sol and Gemini return no assistant content in these decisions; 19 of Opus's 100 responses have content, none naming an action.")

rep('M3', 'material', 'sections/main.tex',
    'The two readings were not blind (packaged comparison records first-row exposure); population concentrated in G1 and G15.',
    "Two Astra readings agree on explicit trade-linked rival consequences in 61 of 74 legally acceptable recipient-completing refusals: 27/38 recipient-only and 34/36 both-completing.",
    "Two model-assisted Astra readings, not blind to each other, both find explicit trade-linked rival consequences in 61 of 74 legally acceptable recipient-completing refusals: 27/38 recipient-only and 34/36 both-completing. G1 and G15 contribute 34 of the 74.")

rep('M3b', 'material', 'sections/final_supplement.tex',
    'State non-blindness and concentration where the coding is defined.',
    "The reported 61 is this intersection, not an adjudicated exhaustive count.",
    "The reported 61 is this intersection, not an adjudicated exhaustive count. The comparison file records a shared source, first-row exposure and category-boundary ambiguity, so the agreement is not a blind validation. The population is concentrated: G1 contributes 22 records and G15 twelve, and Grok and Gemini are the recipients in 31 each.")

rep('M4', 'material', 'sections/main.tex',
    'Brief requires memory and statement/action literature; integrated cites neither. Sources verified at primary pages on 15 Nov 2026.',
    "They support a more specific observational distinction between recognizing the inventory needed to pay and accepting the next legal financing action.",
    "They support a more specific observational distinction between recognizing the inventory needed to pay and accepting the next legal financing action.\n\n"
    "Statement--action gaps and memory effects are also established. Declared plans often diverge from executed structure~\\cite{oota2026declare}, and agents can reason that an action violates a stated rule and then submit it~\\cite{co2026atomic}. Grok's channel conflicts belong to this family; the harness makes them visible by retaining every channel. Errors in stored experience can propagate into later decisions~\\cite{xiong2026memory}. The carried \\$130 and \\$30 figures are consistent with such reuse but also equal the current menu's mortgage values, so these records do not test it.")

rep('M5', 'material', 'sections/final_supplement.tex',
    'Versioned rules: map games to commits and give the engine/board hashes that identify the implemented rules (verified from git blobs and run manifests).',
    "The runs use source commits \\path{42f85183fa772b2ab3759cc49987e5ed6cc9efcc} and \\path{d6808534a831862682a6940f394c6c87bb2691cb}.",
    "Games G1--G4 ran at source commit \\path{42f85183fa772b2ab3759cc49987e5ed6cc9efcc} and G5--G20 at \\path{d6808534a831862682a6940f394c6c87bb2691cb}, as recorded in each run's \\path{cloud/execution_manifest.json}. The implemented rules are identified by \\path{python/packages/engine/src/monopoly_engine/engine.py} (SHA-256 \\path{122edf5f16db0c4b8e0bd475ded73bf70a2b08065304d0517b8f8e2c98d63e0d}) and \\path{contracts/data/board.json} (SHA-256 \\path{fc30829e23b8dc9df27235d967afc7f4861f4e116fb3cde576e29e8a178ab774}), byte-identical at both commits.")

# ---------------- optional ----------------
rep('O1', 'optional', 'sections/main.tex',
    'Strongest omitted positive insight: Gemini publicly understates its financing capacity while its same-response note counts $450 of mortgageable deeds; Sol discounts the claim; Gemini then mortgages exactly $450.',
    "Gemini counters at \\$520, explicitly calculating Sol's remaining development cost; Sol maintains its ask after noting that Gemini can mortgage other deeds to fund oranges. Gemini pays \\$700, mortgages five deeds and builds four orange houses.",
    "Gemini counters at \\$520, explicitly calculating Sol's remaining development cost and publicly claiming that \\$700 would leave it unable to build, although its note in the same response counts \\$450 of mortgageable deeds. Sol's note calls that constraint overstated, and Sol holds its ask. Gemini pays \\$700, mortgages five deeds for exactly \\$450 and builds four orange houses.")

rep('O1b', 'optional', 'sections/casebook.tex',
    'Casebook counterpart of O1; the inline words are exact substrings of G7 d143.',
    "Sol maintains its ask after considering Gemini's other financing:",
    "Gemini's public message also says that \\$700 would leave it ``unable to build'', while its private note in the same response counts ``\\$450 in mortgageable non-Orange properties''. Sol maintains its ask after considering that financing:")

rep('O1c', 'optional', 'sections/casebook.tex',
    'Record that the realized mortgages equal the privately counted capacity.',
    "Gemini pays \\$700, mortgages five deeds and builds four orange houses that turn.",
    "Gemini pays \\$700, mortgages five deeds for \\$450 and builds four orange houses that turn.")

rep('O2', 'optional', 'sections/final_supplement.tex',
    'Locked/unlocked split (27/27 vs 16/21) and the three listed-only maxima on unpayable debts, without an exhaustive denominator.',
    "This is a numeric-presence description, not an accuracy rate for whole assessments.",
    "All 27 responses whose debtor has no locked collateral ($U_0=U_*$) contain such a numeral, as do 16 of the 21 with locked collateral. Of the five without one, two itemize the released mortgages without a total, and three (G3 d426, G5 d309 and G8 d280) state exactly $U_0$ as the maximum, the listed-only form of the two payable failures, here on debts that remain unpayable. This is a numeric-presence description, not an accuracy rate for whole assessments.")

rep('O3', 'optional', 'sections/main.tex',
    'Main text never references the complete first-action table that contextualizes "decisions to stop".',
    "All six are documented alongside the payable declaration in Appendix~\\ref{app:divergences}.",
    "All six are documented alongside the payable declaration in Appendix~\\ref{app:divergences}, where Table~\\ref{tab:first-actions} gives all 188 first actions as context rather than as a score.")

rep('O4', 'optional', 'sections/final_supplement.tex',
    'The third proof class is asserted, not argued; one clause closes it.',
    "In the third, hotel stock cannot obstruct continuation.",
    "In the third, bank houses minus four per remaining hotel never decrease, because a house sale raises the difference and a downgrade leaves it unchanged; a remaining hotel therefore always has four bank houses available.")

rep('O5', 'optional', 'manuscript.tex',
    'PDF metadata author and title are empty in the pinned PDF.',
    "\\title{Financial Assessment and Strategic Bargaining by LLM Agents\\\\in Twenty Complete Monopoly Games}",
    "\\hypersetup{pdftitle={Financial Assessment and Strategic Bargaining by LLM Agents in Twenty Complete Monopoly Games},pdfauthor={Kushagra Bharti}}\n\\title{Financial Assessment and Strategic Bargaining by LLM Agents\\\\in Twenty Complete Monopoly Games}")

rep('O6', 'optional', 'sections/final_supplement.tex',
    'Robustness of the selected-field rule, stated without changing it.',
    "Both available channels are printed below so readers can inspect that distinction.",
    "An independent all-channel reading in one frozen coauthor draft gives the same 5/3/5/1/2 split. Both available channels are printed below so readers can inspect that distinction.")

BIB = r"""@inproceedings{xiong2026memory,
  author = {Xiong, Zidi and Lin, Yuping and Xie, Wenya and He, Pengfei and Liu, Zirui and Tang, Jiliang and Lakkaraju, Himabindu and Xiang, Zhen},
  title = {How Memory Management Impacts {LLM} Agents: An Empirical Study of Experience-Following Behavior},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  pages = {623--645}, year = {2026}, doi = {10.18653/v1/2026.acl-long.27},
  url = {https://aclanthology.org/2026.acl-long.27/}}
@misc{oota2026declare,
  author = {Oota, Subba Reddy and Herrera, Francisco and Cabot Sagrera, Jordi and L{\'o}pez de Prado, Marcos and Khan, Shadab},
  title = {Do {LLM} Agents Execute the Plans They Declare? {F}rom Planning-Mode Declaration to Pattern-Specific Execution},
  year = {2026}, eprint = {2609.38108}, archivePrefix = {arXiv}, url = {https://arxiv.org/abs/2609.38108}}
@misc{co2026atomic,
  author = {Co, Ryan and Konuganti, Karthik R.},
  title = {Unpropagated Refutation in Atomic Chess: When Agents Identify Unsafe Actions and Take Them Anyway},
  year = {2026},
  howpublished = {Poster, Second Workshop on Agents in the Wild: Safety, Security, and Beyond, at ICML},
  url = {https://icml.cc/virtual/2026/67788}}
"""

def tex_escape_comment(s):
    return '\n'.join('% ' + line for line in s.splitlines())

def write_tex():
    out = [r"% Opus final review: minimal replacement prose for the pinned integrated candidate",
           r"% (integrated PDF e5c44beb...0dae). Each block gives file, tier, reason, the exact",
           r"% current text (commented) and its replacement. Every OLD string occurs exactly once",
           r"% in the pinned source; checks/replacements.py --apply verifies this and compiles a copy",
           r"% under amended_build/. Nothing here is a new evaluation; all numbers come from saved",
           r"% records checked in checks/. Material blocks are M*, optional blocks O*.", ""]
    for r in R:
        out.append('%' + '=' * 78)
        out.append(f"% [{r['id']}] {r['tier'].upper()} -- {r['file']}")
        out.append(tex_escape_comment('WHY: ' + r['why']))
        out.append('% OLD:')
        out.append(tex_escape_comment(r['old']))
        out.append('% NEW:')
        out.append(r['new'])
        out.append('')
    out.append('%' + '=' * 78)
    out.append('% [M4-bib] Append to final_references.bib (entries verified at primary pages 15 Nov 2026):')
    out.append(tex_escape_comment(BIB))
    (REVIEW / 'replacement_prose.tex').write_text('\n'.join(out) + '\n')
    (HERE / 'replacements.json').write_text(json.dumps(R, indent=1) + '\n')

def apply():
    dst = REVIEW / 'amended_build'
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir()
    for name in ['.latexmkrc', 'build.sh', 'manuscript.tex', 'preamble.tex', 'references.bib',
                 'supplemental.bib', 'new_references.bib', 'final_references.bib']:
        shutil.copy2(INT / name, dst / name)
    shutil.copytree(INT / 'sections', dst / 'sections')
    shutil.copytree(INT / 'assets', dst / 'assets')
    for r in R:
        p = dst / r['file']
        s = p.read_text()
        n = s.count(r['old'])
        assert n == 1, (r['id'], n)
        p.write_text(s.replace(r['old'], r['new']))
    with open(dst / 'final_references.bib', 'a') as f:
        f.write('\n' + BIB)
    print('applied', len(R), 'replacements into', dst)

if __name__ == '__main__':
    write_tex()
    if '--apply' in sys.argv:
        apply()
