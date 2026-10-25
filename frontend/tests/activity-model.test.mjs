import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildActivity, orderEvents, filterActivity, waitingDecisionId, providerReasoning, describeDecision, returnedModel } from '../src/pages/cloud/game/activityModel.ts'
import { isDecisionResolved } from '../src/domain/decisionOutcome.ts'

test('inspector and timeline require canonical resolution before labelling a default action applied',()=>{
  for (const phase of [undefined,null,'decision_started','request_failed']) {
    assert.equal(isDecisionResolved({phase,fallback_used:true}),false)
  }
  assert.equal(isDecisionResolved(null),false)
  assert.equal(isDecisionResolved({phase:'decision_resolved'}),true)
})

const names = { player: id => ({p1:'Claude',p2:'GPT',p3:'Gemini',p4:'Grok'}[id] ?? id), space: i => i === 11 ? 'St. Charles Place' : `Space ${i}`, spaceKey: key => key, card: id => id }
const event = (seq, type, payload = {}, turn = 0, player = 'p1') => ({schema_version:'v1',run_id:'run-a',event_id:`e${seq}`,seq,turn_index:turn,ts_ms:1000-seq,actor:{kind:player?'PLAYER':'ENGINE',player_id:player},type,payload})
const items = events => buildActivity(events,names,'run-a').flatMap(t=>t.items)
const ids = events => items(events).flatMap(i=>i.eventIds)

test('timeline follows canonical sequence, excludes foreign runs and deduplicates deliveries without mutating input',()=>{
  const a=event(1,'GAME_STARTED'), b=event(2,'DICE_ROLLED',{d1:2,d2:3,is_double:false})
  const input=[b,a,b,{...a,run_id:'foreign'}]
  assert.deepEqual(orderEvents(input,'run-a').map(e=>e.seq),[1,2])
  assert.equal(input[0],b)
})

test('turn zero, setup and chronological turn boundaries are preserved',()=>{
  const turns=buildActivity([event(4,'TURN_STARTED',{},1,'p2'),event(3,'TURN_ENDED'),event(2,'DICE_ROLLED',{d1:1,d2:1,is_double:true}),event(1,'TURN_STARTED'),event(0,'GAME_STARTED')],names,'run-a')
  assert.equal(turns[0].setup,true)
  assert.equal(turns[1].turnIndex,0)
  assert.equal(turns[1].ended,true)
  assert.equal(turns[2].turnIndex,1)
})

test('a partial event window does not invent a turn start or identify an auction bidder as turn owner',()=>{
  const [turn]=buildActivity([event(80,'LLM_DECISION_REQUESTED',{decision_id:'auction',player_id:'p3',decision_type:'AUCTION_BID_DECISION'},7,'p3')],names,'run-a')
  assert.equal(turn.continued,true)
  assert.equal(turn.started,false)
  assert.equal(turn.playerId,null)
})

test('identical legitimate public messages remain separate across decisions and legacy messages',()=>{
  const e=[event(1,'LLM_PUBLIC_MESSAGE',{decision_id:'a',player_id:'p1',message:'Same message'}),event(2,'LLM_PUBLIC_MESSAGE',{decision_id:'b',player_id:'p1',message:'Same message'}),event(3,'LLM_PUBLIC_MESSAGE',{player_id:'p1',message:'Same message'})]
  const all=items(e)
  assert.equal(all.filter(i=>i.kind==='decision').reduce((n,i)=>n+i.messages.length,0)+all.filter(i=>i.kind==='chat').length,3)
})

test('private thoughts never count as public chat, including older events without decision IDs',()=>{
  const turns=buildActivity([event(1,'LLM_PRIVATE_THOUGHT',{decision_id:'a',player_id:'p1',thought:'PRIVATE_SENTINEL'}),event(2,'LLM_PRIVATE_THOUGHT',{player_id:'p2',thought:'LEGACY_PRIVATE_SENTINEL'})],names,'run-a')
  assert.match(JSON.stringify(turns),/LEGACY_PRIVATE_SENTINEL/)
  assert.doesNotMatch(JSON.stringify(filterActivity(turns,'chat')),/PRIVATE_SENTINEL/)
})

