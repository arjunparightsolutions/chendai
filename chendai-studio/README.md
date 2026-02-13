# ChendAI Studio - Professional Kerala Percussion DAW

![ChendAI Studio](https://img.shields.io/badge/Version-2.0-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-cyan)

**ChendAI Studio** is a professional Digital Audio Workstation (DAW) for generating and editing traditional Kerala percussion music using AI-powered composition and advanced spectral synthesis.

## 🚀 Quick Start

### Installation

1. **Install Python 3.8+** from [python.org](https://python.org/downloads)

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API key** (for AI composition):
```bash
# Create .env file
echo OPENAI_API_KEY=your_api_key_here > .env
```

### Running the Application

```bash
python chendai_studio_gui.py
```

## ✨ Features

### 🎼 AI-Powered Composition
- **Natural Language Mode**: Describe music in plain text
- **Pattern Mode**: Choose from traditional styles:
  - 🥁 Panchari Melam (Temple)
  - ⚡ Pandi Melam (Powerful)
  - 🎯 Thayambaka (Solo)
  - 🎺 Panchavadyam (5 Instruments)
- **5 Orchestration Strategies**: Traditional, Dynamic, Unison, Antiphonal, Layered

### 🎛️ Professional DAW Interface
- **3-Panel Layout**: Controls | Timeline | Mixer
- **6-Player Ensemble**: 3 Chenda + 2 Elathaalam + 1 Kombu
- **Real-time Mixer**: Individual channel faders, pan, solo/mute
- **Audio Playback**: Integrated transport controls

### 🎨 Advanced Synthesis
- **Spectral Synthesis**: 5000 acoustic signatures
- **Material Physics**: Authentic stick-impact modeling
- **Spatial Audio**: Stereo positioning simulation
- **Modal Synthesis**: Metal instrument resonance

## 📦 System Requirements

- **OS**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB for application + generated audio
- **Audio**: Sound card with stereo output

## 🎯 Usage Guide

### 1. Pattern-Based Generation
1. Select a pattern style from dropdown
2. Set duration (5-300 seconds)
3. Choose orchestration strategy
4. Click **✨ Generate Music**

### 2. Natural Language Generation
1. Enable "Natural Language Mode" checkbox
2. Describe the music you want:
   ```
   Generate a traditional BGM for Kerala with chenda and 
   cymbals, energetic temple festival atmosphere...
   ```
3. Click **✨ Generate Music**

### 3. Playback
- **Play/Pause**: ▶/⏸ button
- **Stop**: ⏹ button
- **Progress**: Time display shows current position

### 4. Mixer Controls
- **Volume Fader**: Vertical slider (0-100%)
- **Pan**: Horizontal slider (L50 ← C → R50)
- **Solo**: Isolate single channel
- **Mute**: Silence channel

## 🛠️ Project Structure

```
a:\chendai\
├── chendai_studio_gui.py       # Main application entry
├── chendai_6player.py          # Audio engine
├── ai_composer.py              # AI composition
├── ensemble_mixer.py           # Mixing & rendering
├── spectral_engine.py          # Synthesis
├── ui/
│   ├── main_window.py          # Main window
│   ├── audio_worker.py         # Background generation
│   ├── widgets/
│   │   ├── control_panel.py    # Composition controls
│   │   ├── mixer_panel.py      # Mixer interface
│   │   ├── waveform_widget.py  # Visualization
│   │   └── transport.py        # Playback controls
│   └── styles/
│       └── dark_theme.qss      # Application theme
├── requirements.txt            # Dependencies
└── output/                     # Generated audio files
```

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Install all dependencies: `pip install -r requirements.txt`
- Check console for error messages

### Audio engine initialization failed
- Verify all audio libraries are installed
- Check that `chenda_master_db.json` exists
- Ensure sufficient RAM (4GB minimum)

### No audio playback
- Install pygame: `pip install pygame`
- Check system audio settings
- Verify audio output device is available

### Generation fails
- Set `OPENAI_API_KEY` in `.env` file
- Check internet connection for AI features
- Verify API key is valid

## 📝 Changelog

### v2.0 (Current)
- ✅ Replaced Electron with native PyQt5 UI
- ✅ Direct Python integration (no HTTP server)
- ✅ Background generation with progress dialog
- ✅ Pygame-based audio playback
- ✅ Professional dark theme with glassmorphism
- ✅ Comprehensive error handling
- ✅ 75% reduction in memory usage

### v1.0
- Initial Electron/React version
- Basic 6-player ensemble
- AI composition with OpenAI
- Spatial audio mixing

## 📄 License

Copyright © 2026 Right Solutions A.I

## 🙏 Acknowledgments

- Traditional Kerala percussion artists
- OpenAI GPT-4 for AI composition
- PyQt5 community
- Pygame audio library

## 📧 Support

For issues and feature requests, check the console output or contact support.

---

**Made with ❤️ for preserving Kerala's musical heritage through AI**
