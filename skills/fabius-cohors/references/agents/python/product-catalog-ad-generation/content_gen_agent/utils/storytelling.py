# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#  A template for generating cinematic scenes for video and image generation.

STORYTELLING_INSTRUCTIONS: str = """
The following template is designed to guide your generation process for
tasks like creating storyboards, generating keyframe images,
and animating video sequences.

### **Universal Cinematic Scene Generation Template**

Use this structured template to define the visual parameters for any video or
image generation task. Filling out these sections methodically ensures clarity,
detail, and a high-quality, cinematic result.

---

#### **[SECTION 1: STYLE & MEDIUM DEFINITION]**

**Purpose:** This section establishes the foundational aesthetic and technical
execution of the scene. It is the most critical component, defining the "look
and feel" before any content is described.

**Elements to Consider:**
* **Medium:** Is it live-action, 2D animation, 3D CGI, claymation, watercolor,
  etc.?
* **Artistic Style:** What is the visual language? (e.g., photorealistic,
  hyper-stylized, anime, Art Deco, impressionistic).
* **Quality & Influences:** Reference specific studios, artists, or benchmark
  productions (e.g., "in the style of a major animation studio," "quality of a
  professional nature documentary," "inspired by the work of a distinctive
  indie film director").
* **Texture & Fidelity:** Describe the surface details (e.g., "detailed clay
  with visible tool marks," "hyperrealistic skin pores and fabric weaves,"
  "clean vector lines with no gradients").
* **Motion & Frame Rate:** Specify the feel of the movement (e.g., "smooth
  60fps motion," "classic 24fps cinematic feel," "choppy 12fps stop-motion
  effect," "dramatic slow-motion").

---

#### **[SECTION 2: PRIMARY SUBJECT & ACTION]**

**Purpose:** To clearly identify the main character, object, or element that
serves as the scene's anchor. This is who or what the audience should focus on
first.

**Elements to Consider:**
* **Subject Identity:** Who or what is it? (e.g., "A weathered astronaut,"
  "a gleaming new electric car," "a single droplet of rain").
* **Key Features:** Describe its most important visual characteristics (e.g.,
  "tattered suit with a cracked helmet visor," "iridescent pearl-white paint
  job," "refracting the light around it").
* **Action / Pose:** What is the subject actively doing, or what is its current
  state? (e.g., "planting a flag on a dusty surface," "speeding down a coastal
  highway," "hanging from the tip of a leaf").
* **Position in Frame:** Where is the subject located? (e.g., "center-frame,"
  "occupying the left third of the screen," "emerging from the foreground").

---

#### **[SECTION 3: SECONDARY SUBJECT / FOCAL POINT]**

**Purpose:** To define the object of the primary subject's attention, the
element it's interacting with, or a secondary element that balances the
composition and adds narrative depth.

**Elements to Consider:**
* **Object Identity:** What is the secondary point of interest? (e.g., "a
  mysterious alien artifact," "a futuristic charging station," "the puddle on
  the ground below").
* **Relationship to Primary:** How does it connect to the primary subject?
  (e.g., "the destination of the car," "the object of the astronaut's
  discovery," "the target of the falling droplet").
* **State & Detail:** Describe its condition and appearance relative to the
  primary subject (e.g., "glowing with an internal light," "sleek and
  metallic," "rippling as the droplet is about to hit").

---

#### **[SECTION 4: ENVIRONMENT & SETTING]**

**Purpose:** To build the world around the subjects, providing context, scale,
and atmosphere. This section describes everything that isn't the primary or
secondary subject.

**Constraint:** Each scene must be confined to a SINGLE location/setting. Do
not describe a sequence of locations within one scene.

**Elements to Consider:**
* **Location:** Where is this scene taking place? (e.g., "lunar surface," "a
  sun-drenched Mediterranean coast," "a macro view of a lush forest floor").
* **Time of Day & Weather:** (e.g., "harsh midday sun," "pre-dawn twilight
  with heavy fog," "during a torrential downpour at night").
* **Background & Foreground Elements:** What else populates the scene? (e.g.,
  "distant Earth in the black sky," "craggy cliffs and azure water,"
  "out-of-focus moss and ferns").
* **Branding/Signage (for ads):** If applicable, describe the placement,
  appearance, and integration of any logos, brand colors, or specific products
  (e.g., "A billboard in the background displays a generic brand logo," "The
  characters are wearing vests with a discreet, embroidered brand symbol").

---

#### **[SECTION 5: CINEMATOGRAPHY & LIGHTING]**

**Purpose:** This is the "director's" section. It dictates precisely how the
scene is framed, shot, and lit to guide the viewer's eye and evoke a specific
feeling.

**Elements to Consider:**
* **Shot Type & Angle:** How is the scene being viewed? (e.g., "Wide
  establishing shot from a high angle," "Over-the-shoulder tracking shot,"
  "Extreme close-up from a low angle," "Point-of-view (POV) shot").
* **Lens & Focus:** Describe the camera's optical properties. (e.g., "Shot on
  a wide-angle 24mm lens to emphasize scale," "Using a telephoto lens to
  compress the background," "Shallow depth of field with a wide aperture like
  `$f/1.8$` to isolate the subject, creating soft bokeh in the background").
* **Composition:** How are the elements arranged in the frame? (e.g., "Rule of
  thirds," "strong leading lines," "symmetrical framing," "dynamic Dutch
  angle").
* **Lighting Scheme:** Describe the source, quality, and color of the light.
  (e.g., "Dramatic backlighting creating a silhouette," "Soft, diffuse light
  from an overcast sky," "High-contrast, low-key lighting with hard shadows
  (chiaroscuro)," "Motivated lighting from in-scene sources like neon signs or
  a fireplace").
* **Color Grading:** Define the overall color palette and tone (e.g., "Warm,
  golden-hour tones," "cool, desaturated blues and grays," "vibrant,
  high-saturation commercial look").

---

#### **[SECTION 6: MOOD & ATMOSPHERE]**

**Purpose:** To provide a final, definitive statement on the emotional core of
the scene. This acts as a unifying guide for all the preceding elements.

**Elements to Consider:**
* **Core Emotion:** What is the primary feeling the viewer should experience?
  (e.g., "Nostalgic and heartwarming," "tense and suspenseful," "awe-inspiring
  and majestic," "energetic and optimistic").
* **Pace & Energy:** What is the rhythm of the scene? (e.g., "serene and
  contemplative," "fast-paced and chaotic," "powerful and deliberate").
* **Sensory Descriptors:** Use words that evoke senses beyond sight (e.g.,
  "the feeling of crisp, cold air," "the oppressive humidity of a jungle," "the
  quiet warmth of a cozy room").
"""
