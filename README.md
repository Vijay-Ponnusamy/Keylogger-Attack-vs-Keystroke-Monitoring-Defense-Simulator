# Keylogger Attack vs Keystroke Monitoring Defense Simulator
## Cyber Range as a Service — Activity 2

### Overview
A GUI-based Python simulation of keylogger attack techniques competing against
multi-layer keystroke monitoring defenses. Built for educational purposes as part
of the Cyber Range concept where attack and defense scenarios run in a sandboxed environment.

---

### Features

#### Attack Module
| Mode | Description | Severity |
|---|---|---|
| Kernel-Level Hook | OS-level keystroke interception | CRITICAL |
| User-Space Hook | SetWindowsHookEx simulation | HIGH |
| API Polling | GetAsyncKeyState rapid polling | MEDIUM |
| Acoustic Attack | Side-channel sound analysis | LOW |
| Form Grabbing | Browser form-submit interception | HIGH |

#### Defense Module
| Layer | Technique | Efficacy |
|---|---|---|
| Anomaly Detection | ML-based typing rhythm analysis | 85% |
| Process Hooking Guard | Hook injection detection | 90% |
| API Call Monitoring | Suspicious syscall tracking | 75% |
| Honeypot Keystrokes | Decoy credential traps | 70% |
| Kernel Integrity Check | IDT/SSDT tampering detection | 95% |

---

### Requirements
```
Python 3.8+
tkinter (included in standard library)
No external pip packages required
```

### Run
```bash
python main.py
```

### Usage
1. Select an **Attack Mode** from the dropdown
2. Enable one or more **Defense Layers** using the checkboxes
3. Click **LAUNCH ATTACK** to start the attacker simulation
4. Click **START DEFENSE** to activate the monitoring engine
5. Observe real-time feeds in all three panels
6. Click **Run Defense Analysis** for a risk report
7. Click **Export Log** to save a JSON session report

---

### Project Structure
```
keylogger_simulator/
├── main.py          # Complete GUI application
└── README.md        # This file
```

### Disclaimer
This project is **strictly educational**. All "keylogging" is fully simulated
using random data generation — no actual system keystrokes are captured.
This tool demonstrates attack concepts for awareness and defense training only.
