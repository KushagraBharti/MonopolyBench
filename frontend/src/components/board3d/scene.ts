import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import type { Player, StateSnapshot } from '@/net/contracts';
import { getPlayerColor, getPlayerIndex } from '@/domain/monopoly/colors';
import { getCardDetails } from '@/domain/monopoly/cardData';
import { blenderPosition, developmentVisible, DIE_NORMALS } from './presentation';
import type { PresentationUpdate } from './presentation';

const BASE = '/board3d/v1/';
type Vec = [number, number, number];
type Anchor = { space_index: number; kind: 'house' | 'hotel'; slot: number; position_blender: Vec; scale: Vec; rotation_blender: Vec };
type Manifest = {
  assets: Record<string, { file: string }>;
  space_anchors: Record<string, Vec>;
  development_anchors: Anchor[];
  jail_gate_anchor_blender: number[][];
  jail_player_anchors_blender: Record<string, Vec>;
  status_markers: { anchors: { space_index: number; kind: string; matrix_blender: number[][] }[] };
};
type Motion = { start: number; duration: number; apply: (t: number) => void; finish?: () => void };
type Piece = { root: THREE.Group; anchor: Anchor; visible: boolean };
const smooth = (t: number) => t * t * (3 - 2 * t);
const vec = (v: readonly number[]) => new THREE.Vector3(...blenderPosition(v));

