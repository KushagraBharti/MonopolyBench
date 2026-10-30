"""Build references.bib from parsed arXiv metadata plus a hand-checked venue map.

Usage: python3 -I build_bib.py <arxiv_metadata.json> <out.bib>
Venue strings come only from VENUES below; each records the source of the
venue claim. Entries without a verified venue are emitted as @misc preprints.
Non-arXiv sources (author pages, journal articles, software) are in EXTRA.
"""
import json
import sys

# key: (arxiv_id, entry_type, venue_or_None, venue_source, note)
VENUES = {
    "li2026arena": ("2608.14825", "misc", None, "arXiv v3 has no venue", "Vending-Bench Arena corpus study"),
    "backlund2025vendingbench": ("2502.15840", "misc", None, "arXiv v1 has no venue", ""),
    "wu2026agentmonopoly": ("2610.29330", "misc", None, "arXiv v2 has no venue", "Code: https://github.com/SuELS-Group/Agent_Monopoly"),
    "hu2026finboardbench": ("2605.27896", "misc", None, "arXiv comments: Preprint", ""),
    "zhang2026dece": ("2610.35773", "misc", None, "arXiv v1 has no venue", "DECE"),
    "muller2026cattletrade": ("2605.14537", "inproceedings", "MALGAI Workshop at ICLR 2026", "arXiv comments", "Workshop paper"),
    "zheng2026marketbench": ("2604.05523", "misc", None, "ACL 2026 indicated only by aggregator; unverified", ""),
    "bansal2025magentic": ("2510.25779", "misc", None, "arXiv; also MSR-TR-2025-50 per search, not opened", ""),
    "zhou2024sotopia": ("2310.11667", "inproceedings", "International Conference on Learning Representations (ICLR 2024), spotlight", "OpenReview mM7VurbA4r", ""),
    "bianchi2024negotiationarena": ("2402.05863", "inproceedings", "Proceedings of the 41st International Conference on Machine Learning, PMLR 235:3935--3951", "PMLR page bianchi24a", ""),
    "pan2023machiavelli": ("2304.03279", "inproceedings", "International Conference on Machine Learning (ICML 2023), oral", "OpenReview nkals4A4Vs; arXiv comments", ""),
    "shi2026cheaptalk": ("2604.04782", "inproceedings", "ICLR 2026 Workshop on AI for Mechanism Design and Strategic Decision Making", "arXiv comments", "Workshop paper"),
    "shi2026agentslie": ("2607.05132", "inproceedings", "ICML 2026 NExT-Game Workshop (Best Paper Award)", "arXiv comments", "Workshop paper"),
    "shi2026emergentcollusion": ("2609.24967", "misc", None, "arXiv v2 has no venue", ""),
    "keppo2026fragility": ("2603.20281", "misc", None, "arXiv v1 has no venue", ""),
    "fish2024algorithmic": ("2404.00806", "misc", None, "arXiv comments say Accepted to EC 2026; proceedings not opened", "Accepted to EC 2026 per arXiv comments"),
    "motwani2024secret": ("2402.07510", "misc", None, "NeurIPS 2024 indicated by aggregator only", ""),
    "elzou2025moloch": ("2510.06105", "misc", None, "arXiv v2 has no venue", ""),
    "golechha2025amongus": ("2504.04072", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2025), spotlight", "OpenReview XP3v1THxsq; arXiv journal-ref", ""),
    "ogara2023hoodwinked": ("2308.01404", "misc", None, "arXiv", ""),
    "scheurer2023strategic": ("2311.07590", "misc", None, "arXiv; no venue verified", ""),
    "park2023deception": ("2308.14752", "misc", None, "Patterns indicated by aggregator only", ""),
    "ren2025mask": ("2503.03750", "misc", None, "arXiv; no venue verified", ""),
    "akata2023repeated": ("2305.16867", "misc", None, "Nature Human Behaviour indicated by aggregator only", ""),
    "mukobi2023welfare": ("2310.08901", "misc", None, "arXiv", ""),
    "piatti2024govsim": ("2404.16698", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024)", "OpenReview 0zWzJj6lO3; arXiv comments", ""),
    "leibo2021meltingpot": ("2107.06857", "inproceedings", "Proceedings of the 38th International Conference on Machine Learning, PMLR, pp. 6187--6199", "arXiv journal-ref", ""),
    "vezhnevets2023concordia": ("2312.03664", "misc", None, "arXiv; software google-deepmind/concordia not opened", ""),
    "park2023generative": ("2304.03442", "misc", None, "UIST 2023 indicated by aggregator only", ""),
    "liu2024agentbench": ("2308.03688", "inproceedings", "International Conference on Learning Representations (ICLR 2024)", "arXiv comments", ""),
    "zhou2024webarena": ("2307.13854", "inproceedings", "International Conference on Learning Representations (ICLR 2024)", "OpenReview oKn9c6ytLx", ""),
    "xie2024osworld": ("2404.07972", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024), Datasets and Benchmarks Track", "OpenReview tN61DTr4Ed", ""),
    "yao2025taubench": ("2406.12045", "inproceedings", "International Conference on Learning Representations (ICLR 2025)", "OpenReview roNSXZpUDN", ""),
    "debenedetti2024agentdojo": ("2406.13352", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024), Datasets and Benchmarks Track", "OpenReview m1YYAQjO3w", ""),
    "chan2025mlebench": ("2410.07095", "inproceedings", "International Conference on Learning Representations (ICLR 2025), oral", "OpenReview 6s5uXNWGIh", ""),
    "xu2025theagentcompany": ("2412.14161", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track", "OpenReview LZnKNApvhG", ""),
    "ma2024agentboard": ("2401.13178", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024), Datasets and Benchmarks Track, oral", "OpenReview 4S8agvKjle", ""),
    "kapoor2026hal": ("2510.11977", "inproceedings", "International Conference on Learning Representations (ICLR 2026)", "ICLR 2026 proceedings abstract page", ""),
    "kwa2025timehorizons": ("2503.14499", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2025)", "arXiv journal-ref", "arXiv v4 title: Measuring AI Ability to Complete Long Software Tasks"),
    "paglieri2025balrog": ("2411.13543", "inproceedings", "International Conference on Learning Representations (ICLR 2025)", "arXiv comments", ""),
    "costarelli2024gamebench": ("2406.06613", "misc", None, "arXiv", ""),
    "duan2024gtbench": ("2402.12348", "misc", None, "arXiv", ""),
    "bonjour2022monopoly": ("2103.00683", "article", "IEEE Transactions on Emerging Topics in Computational Intelligence", "arXiv comments: accepted in IEEE TETCI", "Volume/pages not verified"),
    "zhu2025abc": ("2507.02825", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track", "OpenReview E58HNCqoaA", ""),
    "reuel2024betterbench": ("2411.12990", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024), Datasets and Benchmarks Track, spotlight", "OpenReview hcOq2buakM; arXiv comments", ""),
    "kapoor2024agentsmatter": ("2407.01502", "misc", None, "TMLR indicated by aggregator only", ""),
    "miller2024errorbars": ("2411.00640", "misc", None, "arXiv", ""),
    "biderman2024lessons": ("2405.14782", "misc", None, "arXiv", ""),
    "ren2024safetywashing": ("2407.21792", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2024)", "arXiv comments", ""),
    "turpin2023unfaithful": ("2305.04388", "inproceedings", "Advances in Neural Information Processing Systems (NeurIPS 2023)", "arXiv comments", ""),
    "lanham2023faithfulness": ("2307.13702", "misc", None, "arXiv", ""),
    "baker2025monitoring": ("2503.11926", "misc", None, "arXiv", ""),
    "korbak2025monitorability": ("2507.11473", "misc", None, "arXiv", ""),
    "schoen2025antischeming": ("2509.15541", "misc", None, "arXiv", ""),
    "lynch2025agentic": ("2510.05179", "misc", None, "arXiv", ""),
    "tang2026emptycommitments": ("2610.01045", "misc", None, "arXiv v2 has no venue", "Found by Sol; abstract verified by Opus"),
    "wei2026standing": ("2610.21203", "misc", None, "arXiv v1 has no venue", "Found by Sol; abstract verified by Opus"),
    "greenblatt2024alignmentfaking": ("2412.14093", "misc", None, "arXiv", ""),
}

EXTRA = r"""
@misc{andon2026arena,
  author = {{Andon Labs}},
  title = {Vending-Bench Arena},
  howpublished = {Author evaluation page, \url{https://andonlabs.com/evals/vending-bench-arena}},
  note = {Not peer reviewed. Accessed 2026-10-29; rounds \#1--\#14 listed},
  year = {2026}
}

@misc{andon2026vb2,
  author = {{Andon Labs}},
  title = {Vending-Bench 2},
  howpublished = {Author evaluation page, \url{https://andonlabs.com/evals/vending-bench-2}},
  note = {Not peer reviewed. Accessed 2026-10-29},
  year = {2026}
}

@misc{metr2026page,
  author = {{METR}},
  title = {Task-Completion Time Horizons of Frontier {AI} Models},
  howpublished = {Author page, \url{https://metr.org/time-horizons/}},
  note = {Page states last updated September 8, 2026 and no longer actively updated. Accessed 2026-10-29},
  year = {2026}
}

@misc{agentmonopoly2026repo,
  author = {{SuELS Group}},
  title = {Agent\_Monopoly},
  howpublished = {Software repository, \url{https://github.com/SuELS-Group/Agent_Monopoly}},
  note = {Apache-2.0. README read at commit 2434f4278bf2970237ba82399db191e0116f3d35 (2026-10-21)},
  year = {2026}
}

@article{meta2022cicero,
  author = {{Meta Fundamental AI Research Diplomacy Team (FAIR)} and Bakhtin, Anton and Brown, Noam and others},
  title = {Human-level play in the game of {Diplomacy} by combining language models with strategic reasoning},
  journal = {Science},
  volume = {378},
  number = {6624},
  pages = {1067--1074},
  year = {2022},
  doi = {10.1126/science.ade9097},
  note = {Metadata verified via Crossref}
}
"""


def esc(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def main() -> None:
    meta = json.load(open(sys.argv[1]))
    out = ["% Generated by scripts/build_bib.py from arxiv_metadata.json (checked 2026-10-29).",
           "% venue_source gives the basis for each venue string; misc = no verified venue.", ""]
    for key, (aid, etype, venue, vsrc, note) in VENUES.items():
        m = meta[aid]
        authors = m["authors"]
        auth = " and ".join(authors) if len(authors) <= 15 else " and ".join(authors[:15]) + " and others"
        last_v, last_d = m["versions"][-1]
        year = (venue and next((y for y in ("2021", "2022", "2023", "2024", "2025", "2026") if y in venue), None)) or last_d[-4:] if venue else m["versions"][0][1][-4:]
        fields = [f"  author = {{{auth}}}", f"  title = {{{{{esc(m['title'])}}}}}"]
        if etype == "inproceedings":
            fields.append(f"  booktitle = {{{esc(venue)}}}")
        elif etype == "article":
            fields.append(f"  journal = {{{esc(venue)}}}")
        fields += [f"  year = {{{year}}}", f"  eprint = {{{aid}}}", "  archivePrefix = {arXiv}",
                   f"  url = {{https://arxiv.org/abs/{aid}}}"]
        n = f"Checked arXiv {last_v} ({last_d}). Venue source: {vsrc}."
        if note:
            n += " " + note + "."
        fields.append(f"  note = {{{esc(n)}}}")
        out.append(f"@{etype}{{{key},\n" + ",\n".join(fields) + "\n}\n")
    out.append(EXTRA.strip() + "\n")
    open(sys.argv[2], "w").write("\n".join(out))


if __name__ == "__main__":
    main()
