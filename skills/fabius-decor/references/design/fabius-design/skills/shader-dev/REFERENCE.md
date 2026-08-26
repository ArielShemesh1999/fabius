---
name: fabius-decor-shader-dev
description: GLSL shader techniques for ray marching, fluid simulation, particle systems, and procedural generation — hero visuals and motion stills.
triggers:
  - "shader"
  - "glsl"
  - "ray marching"
  - "fluid simulation"
  - "procedural generation"
---

# shader-dev

## What it does

Apply GLSL shader techniques to produce real-time visual effects: ray marching, fluid simulation, particle systems, and procedural generation. Suited for hero section visuals, animated backgrounds, and high-quality motion stills.

## When to use

- You need a live, GPU-driven hero visual (not a video or GIF).
- You want procedural geometry or noise-based animation without 3D assets.
- You're building a canvas or WebGL visual that must run in the browser.

## Techniques covered

| Technique | Use case |
|---|---|
| Ray marching | Signed-distance-field shapes, soft shadows, ambient occlusion |
| Fluid simulation | Ink-in-water, smoke, fire effects |
| Particle systems | Constellation fields, dust, sparks |
| Procedural noise | Terrain, organic textures, animated gradients |

## How to use

1. Set up a WebGL canvas with a full-screen quad:
   ```html
   <canvas id="c"></canvas>
   ```

2. Write vertex + fragment shaders. Minimal ray-march template:
   ```glsl
   // fragment shader
   uniform vec2 u_resolution;
   uniform float u_time;

   float sdSphere(vec3 p, float r) { return length(p) - r; }

   void main() {
     vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;
     vec3 ro = vec3(0.0, 0.0, 3.0);
     vec3 rd = normalize(vec3(uv, -1.0));
     float t = 0.0;
     for (int i = 0; i < 64; i++) {
       float d = sdSphere(ro + rd * t, 1.0);
       if (d < 0.001) break;
       t += d;
     }
     gl_FragColor = vec4(vec3(t * 0.1), 1.0);
   }
   ```

3. Pass uniforms (`u_time`, `u_resolution`, `u_mouse`) from JS on each animation frame.

4. For fluid simulation, implement a ping-pong FBO loop updating velocity and density textures each frame.

## Tips

- Use `smoothstep` and `mix` for soft transitions; avoid hard `if` branches in inner loops.
- Profile with browser DevTools GPU flame charts; reduce march steps first when fps drops.
- `dFdx`/`dFdy` derivatives enable cheap normal estimation from an SDF without extra samples.

## Output

A self-contained WebGL sketch or snippet producing the target visual effect, ready to embed in a canvas element.