function disposeTree(root: THREE.Object3D) {
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>();
  root.traverse(o => {
    if (!(o instanceof THREE.Mesh)) return;
    geometries.add(o.geometry);
    for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
      materials.add(m);
      for (const value of Object.values(m)) if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  geometries.forEach(g => g.dispose()); materials.forEach(m => m.dispose()); textures.forEach(t => t.dispose());
}

export class BoardScene {
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.PerspectiveCamera(38, 1, .1, 100);
  readonly renderer: THREE.WebGLRenderer;
  readonly controls: OrbitControls;
  private readonly host: HTMLElement;
  private readonly onSelect: (index: number) => void;
  private readonly onFailure: () => void;
  private readonly motions = new Map<string, Motion>();
  private readonly pieces: Piece[] = [];
  private readonly players = new Map<string, THREE.Group>();
  private readonly owners = new Map<number, THREE.Mesh>();
  private readonly mortgages = new Map<number, THREE.Mesh>();
  private readonly targets: THREE.Mesh[] = [];
  private readonly assets = new Map<string, THREE.Group>();
  private readonly draco = new DRACOLoader().setDecoderPath(`${BASE}draco/`).setWorkerLimit(2);
  private readonly abort = new AbortController();
  private readonly resize: ResizeObserver;
  private readonly observer: IntersectionObserver;
  private environment: THREE.WebGLRenderTarget;
  private manifest!: Manifest;
  private gate = new THREE.Group();
  private dice: THREE.Group[] = [];
  private card: THREE.Group | null = null;
  private readonly highlight: THREE.Mesh<THREE.BufferGeometry, THREE.MeshBasicMaterial> = new THREE.Mesh(new THREE.BoxGeometry(1, .025, 1.6), new THREE.MeshBasicMaterial({ color: '#f7bf47', transparent: true, opacity: .22, depthWrite: false }));
  private snapshot: StateSnapshot | null = null;
  private ready = false;
  private disposed = false;
  private visible = true;
  private dirty = true;
  private raf = 0;
  private transientQueue: PresentationUpdate['events'] = [];
  private transientBusy = false;
  private down = new THREE.Vector2();

  constructor(host: HTMLElement, onSelect: (index: number) => void, onFailure: () => void) {
    this.host = host; this.onSelect = onSelect; this.onFailure = onFailure;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = .95;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.domElement.setAttribute('aria-label', 'Interactive 3D Monopoly board. Drag to orbit, scroll to zoom. Use the property selector for keyboard inspection.');
    this.renderer.domElement.setAttribute('role', 'img');
    this.renderer.domElement.addEventListener('webglcontextlost', this.contextLost);
    host.appendChild(this.renderer.domElement);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true; this.controls.dampingFactor = .09;
    this.controls.minDistance = 5; this.controls.maxDistance = 48;
    this.controls.maxPolarAngle = Math.PI * .46;
    this.controls.minPolarAngle = .04;
    this.controls.enablePan = true;
    this.controls.addEventListener('change', this.invalidate);
    this.resetCamera();
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    const room = new RoomEnvironment();
    this.environment = pmrem.fromScene(room, .04);
    this.scene.environment = this.environment.texture;
    this.scene.environmentIntensity = .75;
    room.dispose(); pmrem.dispose();
    this.scene.add(new THREE.HemisphereLight('#fff5e3', '#99a5b4', 1.25));
    const key = new THREE.DirectionalLight('#fff3dd', 2.4);
    key.position.set(-5, 13, 8); key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: .5, far: 35 });
    key.shadow.bias = -.0004; key.shadow.normalBias = .025;
    this.scene.add(key);
    const fill = new THREE.DirectionalLight('#d8edff', .8); fill.position.set(6, 8, -7); this.scene.add(fill);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ opacity: .15 }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -.12; ground.receiveShadow = true; this.scene.add(ground);
    this.highlight.visible = false; this.scene.add(this.highlight);
    this.resize = new ResizeObserver(() => {
      const w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h); this.resetCamera(); this.dirty = true;
    });
    this.resize.observe(host);
    this.observer = new IntersectionObserver(entries => { this.visible = entries[0]?.isIntersecting ?? true; this.dirty = true; });
    this.observer.observe(host);
    this.renderer.domElement.addEventListener('pointerdown', this.pointerDown);
    this.renderer.domElement.addEventListener('pointerup', this.pointerUp);
    this.raf = requestAnimationFrame(this.tick);
  }

  async load() {
    const response = await fetch(`${BASE}manifest.json`, { signal: this.abort.signal });
    if (!response.ok) throw new Error('Board asset manifest could not be loaded');
    this.manifest = await response.json() as Manifest;
    const loader = new GLTFLoader().setDRACOLoader(this.draco);
    const results = await Promise.allSettled(Object.entries(this.manifest.assets).map(async ([name, entry]) => {
      const gltf = await loader.loadAsync(`${BASE}${entry.file}`);
      if (this.disposed) { disposeTree(gltf.scene); return; }
      gltf.scene.traverse(o => { if (o instanceof THREE.Mesh) { o.castShadow = true; o.receiveShadow = true; } });
      this.assets.set(name, gltf.scene);
    }));
    if (this.disposed) return;
    if (results.some(r => r.status === 'rejected')) throw new Error('A board model could not be loaded');
    this.scene.add(this.assets.get('board_web')!);
    const dotCanvas = document.createElement('canvas'); dotCanvas.width = dotCanvas.height = 64;
    const dots = dotCanvas.getContext('2d')!; dots.fillStyle = '#272727'; dots.beginPath(); dots.arc(32, 32, 1.4, 0, Math.PI * 2); dots.fill();
    const dotMap = new THREE.CanvasTexture(dotCanvas); dotMap.wrapS = dotMap.wrapT = THREE.RepeatWrapping; dotMap.repeat.set(36, 36);
    const dotGrid = new THREE.Mesh(new THREE.PlaneGeometry(7.8, 7.8), new THREE.MeshBasicMaterial({ map: dotMap, transparent: true, opacity: .18, depthWrite: false }));
    dotGrid.rotation.x = -Math.PI / 2; dotGrid.position.y = .385; this.scene.add(dotGrid);
    for (const anchor of this.manifest.development_anchors) {
      const parent = new THREE.Group(); parent.position.copy(vec(anchor.position_blender));
      parent.rotation.y = anchor.rotation_blender[2]; parent.scale.set(anchor.scale[0], anchor.scale[2], anchor.scale[1]);
      const root = this.clone(anchor.kind); root.scale.setScalar(0); root.visible = false; parent.add(root); this.scene.add(parent);
      this.pieces.push({ root, anchor, visible: false });
    }
    const gateParent = new THREE.Group(); gateParent.position.copy(this.matrixPosition(this.manifest.jail_gate_anchor_blender));
    this.gate = this.clone('jail_gate'); gateParent.add(this.gate); this.scene.add(gateParent); this.gate.position.y = .72;
    for (const anchor of this.manifest.status_markers.anchors) {
      const mortgage = anchor.kind === 'mortgage';
      const marker = new THREE.Mesh(new THREE.BoxGeometry(.73, .016, mortgage ? .20 : .047), new THREE.MeshStandardMaterial({ color: mortgage ? '#272727' : '#ffffff', roughness: .5 }));
      marker.position.copy(this.matrixPosition(anchor.matrix_blender));
      marker.rotation.y = Math.atan2(anchor.matrix_blender[1][0], anchor.matrix_blender[0][0]);
      marker.visible = false; this.scene.add(marker);
      (mortgage ? this.mortgages : this.owners).set(anchor.space_index, marker);
      if (mortgage) {
        const label = this.textPlane('MORTGAGED', '#ffffff', '#272727', .70, .18);
        label.rotation.x = -Math.PI / 2; label.position.y = .010; marker.add(label);
      }
    }
    for (let index = 0; index < 40; index++) {
      const side = Math.floor(index / 10), n = index % 10;
      const x = side === 0 ? (n ? 5 - n : 5.25) : side === 1 ? -5.25 : side === 2 ? (n ? n - 5 : -5.25) : 5.25;
      const z = side === 0 ? 5.25 : side === 1 ? (n ? 5 - n : 5.25) : side === 2 ? -5.25 : (n ? n - 5 : -5.25);
      const target = new THREE.Mesh(new THREE.BoxGeometry(n ? (side % 2 ? 1.6 : 1) : 1.6, .05, n ? (side % 2 ? 1 : 1.6) : 1.6), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false, colorWrite: false }));
      target.position.set(x, .42, z); target.userData.spaceIndex = index;
      this.scene.add(target); this.targets.push(target);
    }
    this.dice = [this.clone('die'), this.clone('die')];
    this.dice.forEach(die => { die.visible = false; this.scene.add(die); });
    this.ready = true; this.dirty = true;
  }

  update(update: PresentationUpdate) {
    if (!this.ready || this.disposed) return;
    const { snapshot, immediate } = update;
    if (update.reset || immediate) {
      this.motions.clear(); this.clearCard(); this.transientQueue = []; this.transientBusy = false;
      this.dice.forEach(die => { die.visible = false; });
      delete this.host.dataset.dice;
    }
    const old = this.snapshot;
    const board = new Map(snapshot?.board.map(s => [s.index, s]) ?? []);
    for (const piece of this.pieces) {
      const space = board.get(piece.anchor.space_index);
      const show = developmentVisible(space, piece.anchor.kind, piece.anchor.slot);
      if (!immediate && show === piece.visible) continue;
      const wasHotel = old?.board.find(s => s.index === piece.anchor.space_index)?.hotel;
      const delay = show && ((piece.anchor.kind === 'hotel' && !wasHotel) || (piece.anchor.kind === 'house' && wasHotel)) ? .35 : 0;
      this.development(piece, show, immediate, delay);
    }
    for (const [index, marker] of this.owners) {
      const owner = board.get(index)?.owner_id;
      marker.visible = Boolean(owner);
      if (owner) (marker.material as THREE.MeshStandardMaterial).color.set(getPlayerColor(owner));
    }
    for (const [index, marker] of this.mortgages) marker.visible = Boolean(board.get(index)?.mortgaged);
    const oldJailed = old?.players.some(p => p.in_jail && !p.bankrupt) ?? false;
    const jailed = snapshot?.players.some(p => p.in_jail && !p.bankrupt) ?? false;
    const jailChanged = snapshot?.players.some(p => p.in_jail !== old?.players.find(before => before.player_id === p.player_id)?.in_jail) ?? false;
    for (const [id, root] of this.players) if (!snapshot?.players.some(p => p.player_id === id)) root.visible = false;
    for (const p of snapshot?.players ?? []) {
      let root = this.players.get(p.player_id);
      if (!root) {
        root = this.clone(`player_${['red', 'blue', 'green', 'gold'][getPlayerIndex(p.player_id) % 4]}`);
        this.players.set(p.player_id, root); this.scene.add(root);
      }
      const pose = this.playerPose(p, snapshot!);
      const previous = old?.players.find(player => player.player_id === p.player_id);
      root.visible = !p.bankrupt;
      if (immediate || !previous) { root.position.copy(pose.position); root.scale.setScalar(pose.scale); continue; }
      const previousPose = this.playerPose(previous, old!);
      if (previousPose.position.distanceTo(pose.position) < .001 && Math.abs(previousPose.scale - pose.scale) < .001) continue;
      const object = root, from = object.position.clone(), scale = object.scale.x;
      this.motion(`player:${p.player_id}`, .95, t => {
        const u = smooth(t); object.position.lerpVectors(from, pose.position, u);
        object.position.y += Math.sin(Math.PI * t) * 1.2;
        object.scale.setScalar(THREE.MathUtils.lerp(scale, pose.scale, u));
      }, undefined, jailChanged ? .22 : 0);
    }
    if (immediate) this.gate.position.y = jailed ? 0 : .72;
    else if (jailChanged || oldJailed !== jailed) {
      const start = this.gate.position.y;
      this.motion('gate', 1.55, t => {
        this.gate.position.y = t < .17 ? THREE.MathUtils.lerp(start, .72, smooth(t / .17)) : t < .77 ? .72 : THREE.MathUtils.lerp(.72, jailed ? 0 : .72, smooth((t - .77) / .23));
      });
    }
    this.snapshot = snapshot;
    this.transientQueue.push(...update.events.filter(e => e.type === 'CARD_DRAWN' || e.type === 'DICE_ROLLED'));
    // Fast streams reconcile state immediately; cap presentation backlog without slowing the engine.
    if (this.transientQueue.length > 8) this.transientQueue = this.transientQueue.slice(-8);
    this.nextTransient(); this.dirty = true;
    this.host.dataset.houses = String(snapshot?.board.reduce((sum, s) => sum + (s.hotel ? 0 : s.houses), 0) ?? 0);
    this.host.dataset.hotels = String(snapshot?.board.filter(s => s.hotel).length ?? 0);
    this.host.dataset.jailed = String(snapshot?.players.filter(p => p.in_jail && !p.bankrupt).length ?? 0);
    this.host.dataset.runId = snapshot?.run_id ?? '';
  }

  private clone(name: string) { return this.assets.get(name)!.clone(true); }
  private matrixPosition(m: number[][]) { return vec([m[0][3], m[1][3], m[2][3]]); }
  private playerPose(p: Player, snapshot: StateSnapshot) {
    const jailed = snapshot.players.filter(p => p.in_jail && !p.bankrupt);
    const position = p.in_jail ? vec(this.manifest.jail_player_anchors_blender[String(Math.max(0, jailed.findIndex(x => x.player_id === p.player_id)) % 4)]) : vec(this.manifest.space_anchors[String(p.position)]);
    const peers = snapshot.players.filter(x => x.position === p.position && !x.in_jail && !x.bankrupt);
    if (!p.in_jail && peers.length > 1) {
      const a = peers.findIndex(x => x.player_id === p.player_id) * Math.PI * 2 / peers.length;
      position.x += .30 * Math.cos(a); position.z -= .30 * Math.sin(a);
    }
    return { position, scale: p.in_jail ? .28 : .75 };
  }
  private development(piece: Piece, show: boolean, immediate: boolean, delay: number) {
    const { root, anchor } = piece; piece.visible = show;
    const key = `piece:${anchor.space_index}:${anchor.kind}:${anchor.slot}`;
    if (immediate) { this.motions.delete(key); root.visible = show; root.scale.setScalar(show ? 1 : 0); root.position.y = 0; return; }
    const from = root.scale.x; root.visible = true;
    this.motion(key, .72, t => {
      const u = show ? 1 + 2.70158 * Math.pow(t - 1, 3) + 1.70158 * Math.pow(t - 1, 2) : smooth(t);
      root.scale.setScalar(Math.max(0, THREE.MathUtils.lerp(from, show ? 1 : 0, u)));
      root.position.y = show ? .24 * (1 - t) : .3 * t;
    }, () => { root.visible = show; root.scale.setScalar(show ? 1 : 0); root.position.y = 0; }, delay + anchor.slot * .07);
  }
  private motion(key: string, duration: number, apply: Motion['apply'], finish?: () => void, delay = 0) {
    this.motions.set(key, { start: performance.now() / 1000 + delay, duration, apply, finish }); this.dirty = true;
  }
  private nextTransient() {
    if (this.transientBusy || !this.transientQueue.length) return;
    const event = this.transientQueue.shift()!; this.transientBusy = true;
    const done = () => { this.transientBusy = false; this.nextTransient(); };
    if (event.type === 'CARD_DRAWN') {
      this.clearCard();
      const { deck_type: deck, card_id: cardId } = event.payload;
      const details = getCardDetails(deck, cardId);
      this.card = new THREE.Group();
      const accent = deck === 'CHANCE' ? '#ff9656' : '#7fcce0';
      const body = new THREE.Mesh(new THREE.BoxGeometry(2.55, .045, 1.55), new THREE.MeshStandardMaterial({ color: '#fffdf6', roughness: .52 }));
      body.castShadow = true; this.card.add(body);
      const face = this.cardFace(deck === 'CHANCE' ? 'CHANCE' : 'COMMUNITY CHEST', details.title, details.description, accent);
      face.rotation.x = -Math.PI / 2; face.position.y = .026; this.card.add(face);
      const back = this.textPlane(deck === 'CHANCE' ? '?' : 'M', '#ffffff', accent, 2.5, 1.50);
      back.rotation.x = Math.PI / 2; back.position.y = -.026; this.card.add(back);
      const card = this.card; this.scene.add(card);
      card.userData.cardId = cardId;
      const origin = new THREE.Vector3(deck === 'CHANCE' ? -1.8 : 1.8, .48, deck === 'CHANCE' ? -1.8 : 2);
      const target = new THREE.Vector3(0, 2.3, .6);
      this.host.dataset.card = cardId;
      this.motion('card', 3.2, t => {
        const u = t < .23 ? smooth(t / .23) : t > .80 ? smooth((1 - t) / .20) : 1;
        card.position.lerpVectors(origin, target, u); card.scale.setScalar(.7 + .4 * u);
        card.rotation.set(.18 * u, 0, Math.PI * (1 - u));
      }, () => { this.clearCard(); done(); });
    } else if (event.type === 'DICE_ROLLED') {
      const values = [event.payload.d1, event.payload.d2];
      this.dice.forEach((die, index) => {
        die.visible = true;
        const settle = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(...DIE_NORMALS[values[index]]), new THREE.Vector3(0, 1, 0));
        const start = new THREE.Quaternion().setFromEuler(new THREE.Euler(2.3 + index, 3.4, 1.2));
        this.motion(`die:${index}`, 1.25, t => {
          const spin = new THREE.Quaternion().setFromEuler(new THREE.Euler((1 - t) * Math.PI * 4, (1 - t) * Math.PI * 2, 0));
          die.quaternion.copy(start).slerp(settle, smooth(t)).premultiply(spin);
          // The model origin is its center. Rotated bounds keep every face above the board.
          const rotation = new THREE.Matrix4().makeRotationFromQuaternion(die.quaternion).elements;
          const clearance = .384 + .234 * (Math.abs(rotation[1]) + Math.abs(rotation[5]) + Math.abs(rotation[9]));
          die.position.set(.7 + index * .8, clearance + 1.3 * (1 - smooth(t)) + Math.abs(Math.sin(t * Math.PI * 3)) * .18 * (1 - t), 2.45);
        });
      });
      this.host.dataset.dice = values.join(',');
      this.motion('dice-hold', 2.4, () => {}, () => { this.dice.forEach(d => { d.visible = false; }); delete this.host.dataset.dice; done(); });
    } else done();
  }
  private clearCard() {
    if (this.card) { this.scene.remove(this.card); disposeTree(this.card); this.card = null; }
    delete this.host.dataset.card;
  }
  /** Read-only render diagnostics for browser regression tests and asset inspection. */
  inspect() {
    return {
      houses: this.pieces.filter(p => p.anchor.kind === 'house' && p.root.visible && p.root.scale.x > .99).length,
      hotels: this.pieces.filter(p => p.anchor.kind === 'hotel' && p.root.visible && p.root.scale.x > .99).length,
      gateHeight: this.gate.position.y,
      card: this.card?.userData.cardId ?? null,
      dice: this.dice.map(d => ({ visible: d.visible, position: d.position.toArray(), up: Object.fromEntries(Object.entries(DIE_NORMALS).map(([face, normal]) => [face, new THREE.Vector3(...normal).applyQuaternion(d.quaternion).y])) })),
      players: Object.fromEntries([...this.players].map(([id, p]) => [id, { visible: p.visible, position: p.position.toArray(), scale: p.scale.x }])),
      owners: [...this.owners].filter(([, m]) => m.visible).map(([i]) => i),
      mortgages: [...this.mortgages].filter(([, m]) => m.visible).map(([i]) => i),
      motions: this.motions.size,
    };
  }
  private textPlane(text: string, ink: string, background: string, width: number, height: number) {
    const canvas = document.createElement('canvas'); canvas.width = 1024; canvas.height = 256;
    const c = canvas.getContext('2d')!; c.fillStyle = background; c.fillRect(0, 0, 1024, 256);
    c.fillStyle = ink; c.font = 'bold 100px Arial'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, 512, 128, 950);
    const map = new THREE.CanvasTexture(canvas); map.colorSpace = THREE.SRGBColorSpace;
    return new THREE.Mesh(new THREE.PlaneGeometry(width, height), new THREE.MeshBasicMaterial({ map }));
  }
  private cardFace(deck: string, title: string, description: string, accent: string) {
    const canvas = document.createElement('canvas'); canvas.width = 1536; canvas.height = 960;
    const c = canvas.getContext('2d')!;
    c.fillStyle = '#fffdf6'; c.fillRect(0, 0, 1536, 960); c.strokeStyle = accent; c.lineWidth = 14; c.strokeRect(26, 26, 1484, 908);
    c.textAlign = 'center'; c.fillStyle = accent; c.font = 'bold 52px Arial'; c.fillText(deck, 768, 158);
    const wrap = (text: string, y: number, size: number, bold: boolean) => {
      c.font = `${bold ? 'bold ' : ''}${size}px Arial`; let line = '';
      for (const word of text.split(/\s+/)) {
        if (c.measureText(`${line} ${word}`).width > 1280 && line) { c.fillText(line, 768, y); y += size * 1.35; line = word; }
        else line = line ? `${line} ${word}` : word;
      }
      c.fillText(line, 768, y); return y + size * 1.35;
    };
    c.fillStyle = '#171717'; const end = wrap(title.toUpperCase(), 320, 68, true);
    wrap(description, Math.max(540, end + 60), 42, false);
    c.font = 'bold 30px Arial'; c.fillText('MONOPOLYBENCH', 768, 861);
    const map = new THREE.CanvasTexture(canvas); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = 4;
    return new THREE.Mesh(new THREE.PlaneGeometry(2.5, 1.5), new THREE.MeshBasicMaterial({ map }));
  }
  focus(index: number | null) {
    const target = index === null ? undefined : this.targets[index];
    this.highlight.visible = Boolean(target);
    if (target) { this.highlight.position.copy(target.position); this.highlight.position.y += .04; this.highlight.geometry.dispose(); this.highlight.geometry = target.geometry.clone(); }
    this.dirty = true;
  }
  resetCamera = (overhead = false) => {
    const halfFov = Math.atan(Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * Math.min(1, this.camera.aspect));
    const distance = 8.7 / Math.sin(halfFov);
    this.camera.position.set(overhead ? 0 : 11.5, overhead ? 24 : 16, overhead ? .1 : 16).normalize().multiplyScalar(distance);
    this.controls.target.set(0, .3, 0); this.controls.update(); this.dirty = true;
  };
  private invalidate = () => { this.dirty = true; };
  private contextLost = (event: globalThis.Event) => { event.preventDefault(); this.onFailure(); };
  private pointerDown = (event: PointerEvent) => { this.down.set(event.clientX, event.clientY); };
  private pointerUp = (event: PointerEvent) => {
    if (this.down.distanceTo(new THREE.Vector2(event.clientX, event.clientY)) > 5) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1), this.camera);
    const hit = ray.intersectObjects(this.targets, false)[0];
    if (hit) this.onSelect(hit.object.userData.spaceIndex as number);
  };
  private tick = () => {
    if (this.disposed) return;
    const now = performance.now() / 1000;
    for (const [key, motion] of [...this.motions]) {
      if (now < motion.start) continue;
      const t = Math.min(1, (now - motion.start) / motion.duration);
      motion.apply(t); this.dirty = true;
      if (t === 1) { this.motions.delete(key); motion.finish?.(); }
    }
    this.controls.update();
    if (this.dirty && this.visible && !document.hidden) {
      this.renderer.render(this.scene, this.camera); this.dirty = false;
    }
    this.raf = requestAnimationFrame(this.tick);
  };
  dispose() {
    if (this.disposed) return;
    this.disposed = true; this.abort.abort(); cancelAnimationFrame(this.raf);
    this.resize.disconnect(); this.observer.disconnect(); this.controls.dispose();
    this.renderer.domElement.removeEventListener('webglcontextlost', this.contextLost);
    this.renderer.domElement.removeEventListener('pointerdown', this.pointerDown);
    this.renderer.domElement.removeEventListener('pointerup', this.pointerUp);
    this.clearCard(); disposeTree(this.scene);
    for (const asset of this.assets.values()) disposeTree(asset);
    this.environment.dispose(); this.draco.dispose(); this.renderer.dispose(); this.renderer.domElement.remove();
    this.motions.clear();
  }
}
