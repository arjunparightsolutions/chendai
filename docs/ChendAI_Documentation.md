# ChendAI Documentation 🥁
**Right Solutions by Arjun P A**

## 🧬 Helix-Harmony Mode Explained

### Concept
Helix-Harmony Mode treats musical instruments as biological entities defined by their "DNA". This DNA is a set of acoustic parameters that define the instrument's unique sonic signature.

### Instrument DNA Files
Located in the root directory, these files are the genetic code of the orchestra:

#### 1. `chendadna.txt` (The King of Rhythm)
- **Genes**: 
  - `frequency`: 70-120Hz (Base pitch of the Valam Thala)
  - `harmonics`: [1.0, 1.4, 2.1, 2.8] (Overtone series acting like DNA strands)
  - `decay`: 0.3-0.8s (Resonance duration)
  - `texture`: granular noise (Simulates skin friction)

#### 2. `illathalamdna.txt` (The Metallic Pulse)
- **Genes**:
  - `inharmonicity`: High (Creates the shimmering metallic crash)
  - `phase_offset`: 2-5ms (Time difference between two cymbals hitting)

#### 3. `sideinstrumentsdna.txt` (The Melodic Soul)
- **Genes**:
  - `kuzhal_waveform`: Sawtooth (Nasal, piercing tone)
  - `kombu_waveform`: Pulse (Brass-like projection)

---

## 🛠️ Technical Architecture

### 1. AI Composer (The Brain)
- **Engine**: OpenAI GPT-4o-mini
- **Role**: Analyzing natural language beat requests (e.g., "slow kathakali padam") and converting them into a JSON-based musical score.
- **Output**: A sequence of events `{ instrument: "chenda", velocity: 0.8, time: 0.0 }`.

### 2. Genetic Synthesizer (The Heart)
- **Engine**: Custom Python Wave Synthesis
- **Process**: 
  1. Reads the "DNA" of the requested instrument.
  2. Generates the raw waveform based on genetic parameters.
  3. Applies "Physics-Based Modeling" (pitch bending, envelope shaping).
  4. Renders the audio sample.

### 3. Audio Mixing Engine
- **Engine**: NumPy & SciPy
- **Process**: Blends all synthesized stems into a final stereo mix (44.1kHz WAV).

---

## 🔒 License & Usage

**Project Owner**: Arjun P A (Right Solutions)
**License Type**: Viewing & Research Only

- You **CAN** read this code to understand the Helix-Harmony approach.
- You **CANNOT** use this code to build a commercial product.
- You **CANNOT** distribute this code without permission.

---

## 📞 Support

For research collaboration or inquiries:
**Arjun P A**
Email: [rightsolutionsarjun@gmail.com](mailto:rightsolutionsarjun@gmail.com)
Phone: +91 9495988525
