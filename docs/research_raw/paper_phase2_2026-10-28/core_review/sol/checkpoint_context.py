"""Persist manually authored scope/provenance notes; never infer review labels."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    path = HERE / "progress.json"
    progress = json.loads(path.read_text())
    additions = {
        "original_checks": [
            "Own corpus_economics_audit.json reconstructs all6989initialcash/holdings/development/bankstocks and matches103spendunits103450outlay93000wholegamerent92550postfirstownspend40zero26alsozeroelimination54of60winnercreditor57builtcolors,58winnergroups34containinginheriteddeedbut30firstcompleteviaestate. Five seeds/four rotations each; balancedseats; twofingerprints,not causalcodecomparison.",
            "Own build_recovery_audit.json replaysall20actualcanonicaleventstreams and locallyexecutes61Opusdefaultplanswithsamepurchasesafterinterleaving. Twoincludehoteloperations requiringgroupfinish/stockreturn. Sol4defaultshave8parsedplans,7unaffordableandG4d174firstlegal700to5;smalleronehouselegalall66defaults. UnevenrecoveriestoanybuildArgon18/19Sol25/29Grok5/5Opus0/61; preservingwithin-decision6/20/5/0, changing12/5/0/0.",
            "Own trade_timeline_audit.json independently matches44of113acceptedreversals682prompts,26of413rejectmisattributions383,232of394selfpartnercounters2022; union2054of6989initialprompts. Initialonly, ambiguousduplicateidenticalrowsnotuniqueeventreliance.",
            "Own received_name_conflict_audit.json independently reconstructs139Grokcontent/toolnamedconflicts:137structurednested,1flatG9d194,1malformednamedG19d224.15equalparsedargumentobjectcases:7buyauction,4rejectaccept,4jail. Only5literalJSONargumentsubstringsbyteequal, other10differinspacing/escaping, so15byte-identicalwordingrejected. Rawtoolnameequalsparsed/appliedin15;upstreamandstreamassemblyunexcluded.28accepts32voluntaryauction61jaildenominators.",
            "Complete G19d135/136, G18d083 and G20d001/004availableoriginalbundles nowread. additional_social_channel_checks.json verifiesG19explicitpremisecorrectionwithacceptance/channelconflict, G18nonidenticalrejectacceptsale130Baltic, andG20actualpublicprivate-noteexposureandrecipientrecognition. No reliance, deliberategifting/leakage, uniqueintentorprovidermechanism inferred.",
            "All 240 fixed common original bundles are completely read and manually judged. All 614 catalog initial judgments remain preserved. Complete historical note trails15–20 are read. No partly read common bundle remains.",
            "G19 common originals and77-line historical notes complete. Exact220pink rents450/450/500correct own initial false States500/Virginia550gloss;269three rails100each;234interleaved nine-house red target legal262, actual234/235/236same-turn layers reach it. Proposed later red-rent correction failed assertion and was withdrawn; initial700/700/750was right.",
            "G20 all twelve common originals and98-line historical notes complete. Complete nonsample235and325read. Conditional actual400accept at235funds4orange houses41while preserving browns, or6with91after legal brown liquidation. Later257actual250accept funds6with64without selling browns. Actual327–336replayed legal700salvage+665mortgages from49 pays1400retain14.325correct1414total has offsetting component errors; provider adds200costwhileappliedprivatesubtracts correctly.",
            "G20sample200cash-only death rationale checked by exact prior actual191Gemini/192Grok management sequences matching focal200cash, holdings and building stocks. Full legal finance reaches1383/566. No artificial debt/control, no future roll or action causation inferred. B&Ounowned inventory differs, not falsely asserted equal.",
            "G12complete061and239originals read after Astra semantic nomination.061conditional does not establish orange membership/dependency;239private/provider explicitly recognizes sales/current2/2/3, forwardholdnotstale. Corroborates own initial qualified/contradicted labels; opaque text unavailable.",
            "G18 all twelve common originals and complete113-line historical note trail read. Complete431/441/442 originals verify last standing250in BOTHactualmemories, invocation and withdrawal after another750payment/major liquidation, not costly reliance/initial dishonesty. Exact284fivehousesales/unlockedDBmortgages876;341Parkredemption/remortgages596;254conditional ECplus150accept/Pacificmortgage/one150yellowhouse71.244NCtoDB5/7is10/36not22or25percent; TNtoNYrequires1.254/341full providers unread.",
            "G17 all twelve common original bundles and complete97-line historical note trail read. Exact236full management liquidation759not599; NC mortgage/three fourth houses plus retrenchment684not524.241actual one fourth934and conditional second909, not774/749. Canonical236position36corrects own initial7gloss; delivered CHANCEhas no index.237/241full providers unread.",
            "G16 all twelve common originals and complete120-line historical note trail read. New exact173spare425not435 gives592, hotel downgrade reaches617.261three/four-house builds and full legal retrenchment reach615/565, refuting a literal next550fatality.322conditional rail acceptance permits seller immediate Park redemption/one BW house99;429conditional EC acceptance leaves77 and raises active WW28to70despite mortgaged EC.429full provider remains unread.",
            "G15 all twelve common original bundles and the complete 87-line historical note trail read. Samples252/189/271 show chosen rail reserves, paid-exit versus doubles-exit rules, current correct three-rail count after an earlier four-rail error, and an unaccepted conditional redemption overbudget. Historical narrative reading is not an independent original audit of every assertion in that narrative.",
            "G14all12commonbundlescomplete;145original8houseplaninterleavedlegal619,actualretry2houses919then145-148sameturn4managementdecisionsreach8/619;162actualredemptionactiveAtlantic44Marvin48unchanged;161interest13makes396activationnot383;147/148/161/162fullprovidersunread",
            "G13samples160/171completeplus272nonsamplecomplete:legalcontentbuild57from357andmortgage309from179versusreceivedEND/phantomprivate;171providercorrectspriorphantom;conditional500Parkacceptance+redemption+sparemortgagespermitsonehouse28,conditional150twohouses68including18transferinterest",
            "G12complete146-151Virginiaexchange:publicinabilityversusown3/4housecapacity;recipient151explicit686and100/house/ownbluefundingmotive;147providerrolereversal;actual152threeRRmortgagesplusBW/PP/BWlegally2/3and195,notblockedat2/2",
            "G12sample312legalCTsale/KYhouse/Readingmortgage/Statessale/Indianahouse/Pennmortgage/IllinoisHOTELends26bank4;242Balticmortgage/Orientalhouseends5;073rivalfinancingends55;291physicalhouses31not27;073and291fullproviderunread",
            "G16d602 exact4831prefix/23legalactions reach1393; applied private already correct1393, own DB build600/salvage300/zero developed paidrent and274-to275explicit changed reserve choice",
            "All60canonical eliminations independently screened;56declarations/4automatic,56belowfullupper,3current-debt-financing-feasible,1hotel-lock; G17d234fivehousesales/Baltic/Parkmortgages pay550retain155andclearBoardwalk",
            "G7d339 actual sole Oriental50mortgage from390 triggers automatic estate440against750; nominal1310notaccessible in debt",
            "G6sample190fullbundle plus adjacent191exact1471prefix Pacific150mortgage/KY150house reduces nominal800to725; no actual alternate debt or dice",
            "G2d062/d247 complete available nonsample bundles: explicit execution recognition across explanatory channels versus applied ProbeOnly/private alongside content/provider END",
            "G7d183 exact1270prefix two100rail mortgages/nine interleavedpinkhouses leaves19 from719; sample182fullbundle and183menu/actions/events, not183fullproviderbundle",
            "G7d329 fullsamplebundle/exact2296prefix legalSolp4hotel100leaves55bank6, opponent hotelsale supplypredicate changes; actual330p3management separately permits ownhotel100to430/bank6, no changed later trajectory or escape339claim",
            "G7sample077 delivered trade30history reversed; canonicald062events435-438cash300andWWp3top1,SLp1top3; no reliance",
            "G8sample177 complete original including separately repaired longreasoning: content2/2/3build versus receivedEND/private4cash; actual704bare, exact1272prefix interleaved700buildlegalleaves4",
            "G10sample132 complete36653characterreasoning repaired; provider explicitlycorrects489survivesallfourhouseLB while appliedprivate saysotherwise; directReading5toVT8/CT9sums3/4not2/4/5",
            "G10sample053/044 pairedactualKentuckyd043events317-320p1pays260top3andgetsdeed;deliveredacceptedrowreversedwhilecurrentnotesrecover",
            "G11complete066/219commonbundlesand121nonsample: exactlocaloneParkhouse+recordednextGO/Vermontleaves163;PAYversusROLLbothactual5+2to830actor/boardequalonly;conditionalartificialacceptanceprovesbilateralredcompletionpossible,notagreement",
            "G11complete255-258socialbundles:recipient256providerfirstechoesfalseVirginia-completionthenexplicitlycorrectsandREJECTS;proposerprivatefalsebothsets257acknowledgesmistake;258rejectsaccurateowncompletion",
            "G11complete267-268cardbundles:initial502generationerror/missingtool;retryCONTENTENDreceivedPROPOSEfreecardwithJokeprivate;recipientexposureandREJECT;44578renderedcharactersreadin3contiguouschunks"
        ],
        "additional_peer_informed_original_targets": [
            "Astra G12C002 d061withoutIllinois still cannotbuildTennessee can mean giving up redblocker does not resolve lone-orange inability, not false orange membership/dependency. C019d239fullcontent/providerrecognizes sales/current2/2/3, forward holdnotstale. Peer-informed before Sol complete originals; preserve initiallabels.",
            "Astra accepts G14 recovery horizon and G13 deferred-mortgage boundary. Her G10 Illinois/Kentucky round trip adds10cash while removing Illinois, and039private says do not send despite received proposal. This matches Sol earlier original g10_public_claim_checks; new peer message is corroboration, not an additional blind audit.",
            "Astra G9d130/131228cashbelow300andTRADE_RESPONSEhasnomortgage;collateraldoesnotproveimmediatenextlandingpurchaseaccess.Prior124management/latermanagementdistincttimes;acceptedwithoutclaimingownnewroute",
            "Astra G8d209public575plus100truefor3houses,butprivate3EACHfrom1/1needs800;all163/164/174/177planslegalnoenginefallback;277private666correctversus280declare386omits280unlockedmortgages,1100insolvencyunchanged",
            "Astra G6samples129validrefusal-recoveredENDand106contentexplicitlyavoidNY-for-STCbecauseSolorange/fourrails1511;chosenholdsnotdefaultedbuilds;acceptedG12thresholdandG11transientechoaspeer-informedpendingownfullsources",
            "Astra G7fresh330hotel100to430bank6thenVirginiahotelsale50to480bank2;143public700leaves45can'tbuildversusprivate450mortgages/144explicitcorrection/145accept/actual151400buildto95;167PP2BW3;16estate deeds;236to24912globaldecisions;339440includes290initialcash",
            "Astra G2d062explicitexecutionrecognition and247content/providerENDversusappliedProbeOnly, later fully independently source-read bySol",
            "Astra G3C011 actual182exposure to181/580calculation,194settlement861after23interest; C012Kentuckyunmortgaged120;582/583Readingalready100; terminal552/1074/617and426omittedunlockedLB160",
            "Astra G19d038IndianaGemini/Tennesseeunowned; d023explicitmissingIndiana andd022contentEND/toolpropose; received afterSolsource-leveltwo-redsnotmonopolyobjection butbeforeownfull038read",
            "Astra G3sampled207providerhouse100versustoolhold247/red150 andd054providerfalseLB/yellowsets; own fullsamplejudgments already retained, no blind recheck claimed",
            "Astra G4d346content3hotelslegalreleases12buttoolEND/zeroactualHOTEL_BUILT;d049OpusproviderEND/toolParkproposal;d208yellow2/3/3;fourParkproposals49/71/97/115;final2524=2314+210estate;d174firstsevenhouse700interleavedlegalto5, not all eight attemptedplansaffordable",
            "Astra G4Grok069/070/126providerfalseopponentmonopolies while appliednotesblockerscorrect,069withinresponsecorrection; received afterSolinitialG4samplejudgments",
            "Astra G5d30670cashLB2/3/3bank0artificialsupplyprobeallowsOriental50;freshlegalVermontsale+Orientalbuyreallocates3/2/3cash45bank0withoutnetexpansion;Solanalyticobjectionaccepted/executedbyAstra,notSolreplication",
            "Astra G5d258declared774followedactual263-265sales600plusunlocked375from74pay900retain149;terminal586/149/799and2450greenpaidrent/zeroGeminiDB;receivedafterSolG5initialpass",
            "Astra G6owncheckd173fourmortgages450from45thenthreeredhousesleave45;d221redemptions165/221legal;terminal595/102/211railrent1900and1800afterfourrailacquisition;peerinformedcorroborationnotownblindcheck"
        ]
    }
    for key, values in additions.items():
        target = progress.setdefault(key, [])
        for value in values:
            if value not in target:
                target.append(value)
    progress.setdefault("complete", False)
    progress["narrative_reading_scope"] = "All 20 completed trajectory conclusions and full historical note trails read. The durable earlier record confirms full Terra1–6 and B7–13 reading; G14 was completed in contiguous lines1–40,41–80,81–113 at final consolidation. Trails15–20 were completed and truncations repaired as individually recorded. All 614 catalog source entries and 240 complete common originals are read and judged. Narrative reading does not independently verify every original assertion."
    progress["pending_partially_read_sample"] = None
    path.write_text(json.dumps(progress, indent=2) + "\n")
    print("Persisted explicit original-check scope and peer-informed leads; no review labels generated")


if __name__ == "__main__":
    main()
