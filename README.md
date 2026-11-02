# EDC16U34 Reverse Engineering

Reverse-engineering notes, Ghidra scripts, and analysis tooling for the **Bosch EDC16U34** diesel ECU (VW/Seat/Audi 1.9 TDI PD, 2004–2010).

> **⚠️ Disclaimers**
> - This repo contains **no** Bosch firmware, decompiled code, or WinOLS Damos data.
> - You must supply your own legally-obtained binary and calibration files.
> - For research, education, and legitimate repair/tuning of vehicles you own.
> - Bosch firmware is copyrighted. Do not redistribute binaries or decompiled output.

## Quick Start

```bash
git clone https://github.com/<your-username>/edc16u34-re.git
cd edc16u34-re
pip install -r python_tools/requirements.txt