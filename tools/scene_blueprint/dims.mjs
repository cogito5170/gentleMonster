// THE STILL RUNWAY -- one scene that carries the whole story (walk · turn · pick up · keep).
// One source for the render and the drawings. Metres, seconds. Studio plan: x across (0 = centre),
// z away from the camera (camera at z = 0, the scene is at z < 0), y up.
export const D = {
  studio: { w: 8, d: 8.2, h: 3.5 },                 // white seamless studio (floor + back wall)
  cam: { pos: [0, 1.2, 0], at: [0, 0.9, -5], vfov: 38, shutter: 1 / 3, lens: '35 mm (APS-C, ≈ 50 mm FF)', iso: 125, f: 'f/8' },
  cube: { x: 0, z: -5, s: 0.45 },
  me: { coat: '#161514', knit: '#8b8d8c', trousers: '#c8b69b', accent: '#c8302a' },   // the still one
  walkers: [                                         // x0 = position when the shutter opens; v m/s; dir +1 = to the right
    { id: 'W1', col: '#151515', z: -3.3, x0: -2.35, dir: 1, v: 1.35 },
    { id: 'W2', col: '#2b2b2b', z: -4.0, x0: 2.45, dir: -1, v: 1.4 },
    { id: 'W3', col: '#c8302a', z: -6.4, x0: -1.85, dir: 1, v: 1.2 },
    { id: 'W4', col: '#6a6a6a', z: -7.4, x0: -0.75, dir: -1, v: 1.3 },
  ],
  // the one who turns: walks in from the right, bends toward the still one and slows down (less blur)
  turner: { col: '#c9b79c', p0: [2.7, -6.2], p1: [1.6, -6.0], p2: [0.85, -5.35], s0: 0.94, bag: true },
  light: { key: [-2.2, 3.2, -2.6], fill: [2.6, 2.4, -3.2] },
  samples: 40,
};
