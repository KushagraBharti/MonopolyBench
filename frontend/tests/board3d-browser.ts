import { BoardScene } from '../src/components/board3d/scene';
import { PresentationCursor } from '../src/components/board3d/presentation';
import type { StateSnapshot, Event } from '../src/net/contracts';
import fixture from './fixtures/board3d.json';

const data = fixture as unknown as { initial_snapshot: StateSnapshot; cues: { event: Event; after_snapshot: StateSnapshot }[] };
const status = document.querySelector('#status')!;
const button = document.querySelector<HTMLButtonElement>('#run')!;
const board = new BoardScene(document.querySelector('#board')!, () => {}, () => { status.textContent = 'FAIL: WebGL'; });
const cursor = new PresentationCursor();
const checks: string[] = [];
const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
const check = (name: string, ok: boolean) => { if (!ok) throw new Error(name); checks.push(name); status.textContent = `${checks.length} checks passed · ${name}`; };
const sync = () => board.update(cursor.accept(data.initial_snapshot, [], 'seek:initial', false));
board.load().then(() => { sync(); button.disabled = false; status.textContent = 'Ready · synthetic fixtures, no game writes'; });
button.onclick = async () => {
  button.disabled = true;
  try {
    // A dedicated reset key hydrates once; subsequent cues animate through the public presentation API.
    board.update(cursor.accept(data.initial_snapshot, [], 'test', true));
    check('Clean board', board.inspect().houses === 0 && board.inspect().hotels === 0 && board.inspect().card === null);
    for (let i = 0; i < data.cues.length; i++) {
      const cue = data.cues[i]; board.update(cursor.accept(cue.after_snapshot, [cue.event], 'test', true));
      await wait(i === 4 || i === 7 ? 900 : i === 8 ? 1450 : 1900);
      const view = board.inspect();
      if (i === 0) check('One house rises on purchase', view.houses === 1 && view.owners.includes(6));
      if (i === 1) check('Four houses visible', view.houses === 4);
      if (i === 2) check('Hotel replaces all four houses', view.hotels === 1 && view.houses === 0);
      if (i === 3) check('Actual player enters the closed jail', view.gateHeight < .001 && Math.abs(view.players.P1.scale - .28) < .001);
      if (i === 4 || i === 7) {
        check(`Independent ${cue.event.type} face ${i}`, view.card === (cue.event as Event & { type: 'CARD_DRAWN' }).payload.card_id);
        await wait(2600); check(`Card returns and is removed ${i}`, board.inspect().card === null);
        board.update(cursor.accept(cue.after_snapshot, [cue.event], 'test', true));
        check(`Duplicate draw stays suppressed ${i}`, board.inspect().card === null);
      }
      if (i === 5) check('Release opens jail and restores player', view.gateHeight > .71 && Math.abs(view.players.P1.scale - .75) < .001);
      if (i === 6) check('Hotel sale restores supplied houses', view.houses === 4 && view.hotels === 0);
      if (i === 8) {
        check('Supplied dice faces land up', view.dice[0].up['3'] > .999 && view.dice[1].up['5'] > .999);
        check('Dice clear the board', view.dice.every(d => d.position[1] >= .617));
        await wait(1100); check('Dice settle then hide', board.inspect().dice.every(d => !d.visible));
      }
      if (i === 9) check('House sale clears the slots', view.houses === 0 && view.hotels === 0);
    }
    const mortgaged = structuredClone(data.cues[1].after_snapshot); mortgaged.board[6].mortgaged = true;
    board.update(cursor.accept(mortgaged, [], 'seek:mortgage', false));
    check('Snapshot seek restores development and mortgage immediately', board.inspect().houses === 4 && board.inspect().mortgages.includes(6) && board.inspect().motions === 0);
    sync(); check('Reset clears all transient effects', board.inspect().card === null && board.inspect().houses === 0 && board.inspect().dice.every(d => !d.visible));
    document.body.dataset.result = 'PASS'; document.body.dataset.checks = JSON.stringify(checks); status.textContent = `PASS · ${checks.length} actual-render checks`;
  } catch (error) { document.body.dataset.result = 'FAIL'; status.textContent = String(error); console.error(error); }
};
