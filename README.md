# Microfluidic Lab-on-a-Chip & Robotic Optical Tweezer Cell Sorter

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)
![Domain](https://img.shields.io/badge/Domain-BioInstrumentation--Robotics-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An interactive **Bio-Instrumentation & Physics Simulation** combining microfluidic hydrodynamics, optical physics, and robotic automation. This project simulates automated **Circulating Tumor Cell (CTC)** isolation using a **Galvo-driven Optical Tweezer** system on a microfluidic Lab-on-a-Chip platform.

---

## 📌 Technical Highlights

- 🧬 **Bioscience & Diagnostics**:
  - High-purity single-cell sorting of fluorescently tagged target cells (e.g., Circulating Tumor Cells) from normal cell populations.
  - Dual-output junction separating normal cells into the **Waste Outlet** and CTCs into the **Harvest Chamber**.
- ⚡ **Microfluidic Hydrodynamics & Physics**:
  - **Poiseuille Flow Profile**: Simulates parabolic velocity distribution across microchannel cross-sections.
  - **Creeping Laminar Flow**: Operates at ultra-low Reynolds numbers (Re ≈ 0.025) dominated by viscous forces.
  - **Stokes Drag Resistance**: Real-time fluid damping modeling on cell kinematics.
- 🎯 **Robotic Optical Tweezers**:
  - **Galvo Scanner Automation**: Real-time closed-loop optical gradient force actuation (32.0 – 48.5 pN) redirecting target cells without mechanical contact.
  - **Piconewton Optical Trapping**: Precision laser manipulation at the cellular scale.
- 📊 **Cyber-Lab Analytics Dashboard**:
  - Real-time oscilloscope chart tracking harvest purity history over time.
  - Population composition ratio monitoring via live donut charts.
  - Live hydrodynamic parameters display (Reynolds number, Wall Shear Stress, Trap Stiffness).

---

## 🛠️ Tech Stack & Concepts

- **Language**: Python 3.x
- **Simulation & GUI**: Pygame
- **Core Principles**: Microfluidics, Optical Physics, Closed-Loop Automation, Real-Time Data Analytics

---

## 🎮 Controls & Interactive UI

| Control | Function |
| :--- | :--- |
| `[SPACE]` / **UI Button** | Toggle Automated Galvo-Laser Trapping Mode |
| `[Left Click Inlet]` / **Button** | Manually inject target CTC cell into the fluidic stream |
| `[C]` / **UI Button** | Reset analytics, cell counters, and purity history |
| `[ESC]` | Exit application |

---

## 🚀 Quick Start

```bash
pip install pygame
python microfluidic_cell_sorter.py