test('cash before and after a purchase is represented once, folded into its action',()=>{
  for(const before of [true,false]){
    const cash=event(before?1:2,'CASH_CHANGED',{player_id:'p1',delta:-140,reason:'buy_property'})
    const buy=event(before?2:1,'PROPERTY_PURCHASED',{player_id:'p1',space_index:11,price:140})
    const e=[cash,buy]
    assert.equal(ids(e).filter(id=>id===cash.event_id).length,1)
    assert.equal(items(e).filter(i=>i.kind==='group').length,0)
    assert.match(items(e).find(i=>i.kind==='action').text,/St\. Charles Place/)
  }
})

test('roll and move share one compact row while preserving both event identities',()=>{
  const e=[event(1,'DICE_ROLLED',{d1:6,d2:5,is_double:false}),event(2,'PLAYER_MOVED',{from:0,to:11,passed_go:false})]
  assert.equal(items(e).length,1)
  assert.deepEqual(ids(e),['e1','e2'])
  assert.match(items(e)[0].text,/rolled 11.*St\. Charles Place/)
})

test('unknown future engine events retain a readable fallback and their payload',()=>{
  const [unknown]=items([event(1,'FUTURE_ENGINE_EVENT',{fact:'retained'})])
  assert.equal(unknown.kind,'unknown')
  assert.equal(unknown.payload.fact,'retained')
})

test('counteroffer and acceptance terms identify the actual offer author rather than the original initiator',()=>{
  const payload={initiator_player_id:'p1',counterparty_player_id:'p2',exchange_index:1,max_exchanges:20,offer:{cash:100,properties:[],get_out_of_jail_cards:0},request:{cash:0,properties:['BALTIC_AVENUE'],get_out_of_jail_cards:0}}
  for(const [type,actor] of [['TRADE_COUNTERED','p2'],['TRADE_ACCEPTED','p1']]){
    const row=items([event(1,type,payload,0,actor)])[0]
    assert.ok(row.details.some(line=>/GPT.*gives.*\$100/.test(line)))
    assert.ok(row.details.some(line=>/Claude.*gives.*BALTIC_AVENUE/.test(line)))
  }
})

test('a terminal marker or answered decision cannot leave a stale waiting indicator',()=>{
  const request=event(1,'LLM_DECISION_REQUESTED',{decision_id:'a',player_id:'p1',decision_type:'PRE_ROLL'})
  assert.equal(waitingDecisionId(buildActivity([request],names)), 'a')
  assert.equal(waitingDecisionId(buildActivity([request,event(2,'LLM_DECISION_RESPONSE',{decision_id:'a',player_id:'p1',action_name:'roll_dice',valid:true,error:null})],names)),null)
  assert.equal(waitingDecisionId(buildActivity([request,event(2,'GAME_ENDED',{winner_player_id:'p1',reason:'TURN_LIMIT'})],names)),null)
})

test('provider reasoning is separate from public content, private tool fields and encrypted reasoning',()=>{
  assert.deepEqual(providerReasoning({choices:[{message:{content:'public',tool_calls:[{private_thought:'not provider reasoning'}]}}]}),{kind:'none'})
  assert.deepEqual(providerReasoning({choices:[{message:{reasoning:'provider text'}}]}),{kind:'text',text:'provider text'})
  assert.deepEqual(providerReasoning({choices:[{message:{reasoning_details:[{text:'one'},{summary:'two'}]}}]}),{kind:'text',text:'one\n\ntwo'})
  assert.deepEqual(providerReasoning({choices:[{message:{reasoning_details:[{type:'reasoning.encrypted',data:'opaque'}]}}]}),{kind:'unreadable'})
})

