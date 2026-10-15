// One source for the render and the drawings. Metres. Assumed, not surveyed -- measure the real window first.
// x across the window (0 = left jamb, seen from the street), y up from the sidewalk, z toward the street (glass at 0).
export const D = {
  win: { w: 3.0, h: 2.7 },            // glass opening above the window bed
  stage: { h: 0.45 },                 // window bed height above the sidewalk
  frame: { side: 0.35, top: 0.4 },    // granite surround
  depth: 1.5,                         // glass to backdrop
  base: { x0: 0.75, x1: 1.65, z0: -1.05, z1: -0.35, h: 0.12 },   // white architectural model base
  man: { x: 1.2, z: -0.7, h: 1.53 },  // headless mannequin standing on the base (feet to neck cap)
  cam: { y: 0.5 },                    // film camera centre above the base top
  tag: { gx: 1.8, gy: 1.32, y: 1.08, w: 0.07, h: 0.12, out: 0.28 },  // string meets glass at (gx, gy); tag bottom y; tag hangs `out` m outside
  bag: { x: 2.15, z: -0.65, w: 0.32, d: 0.12, h: 0.4 },
  spots: [
    { x: 1.2, aim: [1.2, 1.35, -0.7], cd: 26, angle: 0.34, name: 'S1 mannequin', beam: '24°' },
    { x: 2.15, aim: [2.15, 0.7, -0.65], cd: 14, angle: 0.26, name: 'S2 bag', beam: '18°' },
  ],
  eye: { pos: [1.5, 1.5, 3.6], at: [1.5, 1.5, -0.5], fov: 50 },
};
