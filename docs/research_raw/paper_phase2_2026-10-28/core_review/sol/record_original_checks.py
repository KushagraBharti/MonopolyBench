"""Append manually authored original-audit updates without changing initial labels."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# These findings are authored after inspecting the exact outputs and originals.
UPDATES = {
    "public-G19-C009": ("additional_social_channel_checks.json", "Complete135/136 originals read after peer nomination.135content/provider chooseEND, applied private saysAbort/DoNotSend, received tool proposes false States-orange swap. Recipient136actually sees it, corrects color publicly and privately, accepts150plusVirginiaforStates withnoimmediatepinkmonopoly. No induceduptake ofthatproposition, uniqueproposerintent, alliance or originaldeception inferred."),
    "public-G18-C003": ("additional_social_channel_checks.json", "Complete083original now read. Content/provider reject Baltic130while receivedaccept/publicecho buyer valuation and appliedprivatekeepblocker. Actual130cash andBaltic3p3top4completebrown. Argumentsdiffer, notoneof15name-onlycases. No identifiedpersuasion, deliberategift orcoherentintention fromsettlementalone."),
    "public-G20-C010": ("additional_social_channel_checks.json", "Complete001/004 originals now read.001receivedpubliccontainsitsprivateverbatim, emitted event12and actual004memory.004privateexplicitlyrecognizesleak.001contentrequestsemptypublicbutrawtoolalreadycontainsexposedtext. Actualdisclosureandrecognitionsupported, not deliberateleakage, financialexploitation or localizedprovider/streamcause."),
    "public-G20-C015": ("g20_sample_financing_checks.json", "Complete235original:250five-red-housesclaimfalse at150each; cannot-develop400claim depends on scope. Exact actual400conditionalaccept leaves97after10interest, then455sparemortgages/111redemption/fourhouses400leaves41. Earlier six-house target not funded preserving brownhotels, but legal brown liquidation also permits six and91. No identified deceptive intent, optimal acceptance or alternate winner."),
    "public-G20-C020": ("g20_sample_financing_checks.json", "Exact actual327–336ten-decision sequence legally liquidates700buildings plus665mortgages from49, pays1400and retains14. Brown hotels first downgrade to four houses and then sell remaining houses. Full325bundle read: correct1414total hides offsetting25component errors and provider413plus200sign error while applied private correctly213."),
    "public-G20-C021": ("g20_sample_financing_checks.json", "Original hotel downgrades and later brown house sales execute legally at exact327prefix, no artificial stock.700building salvage not675,665mortgages not690, total1414unchanged. Actual bill paid and later rebuilt browns remain separate from an immediate-bankruptcy or winner-counterfactual claim."),
    "public-G12-C002": ("g12_semantic_context_checks.json", "Complete061original both attempts now read after Astra nomination. Without Illinois you STILL cannot build Tennessee does not assert Illinois is orange or a necessary group member; giving up a red blocker can leave the lone-orange constraint unchanged. Wrong-color dependency remains unestablished, corroborating my initial qualified judgment. Provider's offer-direction phrase is separate."),
    "public-G12-C019": ("g12_semantic_context_checks.json", "Complete239original now read after Astra nomination. Applied private explicitly gives43cash and2/2/3, and returned provider expressly recognizes both house sales and100payment. Public stay-as-they-are is a forward hold. Stale-state label contradicted, corroborating my initial judgment. Separate impossible roll1geometry remains a different proposition."),
    "public-G18-C018": ("g18_sample_and_offer_checks.json", "Complete431/441/442 originals now read.431standing250assurance appears in BOTH441seller and442buyer actual memories.441explicitly invokes it;442publicly withdraws and provider cites rival49cash. Another750payment and major orange liquidation intervene after431. Exposure, invocation and withdrawal supported; costly reliance and knowing falsity at initial assurance not identified. Competitive deception allowed, no immutable-offer norm inferred."),
    "b-g13-final-05": ("g13_sample_channel_checks.json", "Complete160and171commonbundlesand272nonsampleconfirmvalidreceivedENDsversuscontentbuild/mortgage.160legalcontentbuildleaves57from357;272legalVentnormortgagereaches309from179. Appliedprivatesclaimunexecutedresults.171providerexplicitlycorrectszerohousesagainstpriorphantomhistory. Noenginefallback, uniqueintentorupstreamcause; mortgage-on-demandmeans272ENDdoesnotestablishfatalomission."),
    "public-G11-C004": ("g11_public_claim_checks.json", "CORRECTIONTOMYINITIAL4TOTAL: BW1preexists104.104buysPP1and122buysPP1plusBW2:4NEWpurchases800but5TOTALhouses(PP2/BW3). Source3totalwrongandmyinitial4totalalsowrong. Onlynewpurchasescountedforoutlay."),
    "public-G11-C006": ("g11_public_claim_checks.json", "Original148transfersStJamestoOpus,KY/ILLtoArgon;149holdingsincludeALLTHREEorangesandactual200buildbuysONEhouseeachNY/TN. Bothcolorscompleted,notArgononly. Argon154cash274plus520mortgages=794,159fivehouses750to44;163addsKYsecond150to94."),
    "public-G11-C007": ("g11_public_claim_checks.json", "Original138OpusbuysBALTIC60,notNY;145actualNYflowsSoltoOpusfor275plusBalticOriental.149actualOpusbuildTWOtotalhousesNY1/TN1,not2eachthreeoranges.151Sol8brownshouses400from1304to904."),
    "public-G11-C009": ("g11_public_claim_checks.json", "176actual120cashand25interesttransfers3encumbereddeeds;160to280sellerand869to724buyer. Sellerprivateexplicitreserve/expectedliquidationrationale; notprooftruthofeveryrentarithmetic."),
    "public-G11-C010": ("g11_public_claim_checks.json", "225originalhouse-onlyfull1064=349+375salvage+340unlockedmortgages,exact36shortof1100. Estate349not1100paidrent."),
    "public-G11-C011": ("g11_public_claim_checks.json", "203sellstwoactualhousesTN1NY1for100;228fullbound306with0furtherliquidation. Estate306,not1700paidrent. Noenginebonusroll187jail3plus3after188END."),
    "public-G11-C014": ("g11_public_claim_checks.json", "215schemaoffers200plusunmortgagedMarvin140andNC150collateral=290,so300publicclaimoverstates10,not20. SourcewronglychecksRECEIVEDalreadyencumberedoranges280instead.216rejectcontainsunexecutedplan; nointentdiagnosis."),
    "public-G11-C015": ("g11_public_claim_checks.json", "255publicandprivatestatefalsepinkcompletion;256recipientexplicitlycorrectsownsStatesbutnotStCharles;257acknowledgespriorerrorandaddsStCharles;258rejectsbothcompletedpinksbecausegivinggreencompletionstillunfavorable. Applied-channeloriginalsverified; completeproviderbundlesnotyetread, noknowinglyfalseintentclaim."),
    "public-G11-C018": ("g11_redemption_count_check.json", "Original181/182charges83/111verified. Exact1182prefixeventsandactualredemptions:activeElectricdice10rent100BEFOREandAFTERWWredemption;Reading50BEFOREandAFTERPRR. Appliedprivates'raisingElectric/doublingReadingclaimswrong,thoughownredeemedlandingactivationreal. Noalternatepaidrentoroptimalityclaim."),
    "public-G11-C019": ("g11_public_claim_checks.json", "267appliedprivateexplicitlyrecordsJoketradetheywillreject;268recipientkeepscardandcitesoptionvalue. Thisisrecordedrationaleratherthanidentifiedhiddenintent. Fullattemptbundlesremainpendingbeforemalformed-retry/socialclaim."),
    "public-G11-C022": ("g11_public_claim_checks.json", "325originalSolprivateCORRECTnominal753=293+250hotelsalvage+60unlockedbrownmortgages+150utilities;source693omits60. Stillbelow1100evenupperbound. Noaccessrouteorfullliquidationreplayclaimed;estate293not1100paidrent."),
    "public-G10-C002": ("g10_public_claim_checks.json", "Original20Grok980atfirstoffer;39cash404afterNY450andlatertax100;40accept250leaves154;43resale260leaves414. SamechainalsoGIVESIllinois, so10cashnetisnotwholeprofit.21cash-onlyrefusalfollowedpropertyplus250acceptdoesNOTviolateproperty-tradecondition.39appliedprivateexplicitlyDon'tsendit.Endturnbuttoolproposes;notchannelconsistentintent."),
    "public-G10-C003": ("g10_public_claim_checks.json", "49offerStatesplusB_O_RAILROAD,notBoardwalk;50recipientprivateknowinglyrefusesbecausepinknotcompleteandfundedredmonopolygivenaway. Property-for-propertynecessaryconditionmetbutstrongercompletionconditionunmet."),
    "public-G10-C004": ("g10_public_claim_checks.json", "Original77550sale324to874verified,tradeexchange_index4(fourcounters),notfivecounters. Solprivateexplicitlyliquidityforfuturepropertiesandred/pinktradesratherthanholdinggreenblocker; don'tinferinducedbelief."),
    "public-G10-C005": ("g10_public_claim_checks.json", "Original92privateexplicitlyretainsTN/NYwhilegivingOrientalfor300cash. 'Orangesstaywithme'correctlyreferstootherretainedholdings,notmiscoloringOriental.305to605cashanddeed6transfer657verified."),
    "public-G10-C006": ("g10_public_claim_checks.json", "Original59480offerrequestsexactlyTN180plusNY200; stated120premiumis20toohigh(100actual). Nomisleadingintentorrelianceinferred."),
    "public-G10-C007": ("g10_public_claim_checks.json", "Original104250plusBNOStatesforVTflows718–722;106nineinterleavedhouses450from514to64afterKentuckymortgage110. Noomittedcashfeeintheseunmortgagedflows."),
    "public-G10-C012": ("g10_public_claim_checks.json", "110BWsecondhouse200from537to337PRECEDES600paidrent799;125/126/127subsequentthreehouses600from937to337. Rentfinancingandoriginalpositiontargetsareexplicitinprivates; notall800investmentafterreceipt."),
    "public-G10-C014": ("g10_public_claim_checks.json", "Original181recipientSolpositionPACIFIC_AVENUEwhileOpusownsdeed; statement'sittingonPacific'accuratelocation,notfalseownership.183bid233>232cash;184minimum234unaffordableanddropverified. Thisisextractorreferenterror,notplayermisinformation."),
    "public-G10-C015": ("g10_public_claim_checks.json", "Original188SolprivateCORRECT692fullbound=232+12houses*25+160unlockedLBmortgages. Source600salvageincorrectusespurchasecost50.193Opusfull648=28+620;198Grokfull509<600. Estatecash232/28/509not1400/1400/600paidrents."),
    "public-G09-C003": ("g09_public_claim_checks.json", "Original79actual111redemptionand85/86utilitymortgage/rentverified; 80tradeplus10interestplus111redemptionis201activationcost, distinctfrom80cashprice. Fee110quoteversus111enginechargeisimplementationdiscrepancy, notidentifiedspeakerlie."),
    "public-G09-C005": ("g09_public_claim_checks.json", "Original86RENT_PAID608utility100withElectricmortgagedafter596; same-ownercountcontinueswhilelandingactivationdiffers. PennRRredemption111at560/561."),
    "public-G09-C009": ("g09_public_claim_checks.json", "Original159acceptedexchange_index11and325cashtransfer;160actuallybuildsTWO100housesonVirginiaandStCharles,notoneeachthreepinks.228minus200=28. Source13countersconflates13decisions(initial+11counter+accept)."),
    "public-G09-C010": ("g09_public_claim_checks.json", "194appliedprivatealreadycorrectfull1171boundwhiletoolmortgages;197final90mortgageautomaticeliminationtransfers1171estatecashat1365/1366,not1400rent.791wasBEFOREfourmortgages,notafter. Providerd194fullbundlenotreadhere; nointentclaimfrommismatch."),
    "public-G09-C011": ("g09_public_claim_checks.json", "Allthreehouse-onlyfullbounds913/1171/824against1100/1400/1400. Opus220salvage200meansfourtotalpinkhouses,notonlytwototal. Estatecash383/1171/54recorded; nofullrentdebtscountedasreceipts."),
    "public-G09-C012": ("g09_public_claim_checks.json", "209actual900orangebuild923to23verified.220final1400debttransfersonly54estatecash,not1400RENT_PAID. Allfourfinancingdeedsnonorange."),
    "public-G09-C013": ("g09_public_claim_checks.json", "Original191privateexplicitlymortgagesisolatedTennessee90to498fornext450LBbuild;192actuallybuildsnineLBhouses450. Financinglightbluedevelopmentisaccuratepurpose,notslipofthefinanceddeed'scolor.195mortgagecalledsellingislexicaldifferencewithrecordedmortgagemotive."),
    "public-G09-C014": ("g09_public_claim_checks.json", "Original189/202/203/204charges66/100/100/111verified. AllfitSAMEfunctionceil(principal*1.1);float90*1.1=99.00000000000001and100*1.1=110.00000000000001. Sourceclaimnotsinglefunctionfalse."),
    "public-G08-C005": ("g08_public_claim_checks.json", "Originaloffers75/77/90/106/113/147areSIXMarvinoffers, notfive. Myinitialsource-IDconcernincluding167isnarrowed:167actuallyoffersVentnorforNorthCarolina, notMarvin. Originalcashat158seller444before300receipt744after, separatefromthisofferchain."),
    "public-G08-C006": ("g08_public_claim_checks.json", "Completed163originalbundle: receivedcontentJSONbuilds1/1/1andproviderstates300buildplan, whereasrawtoolENDandappliedpublic/privateclaimalreadybuilt/cash172againstactual472and0houses. Nonidenticalargumentschannelconflict; notidentifieddeliberatepubliclie.164appliednoterepeatssamestatusbutitsfullbundleunread. ActualTNrent28at1166confirmsbaremonopoly."),
    "public-G08-C007": ("g08_public_claim_checks.json", "Sourceconflatesallownedwithsingle-ownercomplete. Virginiaacquisition154meansallpinkdeedsownedacrossplayersbefore158. Strictmonopoly-for-monopolypolicyrevisedbut156/158privateexplicitlyplansfollowupStatesVirginiaforParkPlace; notunexplainedviolationofall-ownedcondition.300sellerreceipt444to744events1120/1121."),
    "public-G08-C008": ("g08_public_claim_checks.json", "Original171propertyflows1202–1204completebothsets;172interleavedninehouses900leaves299. Recipient171notes744plus290collateral=1034couldfinance5houses, butownfuturemanagementaccessseparate."),
    "public-G08-C009": ("g08_public_claim_checks.json", "Original194/196retentionthen209/211saleverified; Atlanticconditionchangedwithcash128to100andlowerbuyercash1272to911.400plus14interestleavesbuyer497, seller500. Sourceendpoint56redemptionisVermontanalogue, notMarvin140principal."),
    "public-G08-C010": ("g08_public_claim_checks.json", "575publicsufficiencyclaimNOTrefuted: original209cash100plus575=675covers3additional600houses. Itsprivatestronger3eachclaimneedsquantitycontext.249developedBrownsisPROSPECTIVE:privatesaysgivingmonopolywouldallowdevelopmentbeforeitcrossesGO. Thusnotfalsecurrentbrownstatus.400vs140ratioabout2.86ratherthan4remainsnumericmismatch; intent/uptakeunidentified."),
    "public-G08-C012": ("g08_public_claim_checks.json", "184build400from508to108;220sale100raises640to740then700rentleaves40;257sale100and259completesmortgage-funded625paymentleaves13. Payingunchangedrentdoesnotprovebuildhadnoeffectonneedtoliquidate."),
    "public-G08-C013": ("g08_public_claim_checks.json", "OriginalRENT_PAID1587/1859/1911are700+625ArgontoSoland700OpustoSol:2025acrossthreepaymentsbutonlyTWOdistinctpayers. Estatepaymentsnotaddedtorent."),
    "public-G08-C015": ("g08_public_claim_checks.json", "Original249privateexplicitlyprospectivedevelopedBrowns, notfalsecurrentclaim.262sale120plus3interestverified; seller13to133, privaterecords308liquiditywithPark175mortgageandmentions30earlierraised. Noidentifiedfalsityorintent."),
    "public-G08-C016": ("g08_public_claim_checks.json", "Original203seller104not204before200sale, resulting304. Buyer200cashand5interestat1449/1452. Sourcecashpathcorrected."),
    "public-G08-C017": ("g08_public_claim_checks.json", "House-onlyfullbounds271=133+175=308<700;280=86+300salvage+280orange-mortgages-unlocked=666<1100;287=9+300=309<750. Source386Grokunderboundomitsunlockedmortgages. Terminal133/86/9estatecashand3/6/8titles; nofullrentpayments. Theseupperboundsaloneproveinsolvencywithoutclaimingallsequencesreplayed."),
    "public-G08-C018": ("g08_public_claim_checks.json", "274actual221BWredemption3097to2876;275sixhouses1200to1676;280GrokPPdebt1100results86estate. SolalreadyownsPPanddoesnotreceiveitfromGrok. Sourcepayerwordingincorrectforunpaiddebt."),
    "public-G04-C006": ("g04_uptake_boundary_check.json", "Peer-nominateduptakeboundaryoriginalchecked: completerecipient150/152bundles, prior148applied/providerand149/151chronology.150publicFairpointfollowsfalse200yellowcostwhileitsproviderexplicitlycorrects150not200andprior148privatealreadyuses150. PRIOR148alsoplansfallbacktakeYellowwithcash/equityifp1insistsonOrange. Thusdirectionswitchhaspreexistingrecordedcontingency. Uptakeof200notshown; otherinfluenceunidentified. Acceptance523+50-13=560, not573privatenote."),
    "public-G06-C001": ("g06_negative_case_check.json", "Completeoriginald019/d020channelsread. Grokfalseorangepremiseinpublic/private/provider; receivedcontent/providerfavorEND, actualtoolproposes400plusStCharlesPennRRforVermont. Recipientactuallyseespitchandappliedprivatenoteexplicitlysaysopponentorangeclaimincorrectwhileaccepting. Events160/161transfer400and162–164deeds. d021appliednotecorrectsproposerownpremise. Encryptedunavailable; noknownintentorfalsity-reliance."),
    "public-G06-C021": ("g06_unmortgage_menu_check.json", "Exact1693eventprefixmatches. NCA32/BW39bothlistedeligiblepostturnunmortgageindices; un-mortgageablemeanscanunmortgage, notnonredeemable. Independentlocalbrancheseachlegal: NCA165, BW221enginecharge. Sourceinventedspecialbankruptcy-deedrestrictionrejected; nochangetocanonicalgame."),
    "public-G03-C017": ("additional_economics_checks.json", "Original railroad redemption events4272/4278/4284 are exactly three, spaces5/25/35. Pennsylvania RR absent from redemption set. Four-railroad source count rejected."),
    "public-G03-C021": ("additional_economics_checks.json", "All original Argon HOUSE_BUILT/HOTEL_BUILT events exclude green31/32/34. Source green-construction breadth rejected; red, brown, lightblue, darkblue and yellow remain."),
    "public-G04-C005": ("additional_economics_checks.json", "Originald134 sellsVirginiaOpus-to-Sol for300plusPennsylvania, completingSolpinks. Opusredcompletion occursseparately atd165Kentucky600pluscard with11interest. Originald130/d134Solnotes wronglyestimate ninepinkhouses450; enginecost900. No claimthatthismisestimatecausedlaterdefaults."),
    "public-G04-C015": ("additional_economics_checks.json", "Promptbankhousecounts exactly0atd189/d208/d215/d228. No claimstockalonebindseachforegonebuild."),
    "public-G04-C019": ("additional_economics_checks.json", "Originald279terminaldebt750; actorcash86andremainingMED/MARmortgages170cannotcover. Estatecash86events2058/2059, not750rent."),
    "public-G04-C021": ("additional_economics_checks.json", "Originald348terminal625debt yields210estatecash at2556/2557. No625RENT_PAID insegment."),
    "public-G05-C001": ("g05_public_claim_checks.json", "Originald034/035sameglobalturn23. GrokgivesnewNCAand400toOpus, receivesIndiana/Marvin atd036events280–284. PublicliquiditypitchaddressesOpus, notcashcreationforGrok."),
    "public-G05-C002": ("g05_public_claim_checks.json", "Originalsettlementsd060events463–465sellMarvin350toSol; d064events486–488returnMarvin800toGrok. Solnetcash450. No interveningplayerrolls: no demonstratedrentforegonewithinsameglobal37."),
    "public-G05-C003": ("g05_public_claim_checks.json", "Originalappliedd060accept_trade includes bothpublicMarvinnotforsale andprivateRejecttheirMarvingrab. Settlementstill350Marvinsale. Fullproviderresponsecause notauditedhere."),
    "public-G05-C004": ("g05_public_claim_checks.json", "Fable-nominated correction independentlychecked inoriginals: d106offer475plusutility; Grokcurrent266 -> prospective741. Grokd107privatenoteexplicitlyweighs741cashwithnosetandrejects. No supportedcurrentcashfalsity."),
    "public-G05-C007": ("g05_public_claim_checks.json", "Originald092quoteaddresses p2: two greens next to YOUR Boardwalk. p2SolactuallyownsBoardwalk. Speaker's lackofBoardwalkdoesnotmake recipientreferencefalse."),
    "public-G05-C014": ("g05_public_claim_checks.json", "Fable-nominated d159pay_jail_fine confirmed:408minus50fine then12Virginiarent=346. Sol d155starts1136, pays50plus14StJamesrent=1072, not1120minus50. Rawattemptcause notauditedhere."),
    "public-G05-C018": ("g05_public_claim_checks.json", "Opusalreadybids60atd195beforeArgonwarning; d199bids80andwinsafterSol166cashwithdraws. Priorparticipationundercutswarninginitiatedbidding, butdoesnotexcludeincremental influence."),
    "public-G05-C020": ("g05_public_claim_checks.json", "Originals: Argon204, Sol62, Grok306. Grokalreadypassedatd220beforeOpus205bid221; Argon223cannotmeet206min. Ceilingexplanationappliestoremainingactivecounterparties, notallplayersincludingdroppedGrok."),
    "public-G05-C022": ("g05_public_claim_checks.json", "CORRECTION TO MY INITIAL726BOUND: Marvinismortgaged, cannotraiseanother140. Actualcash306plusonlyStates70/NY100/Indiana110=586, stillbelow900. Sourceclaimallfourmortgageableisalsofalse. Fourtitlespassestate, actual306cash."),
    "public-G05-C025": ("g05_public_claim_checks.json", "Exactbalances:987atd274 ->910afterStCharles77 ->822afterVirginiad27588. Source910to822isvalidforsecondredemptiononly; do notsubtractfirst77again. Owninitialskepticismnarrowedtothe ambiguouswindow, notcasherror."),
    "public-G05-C026": ("g05_public_claim_checks.json", "OriginalSol17titlesafterArgonestate, not12. d272Argonsevenencumberedtitleswith149cash. Combinedfirst900rentfinancing1049successfullyleaves149, contradicting source sentence thatitdidnotcover900."),
    "public-G05-C029": ("g05_public_claim_checks.json", "Originald309holdings11titles, not14. House-onlyfullbound84+515clear-deedmortgages+200houses=799, including160LBmortgagesunlockableafterhousesales. Thisrevises639but remainsbelow1100; actualestate84and11titlesevents2368–2381."),
}


UPDATES.update({
    "public-G02-C003": ("g02_channel_case_checks.json", "Complete062originalavailablebundle: content, returned provider explanation and applied private all explicitly recognize Ventnor trade went through. Public corrects arithmetic without denying execution.063 makes mismatch public, not first documented recognition. Source's062writesasifrefused allegation rejected; initial qualified label retained.061 adjacent applied acceptance/refusal messages checked, not a new complete061bundle claim."),
    "public-G02-C014": ("g02_channel_case_checks.json", "Complete247originalavailablebundle: valid received empty proposal creates recipient248decision and rejection; applied private explicitly ProbeOnly. But content selectsEND and returned explanation endswithEND. Thus applied-channel probing rationale exists without channel-consistent intent; no provider/harness cause, hidden motive or causal conversation benefit inferred. Initial qualified label retained."),
    "public-G17-C016": ("elimination_upper_bounds.json", "Original398fullupper476=366cash+50Vermont+60Connecticut. Source526usesVT100listascollateral;stillbelow750. Currentdebtself-financeimpossibleonupper;actualestate366separate."),
    "public-G17-C009": ("elimination_upper_bounds.json", "Ownexact1538-event prefixfiveDBhousesales500thenBaltic30/Park175mortgagespay550retain155andclearBW. Full905notpublic/appliedprivate530. Financing-feasibleobservedbankruptcy;noalternatewinnerorrationalityclaim."),
    "public-G17-C010": ("elimination_upper_bounds.json", "Full60eliminationeventscreenincludes234full905andlocalpaymentroute;itsbankruptcycannotbecalledunavoidablefrom530. Houseownershiptransferrequiresdeedownershipevent,notnewconstructionevent. Otherbankruptciesremainseparatelybounded."),
    "public-G16-C019": ("g16_liquidity_and_development_checks.json", "CanonicalownDBconstructionevents2132/2137/2845threehouses600;salesevents2397/2398/2954threehouses300;zeroRENT_PAIDtoOpuswhileownDBdeveloped.274providerprefersonehouse,but275explicitlyacknowledges19riskandchoosesnextwithsale/mortgagebackup. Changedreservechoicenotidentifiedforgetting;notcompleteoriginalbundle-readingclaim."),
    "public-G16-C022": ("g16_liquidity_and_development_checks.json", "Exact4831-event prefix d602:23legalone-levelsales/mortgagesreach1393estatecashatautomaticbankruptcyagainst2000. Originalappliedprivatealreadycomputes288+375+730=1393correctly. Inheritedhotelbuildingstaysondeeds;noextraHOTEL_BUILTneeded."),
    "public-G16-C026": ("g16_liquidity_and_development_checks.json", "Correctfullandreachable1393=288cash+375hotel/houselevelsalvage+730clear-deedmortgagesincluding160LBunlocked. Source1233omits160;its858is288+570subtotal,notmortgagesalone. Original602appliedprivatealready1393correct. Exact23-actionroute/4831prefixverified;noalternatewinner."),
    "public-G15-C001": ("g15_public_economics_checks.json", "Original057cash158andnoavailablebuild;onlytwoDBdeedsremainafterElectrictransfer. Acceptanceof750doesnotcontradictearliercannotbuildat750;itcorroboratescashconstraint. Ceiling700wasobservablyrevised;intentunidentified."),
    "public-G15-C004": ("g15_public_economics_checks.json", "REVISION TO MY INITIAL SKEPTICISM: publiccolorpairaloneambiguous,but073APPLIEDPRIVATEexplicitlyclaimsfalseyellowcompletion(Marvin+Ventnor+Penn)whilegivingMarvinaway.076privatecorrectlyNoMonopoly/namesMarvinopponent/Pennlonegreen;laterbad-swapphraseisgeneralholdlanguage,notidentifiedadmission. Originalinitialcontradictedlabelretained;underlyingchannel-specificerrornowqualifiedsupported."),
    "public-G15-C005": ("g15_public_economics_checks.json", "Original089PP1/BW2;BWsale100financestwo50payments;090PPsale100financesthird50payment.091cash78PP0/BW1. Threepayments,not title'stwo;sourcePP1endpointwrong. Peer-informedtargetindependentlychecked."),
    "public-G15-C007": ("g15_public_economics_checks.json", "Original122privateexplicitlyp4payingfor2/3yellowwhileIkeepVentnorasthegatekeeper. PublicmissingVentnorreferstowinningbuyer'sset,notforgottenownVentnor. Initialunresolvednowresolvedagainstextractorfalsity;noall-channelbeliefclaim."),
    "public-G15-C008": ("g15_public_economics_checks.json", "Original105OpussellsBalticfor180;106Grokhas903cashandMed,butappliedpublicsaysholdBalticandseller'sprivateCashstays8. Receivedchannelsadoptsellerroleandwrongcash;current120referencealsooff. Upstreamcause/intentnotidentified;fullproviderbundleunread."),
    "public-G15-C009": ("g15_public_economics_checks.json", "Originalmortgagecash75/70/70totals215,not235.100buildNY/TNthirdonly;101oranges2/3/3and34cash.148addsStJames3rd;sourceimmediatethreeeachwrong."),
    "public-G15-C012": ("g15_public_economics_checks.json", "Originalhouse-onlyfulluppers761Grok203and645Opus221below800/950. Clearcollateral470/375andsalvage50/100included. No hotelaccessassumptionoralternatewinner."),
    "public-G15-C019": ("g15_public_economics_checks.json", "234to237canonicalHOUSE_BUILTcountssum6newhouses,1200spend. OneinheritedBoardwalkhousegives7finalPP3/BW4;fourBUILDdecisionsnotimmediatefourglobaldecisionsafter221."),
    "public-G15-C021": ("g15_public_economics_checks.json", "Original273fee111actual291to180;private110isstandard10percentestimatewhenmenukeysonly,notidentifiedreasoningfailure. Correct100rentwith3ownedrailscountingmortgagedsiblings.276fullupper280below450;withoutredemptioncash291alsobelow450. Expost11equitylossnotcausalbankruptcy."),
    "public-G14-C004": ("g14_public_economics_checks.json", "Applied093offersBalticplus200forMed;094events721/722cashGroktoArgonand723/724deedsleavegroupSPLIT. Proposerappliedprivatefalselysayscompletesmybrownset;recipientprivateexplicitlykeepsgroupsplit. No coherentintentclaimwithoutcompleteprovidercheck. Source title'scashdirectionwrong."),
    "public-G14-C009": ("g14_public_economics_checks.json", "139actualevents985/986ArgonpaysGrok100and987MedGroktoArgoncompletebrown.140actualdeliveredacceptedtimelineincorrectlyp3gives100,p2givesMed. Exposuretoreversedhistoryverified,notreliance. Boundaryafterwholesettlementavoidsintermediatefalsecompletionatprior094."),
    "public-G14-C014": ("g14_public_economics_checks.json", "House-onlyfulluppers346/522/907versus800/800/1100. Argon222APPLIEDPRIVATEalreadycorrectly522including60brownmortgagesunlockedbysales;extractor462underbounds. Actualestatecash246/162/522at1495/1622/1737,notthefullrents."),
    "public-G13-C003": ("g13_public_economics_checks.json", "Original060 full public explicitly proposes buying Park Place; private also names eventual purchase. Quoted current-cash phrase is prospective financing, not a claim that an incomplete set is buildable."),
    "public-G13-C004": ("g13_public_economics_checks.json", "TRADE_ACCEPTED624 explicitly carries one offered card. Recipient085 has0 before,087 has1 and uses it. Compact post omits a separate card-transfer row; canonical event terms preserve the change."),
    "public-G13-C006": ("g13_public_economics_checks.json", "Original172 full clause says unmortgage AND build, not just redemption;174 private recognizes254before18transferinterest. Cash-only236covers193redemption but leaves43below200house; additional collateral exists, so neither the isolated quote nor cash alone characterizes full feasible finance. Initial qualified verdict preserved."),
    "public-G13-C007": ("g13_public_economics_checks.json", "Original167 private/public correctly locate Grok onBNO and seven fromNC. Board contractBNO25,NC32;source'sBNO5and27distancewrong. Pacific31asofferedsecondgreenalsoimmediatelyprecedesNC32."),
    "public-G13-C008": ("g13_public_economics_checks.json", "Exact880-event prefix accept140counter then two legal100orangehouse purchases leavesOpus24, existing84included. Original121 private explicitly84plus116threshold. Falsity label contradicted by complete budget and actual engine legality; nofuturebranch."),
    "public-G13-C011": ("g13_public_economics_checks.json", "Original105 private explicitly says givingp2amonopoly. Publicgiveupamonopoly is consistent with granting recipient completion, not mistakenownbrownownership."),
    "public-G13-C016": ("g13_public_economics_checks.json", "Original213 private correctly computes310mortgagesand412shortfall:228+110KY+200BW=538below950. Extractor438boundwrong;model'sappliednoteisnumericcounterexample."),
    "public-G13-C018": ("g13_public_economics_checks.json", "Actualcash1045BEFOREOriental56redemption,989BEFOREVermont56,933afterboth. Source1045afterOrientalwrong. Bothcharges56consistentwithceil50*1.1float."),
    "public-G13-C019": ("g13_public_economics_checks.json", "Original243 public/private BNOsum11and2/36correct;sourceBNO5wrong. Original250public/privateShortLine8/5of36wrong,actualAtlantic26to35sum9/4of36. Probabilitymistakeisdistinctfromlaterrecordedomissionrationale."),
    "public-G12-C001": ("g12_public_claim_checks.json", "Applied d025/026 transfers StCharles Opus to Grok, Indiana Grok to Opus, and40cash Grok to Opus. Source cash/deed orientation is reversed."),
    "public-G12-C005": ("g12_public_claim_checks.json", "Applied146/148/150private notes recognize686cash and own ability to build; public nothing-to-build pitch conflicts with those figures. Buyer147/149public notes explicitly retain cash awareness. Full buyer provider bundles not yet read here; no identified false-premise uptake or causal price concession."),
    "public-G12-C007": ("g12_public_claim_checks.json", "At195 applied private underbounds410; recipient196 corrects60+350salvage+220unlocked mortgages=630, speaker197 acknowledges. Retrospective bust-bluff wording at197 does not establish knowing falsity at195, whose own note used410."),
    "public-G12-C012": ("g12_public_claim_checks.json", "d157 Tennessee90mortgage takes413to503, d158 three150houses leave53. Source first-layer arithmetic confirmed; smaller builds remain distinct legal alternatives, no optimality inference."),
    "public-G12-C014": ("g12_public_claim_checks.json", "Exact1264-event prefix: three red house sales225 plus Illinois120 and Indiana110 mortgages pay500 legally and retain8. Full house-only bound748, not applied private408. No alternate winner inferred."),
    "public-G12-C015": ("g12_public_claim_checks.json", "Complete d249 available bundle read and1703-event prefix replayed. Content's two-Virginia-house sale is legal, cash43to143,pinks2/2/1. Five legal one-house sales also pay250, retain43,pinks0/1/1. No mortgage needed. Received tool declares while content, returned reasoning and even final applied-private recommendation recognize survival; intermediate errors remain. This directly falsifies a uniform omitted-unlocked-mortgages mechanism across all three financing-feasible eliminations. Astra independently confirms exact content plan; no hidden intent/upstream cause/winner claim."),
    "public-G12-C016": ("g12_public_claim_checks.json", "861minus300=561 is price-only. Mortgaged Pennsylvania carries16 mandatory transfer interest, giving545 before optional176redemption369. Source's560Atlantic-plus-Pacific face cost differs by1 even before the omitted fee; hypothetical offer, not accepted cash flow."),
    "public-G12-C017": ("g12_public_claim_checks.json", "Original recipient196 bound630=60+350houses+220unlockable pink mortgages is correct; speaker197 acknowledges correction. This rejects inevitability of bankruptcy from the pitch, without identifying all framing influence or intent."),
})


UPDATES.update({
    "public-G11-C015": ("g11_social_channel_checks.json", "Complete255-258bundles now read.255falsepinkclaim is repeated in appliedprivate;257explicitly corrects.256recipientprovider initially echoes completion, then explicitly corrects before content/tool/private/publicREJECT. No enduring uptake or action-based reliance identified; recipient calling it lie does not prove knowing intent. Revised257genuinely completes both groups but258rejects rivalgreenexternality. Initial qualified retained."),
    "public-G11-C019": ("g11_social_channel_checks.json", "Complete267-268bundles now read.267firstattempt502generationerror/missingtool, retryCONTENTENDversusreceivedPROPOSEfreecardwithJokeprivate. Delivered268offerandactualrejectverified. EvaluativeFair/taunt andappliedjokeselfreport do not establish uniquelychannelconsistentintent orpromptnormviolation; no actualtransfer. All44578renderedcharsreadin3contiguouschunks."),
})


def main():
    path = HERE / "case_reviews.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    for record in records:
        if record["catalog_id"] not in UPDATES:
            continue
        report, conclusion = UPDATES[record["catalog_id"]]
        update = {"report": report, "conclusion": conclusion,
                  "scope": "Original applied actions, canonical events and delivered state arithmetic; not a claim that every original provider channel was reviewed"}
        updates = record.setdefault("verification_updates", [])
        if update not in updates:
            updates.append(update)
    for record in records:
        if record["catalog_id"] == "public-G09-C008":
            update = {"report": "debate.md", "scope": "Peer-informed actor/phase qualification from Astra, no new original branch by Sol",
                      "conclusion": "228<300cash-only purchase limit remains true. Mortgages are not offered during recipient131TRADE_RESPONSE or immediateBUY_OR_AUCTION, so collateral alone does not prove financing access before the next landing. Prior124management or a later safe management opportunity are distinct times. Initial universal-only-way objection retained without asserting a same-opportunity direct-purchase route.",
                      "peer_informed": True}
            updates = record.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if record["catalog_id"] not in {"public-G12-C005", "public-G12-C008"}:
            continue
        update = {"report": "g12_virginia_channel_checks.json",
                  "scope": "Complete available original bundles146-151 plus exact actual152management financing branch",
                  "conclusion": "Full six bundles now read. Public nothing-to-build conflicts with own3/4-house affordability;150provider explicitly withholds rival-financing threshold and stresses own cash.147/149public retain capacity,151provider explicitly686and100housecost/ownbluefundingmotive, so no identified false-premise uptake or causal140discount.147provider buyer/seller reversal and repeated reversed-history confusion remain. Grok's215threshold blocks BOTHblues3/3, not any third house: actual152prefix3rail mortgages plusBW/PP/BW legally reach2/3with195. No optimality, winner or privileged intent claim."}
        updates = record.setdefault("verification_updates", [])
        if update not in updates:
            updates.append(update)
    path.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records))
    sample_path = HERE / "negative_control_reviews.jsonl"
    samples = [json.loads(line) for line in sample_path.read_text().splitlines()]
    for sample in samples:
        if sample.get("sample_index") in {231, 234, 239}:
            conclusions = {
                231: "Astra correctly challenged nominal-upper-only reasoning. New exact actual prior191Gemini/192Grok management branches, with cash/holdings/building stock equal to200, legally reach1383/566. Thus resources are constructively financeable at those opportunities, not merely nominal. No future synthetic rent, changed control or causal inference about the chosen END.",
                234: "Exact actual257conditional acceptance of250returns p3management, then mortgages595/redemption111/sixhouses600legally retain64and brown hotels. This resolves the initial arithmetic-only qualification, not historical agreement or optimality.",
                239: "Complete325original now read. Correct1414total but675salvage/690mortgagescomponentswrong, true700/665. Provider additionally adds200to413while applied private correctly leaves213. Exact actual327–336pays1400and retains14, closing legal hotel-stock/financing sequence."
            }
            update = {"report": "g20_sample_financing_checks.json", "scope": "Exact historical-prefix branches and complete235/325returned channels; conditional agreements explicit",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {216, 220, 225, 227}:
            conclusions = {
                216: "Exact original nine-house red allocation executes after interleaving and leaves262. Actual234/235/236buy three separate layers on the same global management turn115. This preserves the eventual target, not the within-decision retry allocation.",
                220: "CORRECTION TO MY INITIAL ENDORSEMENT: current pink rents are450/450/500, so502covers ALL pinks. I initially repeated the applied States500/Virginia550 error. Full exact-prefix engine rent check corrects both the model proposition and my initial gloss; no future survival or optimality follows.",
                225: "Exact-prefix engine confirms three active railroads charge100each, not200. Current private and prior delivered redemption notes contain false sibling-rent increases; earlier correct statements remain chronological counterexamples to stable ignorance.",
                227: "Exact engine confirms neighboring237red rents700/700/750, as my initial judgment said. My later commentary proposed a false550/550/600correction, caught by a failed assertion and withdrawn before report generation. Only the pink-rent initial gloss requires correction."
            }
            update = {"report": "g19_sample_rent_checks.json", "scope": "Exact historical prefixes, current engine rents and local interleaved construction",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {207, 210, 211, 212}:
            conclusions = {
                207: "Exact341Park redemption193 followed by Park175andBW200mortgages reaches596. CT600exceeds it, but Vermont550does not. Correct current614spare bound and incorrect both-hotels-fatal implication coexist.341full provider unread.",
                210: "Exact284five-house sale plus unlocked Park175/BW200mortgages reaches876, not cash-plus-salvage501. Virginia700is locally financeable after full liquidation; no future draw, optimal hold or winning alternative inferred.",
                211: "Exact254artificial acceptance of the original ECplus150offer returns proposer management. Pacific150mortgage then one150Atlantic house leaves71. Thus public inability-to-build is cash-only; no historical acceptance or preferable deal.253received proposal conflicts with content mortgage and provider final mortgage plan.",
                212: "Original fixed board and dice table: NC32toPP37is5with4/36, BW39is7with6/36, combined10/36=27.78percent. This corrects applied4/6about22percent AND historical narrative25percent. TN18toNY19requires1, so direct next-dice NYrisk1/36is false; card routes remain distinct."
            }
            update = {"report": "g18_sample_and_offer_checks.json", "scope": "Exact local management and conditional acceptance sequences, fixed board arithmetic; full common channels read",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {197, 201}:
            conclusions = {
                197: "Exact241management route applies the actual Oriental fourth, then sells all houses and mortgages clear collateral to934, not774. Adding a legal Vermont fourth first reaches909, not749. The750threshold implication is false; no observed debt or preferable build inferred.241full provider unread.",
                201: "Exact236current legal house-sale/mortgage sequence reaches759, not599; NC mortgage plus three fourth houses and full legal retrenchment reaches684, not524. Fourth rents400/400/450, not350/350/450. CORRECTION TO MY INITIAL LOCATION GLOSS: canonical snapshot position is36, not7. Delivered CHANCE lacks the index, so its applied7and provider35interpretations are not clean knowledge tests. Initial label retained."
            }
            update = {"report": "g17_sample_bound_checks.json", "scope": "Exact-prefix local management sequences and canonical snapshot, not future dice or an optimality test",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {181, 182, 183, 186, 190}:
            conclusions = {
                181: "The donor-only279 comparison omits the recipient212. No agreed transfer is inferred. The separate actual322offer conditionally accepted permits its seller492cash, Park redemption193 and one Boardwalk house, retaining99 at immediate management access.",
                182: "Exact261prefix: NY redemption111 plus four side mortgages355 permits three total orange houses with185cash, or four with85. Legal sale and unlocked orange mortgages then reach615or565 respectively. Thus even four houses do not mechanically make a550hit fatal; three EACH remains unaffordable and no optimality follows.",
                183: "Exact429conditional acceptance pays20plus8transferinterest, leaves77, keeps EC mortgaged, and raises active WW rent28to70on7. Cannot redeem EC83 remains true. Its private claim WW stays4x until redemption is false, not evidence accepting preferable.",
                186: "Exact173spare mortgages sum425, so cash167plus425equals592, not602. One legal Med hotel downgrade adds25to617with existing bank stock. A600payment would require more than the stated spare-only financing, but full insolvency is not supported.",
                190: "Exact322conditional acceptance of the actual350rail offer gives seller492. Immediate returned p2 management legally redeems Park193 and buys one Boardwalk house200, leaving99. Buyer transfer fees do not reduce seller cash. This is reachable development, not agreement or a hypothetical winner."
            }
            update = {"report": "g16_sample_financing_checks.json",
                      "scope": "Exact historical prefixes and local legal sequences after full common readings;429full provider unread",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {156, 160, 161, 164}:
            conclusions = {
                156: "Own qualification: adjacent206 identifies300ofRR-plus-house equity, not a maximum. Another60browncollateral is unlocked by sales, but the partial component statement alone is not a clean false proposition. Barely exceeds mortgage value is also evaluative language, not an exact numeric assertion.",
                160: "Exact145prefix original8house allocation interleaved legally ends619/4each/bank14. Actual retry applies2houses to919; four actual145-148management decisions on globalturn61 reach originaltarget619/4each/bank14. Thus per-decision quantity change and eventual same-turn target preservation coexist. No global continuation equivalence claimed.",
                161: "Exact162redemption leaves already-activeAtlantic44andMarvin48rents unchanged. Only Ventnor landing activates; same-note ALLrentactivation proposition overstated. Full162providerbundle remains unread; actual note/menu/events and local engine calculation checked.",
                164: "Actual161transfer charges240cashplus13mandatorymortgageinterest,162redemption143; total396,not383. Exact reported active-sibling rents remain44/48before/after redemption. Full161/162providerbundles unread, applied actions/events inspected."
            }
            update = {"report": "g14_sample_boundary_checks.json", "scope": "Exact original prefixes, actual management quantities, fees and rent calculations",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {147, 153, 154}:
            conclusions = {
                147: "Complete272nonsamplebundle now read:contentmortgagesVentnor,receivedEND/appliedprivateclaims309/allmortgagedagainstactual179andclearVentnor. Exactlegalmortgagereaches309. No fallback, no fatalomission because debt-time mortgage remains possible.",
                153: "Exact conditionalaccept500plusPacific at172then193redemption/75Electricand110KYmortgages/one200Boardwalkhouseleaves28.18transferinterestincluded. Conditional150acceptat171plusredemption/Electricmortgage/twohousesends68. Zero-houseclaimignoresreachablefinance; exact11reservecalcignoresinterest. Neither conditionalacceptance is historicalagreement.",
                154: "Exact160historicalprefix and originalcontent2-houseplan legally build Ventnor/Marvinfor300andretain57. ActualreceivedENDappliesneitherbuildnorcost; privateclaimscompletedhouses.18310characterreturnedreasoning fullyreadafterrepair.171latercorrectsphantomhistorywithoutestablishinguniformhiddenbelief."
            }
            update = {"report": "g13_sample_channel_checks.json", "scope": "Complete nominated channels and exact local legal branches, conditional agreements explicitly artificial",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {134, 136, 137, 143}:
            conclusions = {
                134: "Exact073rival management prefix: Penn100andKentucky110mortgages plus200Boardwalkhouse legally leave55from45.072fullbundle read,073completeproviderbundle unread. Forecast soon remains semantic/behavioral qualification rather than literal financing limit.",
                136: "Exact242prefix Baltic30mortgage takes25to55, oneOriental50house leaves5. Current empty cash menu is not whole-turn financing impossibility; voluntary reserve preference remains separate.",
                137: "Exact312prefix entry hotel unavailable, but legal CTsale/KYbuild/Readingmortgage/Statessale/Indianabuild/Pennmortgage/Illinoishotel reaches26cash/bank4. This is local reallocation, no future rent/winner benefit. Current-menu restriction true, permanent impossible inference false.",
                143: "Exact291prefix confirms31physicalhouses allp2, bank1. Public27is wrong and no intervening build before292.292payment450and700mortgagecapacity remain correct.291fullproviderbundleunread, no intent identified."
            }
            update = {"report": "g12_sample_sequence_checks.json", "scope": "Exact-prefix local financing and reallocation, fixed-board/current-state checks",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {120, 123, 124}:
            conclusions = {
                120: "Complete nonsample121bundle now read. Exact-prefix StJames-for-KY/Illinois proposal and artificial conditional acceptance legally complete p1reds with534cash. Literal no bilateral completion is false; recipient willingness, mutually beneficial exchange and optimality remain unidentified. This is not historical settlement.",
                123: "Exact fresh219prefixes PAY and ROLL both draw historical5+2, pay50 and receiveHoliday100, reaching equal actor/board state at830 in nextPOST_TURN. The mismatch therefore does not cost50 on this realized draw. Engine jail-exit doubles use rolled_doublefalse and grant no bonus turn; source rule claim closed, provider/transport cause unclosed.",
                124: "Exact066prefix legal200Parkhouse leaves63; END uses same next4+5passGO200, then legalVermont100purchase leaves163. Immediate chosen reserve rationale cannot imply inability to buy the actual next deed after one house. No changed later trajectory/optimality/winner result."
            }
            update = {"report": "g11_sample_boundary_checks.json", "scope": "Complete nominated original bundles and exact-prefix conditional local action sequences",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") == 110:
            update = {"report": "contracts/data/board.json", "scope": "Own correction of the initial adjacent-case numerical gloss",
                      "conclusion": "Actual four-house Vermont rent is400 and Connecticut450, not VT450/CT500. Adjacent132's489 cash would cover either single current four-house rent; its claimed death therefore remains unsupported and is even less close than my initial gloss. Initial judgment retained."}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") in {72, 76, 82, 83}:
            conclusions = {
                72: "Board16three-house rent550, not applied note500. Exact source retained in g07_sample_finance_check.json; level3/3/3andstock5 remain correct.",
                76: "Exact1270prefixat183: two legal railroad100mortgages plus9interleaved100pinkhouses leave19.719cash-onlylimittrue; fullreachable-financeimpossibilityfalse.183completeproviderbundleunread, actualenginefallback distinct.",
                82: "Originalturn30settlementd062events435/436p3pays300top1and437/438SLp1top3/WWp3top1. Actual077deliveredacceptedrowreversesbothdirections. Exposureverified, no reliance or causalholdidentified.",
                83: "Resolved initial board-price query: contractParkPlace37[2]is500, so recorded ParkPlace2rent500 is correct. No rent-error claim retained."
            }
            update = {"report": "g07_sample_finance_check.json" if sample["sample_index"] != 83 else "contracts/data/board.json",
                      "scope": "Exact source-linked local feasibility and fixed board table checks, not latent belief or future outcome",
                      "conclusion": conclusions[sample["sample_index"]]}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") == 61:
            update = {"report": "g06_reserve_bound_check.json", "scope": "Sample190 complete bundle plus adjacent191 applied rationale and exact local financing diagnostic",
                      "conclusion": "Currentbank8notzero;historicalone-houseentriespredatesevenpinkhousesales. Exact1471-event prefix at191ArgonlegalPacific150mortgageplusKentucky150housechangesfullnominalupper800to725,confirming75salvagelossagainstexisting750/800rentthresholds. Noalternateactualdebt/dice/winneroroptimalityclaim;191fullproviderbundleunread."}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") == 34:
            update = {"report": "g03_reachable_build_check.json", "scope": "Actual364management-prefixfinancing/builddiagnosticandfull363/364available-channelread",
                      "conclusion": "2474prefixeventsmatch. OneexistingbankhouseandKY110/Atlantic130mortgagesallowPPfourth200:43to283to83. Additionalstockreleaseunnecessary.363privateexplicitlyknowsonehouse+financingwhilepublicframesstocknecessity;recipient364seesmessagebuthadprior362retentionrationale. Noidentifieduptake/explicitdeceptive-intentrationale. Cash58becomes43after15tax,holdingssame. CHANCEpositionisambiguousindeliveredpayload;canonical22/provider36notcleanknowledgetest."}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") == 32:
            update = {"report": "g03_opus_restraint_check.json", "scope": "Exact-prefix one-house legality diagnostic",
                      "conclusion": "1252canonicalprefixeventsmatch;Atlantic150houselegalat204cashandbank8,leaves54. HistoricalresponseisrefusedthenvalidchosenENDwithfallback_usedfalse. Availablecontent/providerexplainpreservingcash; noappliedprivate. Nooptimalityorwinnercounterfactual."}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") == 25:
            update = {"report": "g03_hotel_liquidity_check.json", "scope": "Exact management-prefix local engine sequence, no alternate roll or debt",
                      "conclusion": "3200canonicalprefixeventsmatchat451. Targetassets/cash/bankunchangedfrom449forecast.94plus8redhousesales600plusoneKYmortgage110legallyreaches804, exceedinghypothetical700threshold. Earlieronly600liquidityforecastomitsunlockedmortgages. Doesnotasserta700debtactuallyoccurrednoroptimalityofunnecessaryliquidation."}
            updates = sample.setdefault("verification_updates", [])
            if update not in updates:
                updates.append(update)
        if sample.get("sample_index") != 17:
            continue
        update = {"report": "g02_recovery_quantity_check.json", "scope": "Exact-prefix local engine legality and actual purchase quantities",
                  "conclusion": "Originalseven-houseplan2/2/3legalandaffordableafterinterleaving, cash208; actualcorrectiveretrybuilds3thenfollowing244adds3, cash358/2each.1700canonicalprefixeventsmatch. Initialunreplayedlimitclosedforlocallegalityonly; nofuturerent/winnerclaim."}
        updates = sample.setdefault("verification_updates", [])
        if update not in updates:
            updates.append(update)
    sample_path.write_text("".join(json.dumps(sample, ensure_ascii=False) + "\n" for sample in samples))
    print("Preserved initial verdicts; appended authored original-audit updates")


if __name__ == "__main__":
    main()
