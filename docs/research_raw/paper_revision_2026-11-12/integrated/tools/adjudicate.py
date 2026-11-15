"""Record editorial decisions; does not alter review or manuscript sources."""
from pathlib import Path
import json
import hashlib
HERE=Path(__file__).resolve().parents[1]
REVIEWS=HERE.parent/"reviews"
groups=[
    ("scoped-statement-action",["AR01","AR05","SC-05","XR-F52-11"],"Accepted: scope correspondences to the sixteen episodes and selected incidents; no general predictive rule or nested evidence ladder."),
    ("capacity-null",["AR02","SC-04","OPX-04","XR-F52-04"],"Accepted: no null-sensitivity claim; do not promote exploratory capacity bins."),
    ("accuracy-and-information",["AR03","AR04","SC-02","OPX-05","XR-F52-03"],"Accepted with a narrower presentation: full sixteen fields, explicit resource omissions, no aggregate recall/assessment-accuracy score."),
    ("resampling",["AR06","SC-08","OPX-07","XR-F52-09"],"Modified: block points and omission ranges in the main figure; all three weighting schemes in a supplement table with distinct targets."),
    ("requirements",["AR07","SC-03","OPX-06","XR-F52-02"],"Accepted: financing requirements, never calibrated difficulty."),
    ("first-action",["AR08","SC-01","OPX-02","XR-F52-01"],"Accepted as context: initial actions, compulsory menus and payability definition stated; no classifier score or new matched-shortfall headline."),
    ("note-origin",["AR09"],"Accepted: model-authored notes distinguished from fallback notes."),
    ("episode-label",["AR10","SC-07"],"Accepted: no G18/Park Place misattribution; full G8 and G18 fields printed."),
    ("full-fields",["AR11"],"Accepted: all sixteen full initial fields printed with a uniform channel-selection rule and source manifests."),
    ("offer-denominator",["AR12","OPX-03"],"Accepted: complete four-form census; no 3/186 completion-effect headline."),
    ("conflict-scope",["AR13","XR-F52-08"],"Accepted: selected Grok action-name conflict screen, seven response-side acceptance conflicts; no uniqueness or causal claim."),
    ("forms",["SC-06","XR-F52-13"],"Accepted: cash asks retained separately, all zero cells shown."),
    ("feasibility",["SC-09"],"Accepted: sufficient arithmetic bounds are not legal-route witnesses."),
    ("request-provenance",["SC-10","OPX-14"],"Accepted: saved request records and source commits, distinct request/attempt counts."),
    ("dice-event",["SC-11"],"Accepted: direct nine on one roll; does not include doubles continuation."),
    ("scenario-note",["OPX-01"],"Accepted: liquidation note printed and independently checked across 338 initial payloads."),
    ("counter-baselines",["OPX-08"],"Accepted by selection: retain counter counts with the non-completing baseline; omit unvalidated refusal-style screens."),
    ("recipient-composition",["OPX-09"],"Accepted: exact -0.2 to +8.5 range and recipient counts."),
    ("third-party-warnings",["OPX-10","XR-F52-19"],"Accepted: G2 and G15 delivered public appeals included without a persuasion claim."),
    ("causal-wording",["OPX-11","XR-F52-14"],"Accepted: stated concern and subsequent refusal, not because-of causation."),
    ("small-cell",["OPX-12"],"Accepted: preserve counts but suppress a gap when either proposer cell has fewer than five offers."),
    ("title",["OPX-13","XR-F52-10"],"Accepted: title names stated plans and economic actions."),
    ("case-depth",["OPX-15","XR-F52-15"],"Partly accepted: continuation facts retained and refined; eight compact main-text incidents retained to meet the user's preference."),
    ("refusal-cause",["OPX-16","XR-F52-17"],"Accepted: provider message and recovery association stated; structured historical category remains unavailable."),
    ("g13-motives",["XR-F52-05","XR-F52-06","XR-F52-07"],"Accepted: complete relevant buyer excerpt includes both estate motives; pitch probability miscount dated."),
    ("keyword",["XR-F52-12"],"Accepted: no lexical screen promoted as a semantic result or abstract claim."),
    ("economic-context",["XR-F52-16"],"Accepted: investment, competing finance and nonterminal inheritance context retained."),
    ("positive-revision",["XR-F52-18"],"Accepted: G5 correction extracted from its original provider field and paired with the applied budget and payment."),
    ("core-prose",["XR-F52-20"],"Adapted: full-paper integration uses the strongest prose without adopting unsupported claims.")
]
decisions={fid:dict(topic=topic,decision=decision) for topic,ids,decision in groups for fid in ids}
out=[]
for author in ["astra","sol","opus","fable_5_2"]:
    p=REVIEWS/author/"findings.json"
    source=json.loads(p.read_text())
    rows=source if isinstance(source,list) else source["findings"]
    for f in rows:
        fid=f["id"]
        assert fid in decisions,fid
        out.append(dict(reviewer=author,id=fid,severity=f["severity"],
            source=str(p.relative_to(HERE.parent)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            **decisions[fid]))
assert len(out)==60
(HERE/"adjudication.json").write_text(json.dumps(out,indent=2)+"\n")
print(f"Recorded {len(out)} review decisions.")
