# RF-Sense

**RF Signal Analysis & Interference Detection Platform**

RF-Sense is a Python-based project designed to simulate, analyze, and detect potential interference in synthetic radio-frequency (RF) signals.

The project explores digital signal processing (DSP), frequency-domain analysis, noise estimation, and interference detection through a modular software architecture.


## Project Objectives

- Generate and visualize synthetic signals with different frequencies and amplitudes.
- Analyze signals in the time and frequency domains using the Fast Fourier Transform (FFT).
- Simulate noise and interfering signals.
- Estimate signal-to-noise ratio (SNR).
- Detect significant frequency peaks using an adaptive threshold.
- Classify detected frequency components as expected signals or potential interference.
- Evaluate detection performance under different signal and noise conditions.


## Technologies

- **Python** - Core development language
- **NumPy** - Numerical computations and signal generation
- **Scipy FFT** - Frequency-domain analysis
- **Matplotlib** - Signal and spectrum visualization
- **Git & GitHub** - Version control


## Current Features

### 1. Signal Generation

Generates synthetic sinusoidal signals with configurable frequencies, amplitudes, sampling rates, and durations.

### 2. Frequency Spectrum Analysis

Uses the Fast Fourier Transform (FFT) to convert time-domain signals into frequency-domain representations and identify frequency components.


## Example Results

The following results were obtained using synthetic signals with an
expected frequency of 10 Hz and an interfering component at 30 Hz.

| Noise Level | Estimated Noise Floor | Adaptive Threshold | Detected Frequencies |
|---|---|---|---|
| 0.3 | 0.0154 | 0.0772 | 10 Hz, 30 Hz |
| 1.5 | 0.0772 | 0.3862 | 10 Hz, 30 Hz |
| 3.0 | 0.1545 | 0.7725 | 10 Hz, 30 Hz |

The detector identified both components in these three experiments.
Further testing is needed to evaluate detection reliability,
false positives, and false negatives.


## Project Structure

```text
RF-Sense/
├── src/
│   ├── signal_generator.py
│   ├── spectrum_analyzer.py
│   ├── noise_simulator.py
│   └── interference_detector.py
├── tests/
├── docs/
├── README.md
├── requirements.txt
└── .gitignore
```


## Getting Started

Clone the repository and navigate to the project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the current simulation and detection workflow:

```bash
python src/noise_simulator.py
```


## Development Roadmap

- [x] Phase 1 - Project Setup
- [x] Phase 2 - Signal Generation & FFT
- [x] Phase 3 - Noise & SNR Analysis
- [x] Phase 4 - Interference Detection
- [ ] Phase 5 - Testing & Evaluation
- [ ] Phase 6 - PyQt6 Graphical User Interface
- [ ] Phase 7 - System Integration
- [ ] Phase 8 - Final Documentation & GitHub Release


## Future Improvements

Planned improvements include automated testing, quantitative detection
metrics, additional interference scenarios, and an interactive PyQt6
graphical user interface.


## Project Status

**In Development - Phase 5: Testing & Evaluation**

RF-Sense is an educational engineering project using synthetic signals.
It is intended to demonstrate signal-processing and software-development
concepts, rather than operate as a validated real-world RF monitoring system.