test('fallback-model requests and engine default actions remain distinct, and returned models come from recorded metadata',()=>{
  const bundle={decision_id:'a',summary:{phase:'decision_resolved'},final_action:{action:'roll_dice'},fallback_used:false,retry_used:true,attempts:[{attempt_index:0,requested_model:'anthropic/claude-opus-5.5',response_condition:'standard'},{attempt_index:1,requested_model:'anthropic/claude-opus-4.8',response_condition:'fallback_without_private_thought',response:{model:'anthropic/claude-opus-4.8',choices:[{message:{}}]}}]}
  const view=describeDecision(bundle,'anthropic/claude-opus-5.5')
  assert.equal(view.defaultActionApplied,false)
  assert.equal(view.attempts[1].usedFallbackModel,true)
  assert.equal(view.attempts[1].returnedModel,'anthropic/claude-opus-4.8')
  assert.equal(view.attempts[1].withoutPrivateThought,true)
  assert.deepEqual(view.attempts[1].reasoning,{kind:'none'})
  const fallback=describeDecision({...bundle,fallback_used:true,fallback_reason:'invalid_output'},'anthropic/claude-opus-5.5')
  assert.equal(fallback.defaultActionApplied,true)
  assert.match(fallback.outcome,/engine applied its default action/)
})

test('an unresolved or failed attempt is not described as an accepted answer',()=>{
  const view=describeDecision({decision_id:'a',summary:{phase:'decision_started'},attempts:[{attempt_index:0,error_reason:'provider_unavailable',response:{error:{message:'failed'}}}]},'openai/gpt-6.1-sol')
  assert.doesNotMatch(view.outcome,/^Accepted/)
})

test('earlier attempts cannot inherit the final fallback model from shared sequence metadata',()=>{
  const shared={returned_model:'anthropic/claude-opus-4.8'}
  assert.equal(returnedModel({attempt_index:0,response:{model:'anthropic/claude-opus-5.5'},sequence_meta:shared}),'anthropic/claude-opus-5.5')
  assert.equal(returnedModel({attempt_index:0,response:{error:{message:'unavailable'}},sequence_meta:shared}),null)
})

test('infrastructure-failed provisional fallback artifacts do not prove a game action was applied',()=>{
  const view=describeDecision({decision_id:'a',summary:{phase:'decision_started'},final_action:{action:'end_turn'},fallback_used:true,fallback_reason:'infrastructure_failure',attempts:[{attempt_index:0,error_reason:'provider_unavailable'}]},'openai/gpt-6.1-sol')
  assert.equal(view.defaultActionApplied,false)
  assert.equal(view.accepted,false)
  assert.equal(view.finalAction,null)
  assert.doesNotMatch(view.outcome,/engine applied|^Accepted/)
})

test('a resolved engine default action remains distinct from an accepted model answer',()=>{
  const view=describeDecision({decision_id:'a',summary:{phase:'decision_resolved'},final_action:{action:'end_turn'},fallback_used:true,attempts:[]},'openai/gpt-6.1-sol')
  assert.equal(view.defaultActionApplied,true)
  assert.equal(view.accepted,false)
  assert.equal(view.finalAction,'end_turn')
})

test('an auction leader can win when the auction reaches its action limit',()=>{
  const row=items([event(1,'AUCTION_ENDED',{property_space:'BALTIC_AVENUE',winner_player_id:'p1',winning_bid:60,reason:'MAX_ACTIONS'})])[0]
  assert.match(row.text,/Claude won.*\$60/)
  assert.doesNotMatch(row.text,/no sale/)
  assert.ok(row.details.some(d=>/Max actions/.test(d)))
})

test('empty public-message events preserve their decision record but do not count as readable chat',()=>{
  const turns=buildActivity([event(1,'LLM_PUBLIC_MESSAGE',{decision_id:'empty',player_id:'p1',message:'  '})],names,'run-a')
  assert.deepEqual(turns[0].items[0].eventIds,['e1'])
  assert.equal(filterActivity(turns,'chat').length,0)
})
