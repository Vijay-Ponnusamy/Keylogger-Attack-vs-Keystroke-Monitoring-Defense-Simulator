"""
Keylogger Attack vs Keystroke Monitoring Defense Simulator
Cyber Range as a Service - Attack-Defense Simulation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import string
import datetime
import json
import hashlib
import re
from collections import deque, Counter

# ── Colours & Fonts ───────────────────────────────────────────────────────────
BG_DARK      = "#0d1117"
BG_PANEL     = "#161b22"
BG_CARD      = "#1c2128"
ACCENT_RED   = "#f85149"
ACCENT_GREEN = "#3fb950"
ACCENT_BLUE  = "#58a6ff"
ACCENT_AMBER = "#d29922"
ACCENT_PURPLE= "#bc8cff"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED   = "#8b949e"
BORDER       = "#30363d"

FONT_HEADER  = ("Consolas", 11, "bold")
FONT_BODY    = ("Consolas", 10)
FONT_SMALL   = ("Consolas", 9)
FONT_LOG     = ("Courier New", 9)


# ── Attack Engine ─────────────────────────────────────────────────────────────
class KeyloggerAttackEngine:
    ATTACK_MODES = {
        "Kernel-Level Hook": {
            "desc": "Simulates a kernel-level keystroke hook intercepting OS input",
            "severity": "CRITICAL", "stealth": 95, "detection_risk": 20,
        },
        "User-Space Hook": {
            "desc": "SetWindowsHookEx / Xlib hook at user-space level",
            "severity": "HIGH", "stealth": 70, "detection_risk": 55,
        },
        "API Polling": {
            "desc": "GetAsyncKeyState polling attack every 10 ms",
            "severity": "MEDIUM", "stealth": 50, "detection_risk": 75,
        },
        "Acoustic Attack": {
            "desc": "Keystroke sound pattern analysis (side-channel)",
            "severity": "LOW", "stealth": 90, "detection_risk": 10,
        },
        "Form Grabbing": {
            "desc": "Browser form-submit interception before encryption",
            "severity": "HIGH", "stealth": 85, "detection_risk": 35,
        },
    }
    SENSITIVE_PATTERNS = [
        (r"password[:\s=]+\S+",                               "PASSWORD"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "EMAIL"),
        (r"\b(?:\d[ -]?){13,16}\b",                           "CREDIT_CARD"),
        (r"\b\d{3}-\d{2}-\d{4}\b",                            "SSN"),
        (r"(?i)(?:api[_-]?key|token)[:\s=]+\S+",              "API_KEY"),
    ]

    def __init__(self):
        self.active = False;  self.mode = "User-Space Hook"
        self.captured_keys = [];  self.session_log = []
        self.exfil_attempts = 0;  self.bytes_stolen = 0
        self._lock = threading.Lock();  self.callbacks = {}

    def register_callback(self, ev, fn): self.callbacks[ev] = fn
    def _fire(self, ev, *a):
        if ev in self.callbacks: self.callbacks[ev](*a)

    def start_attack(self, mode=None):
        if mode: self.mode = mode
        self.active = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop_attack(self): self.active = False

    def _loop(self):
        samples = [
            "password=S3cr3t!", "user@example.com", "admin",
            "credit_card: 4111 1111 1111 1111", "Hello World",
            "git push origin main", "ssh root@192.168.1.1",
            "api_key=sk-ABCDEF123456", "sudo rm -rf /",
            "SELECT * FROM users WHERE id=1",
        ] + list(string.ascii_lowercase * 4)
        while self.active:
            time.sleep(random.uniform(0.3, 1.2))
            ks = random.choice(samples)
            ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            entry = {"time": ts, "data": ks, "mode": self.mode}
            with self._lock:
                self.captured_keys.append(entry)
                self.bytes_stolen += len(ks)
            for pat, label in self.SENSITIVE_PATTERNS:
                if re.search(pat, ks, re.IGNORECASE):
                    ex = {"time": ts, "type": label, "data": ks,
                          "hash": hashlib.md5(ks.encode()).hexdigest()[:8]}
                    with self._lock:
                        self.session_log.append(ex)
                        self.exfil_attempts += 1
                    self._fire("sensitive_captured", ex)
            self._fire("keystroke_captured", entry)

    def get_stats(self):
        with self._lock:
            return {"total_keystrokes": len(self.captured_keys),
                    "exfil_attempts": self.exfil_attempts,
                    "bytes_stolen": self.bytes_stolen, "mode": self.mode,
                    "stealth": self.ATTACK_MODES[self.mode]["stealth"],
                    "detection_risk": self.ATTACK_MODES[self.mode]["detection_risk"]}


# ── Defense Engine ────────────────────────────────────────────────────────────
class KeystrokeDefenseEngine:
    DEFENSE_LAYERS = {
        "Anomaly Detection":      {"desc": "ML-based typing rhythm analysis",        "efficacy": 85},
        "Process Hooking Guard":  {"desc": "Detect & terminate hook injection",       "efficacy": 90},
        "API Call Monitoring":    {"desc": "Monitor suspicious WinAPI / syscalls",    "efficacy": 75},
        "Honeypot Keystrokes":    {"desc": "Inject decoy credentials to trap logger", "efficacy": 70},
        "Kernel Integrity Check": {"desc": "Verify kernel structures for tampering",  "efficacy": 95},
    }

    def __init__(self, atk):
        self.atk = atk;  self.active_layers = set()
        self.alerts = deque(maxlen=200)
        self.blocked_count = 0;  self.detection_count = 0
        self._lock = threading.Lock();  self.callbacks = {}
        self._running = False

    def register_callback(self, ev, fn): self.callbacks[ev] = fn
    def _fire(self, ev, *a):
        if ev in self.callbacks: self.callbacks[ev](*a)

    def enable_layer(self, l):  self.active_layers.add(l)
    def disable_layer(self, l): self.active_layers.discard(l)

    def start_defense(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop_defense(self): self._running = False

    def _loop(self):
        tpl = {
            "Anomaly Detection": [
                "Irregular typing cadence - entropy spike 3.2s",
                "Inhuman keystroke interval (0.001ms) flagged",
                "Bot-pattern rhythm detected (Mahalanobis)",
            ],
            "Process Hooking Guard": [
                "Suspicious SetWindowsHookEx call intercepted",
                "Unknown DLL injection into explorer.exe blocked",
                "Ring-3 hook on keyboard device detected",
            ],
            "API Call Monitoring": [
                "GetAsyncKeyState called 840x/sec - above threshold",
                "ReadFile on /dev/input/event0 by untrusted process",
                "Suspicious NtUserGetRawInputData syscall sequence",
            ],
            "Honeypot Keystrokes": [
                "Honeypot credential 'admin/H0n3yP0t!' accessed!",
                "Decoy API key exfiltration attempt caught",
                "Trap SSN triggered - attacker endpoint logged",
            ],
            "Kernel Integrity Check": [
                "IDT hook detected - potential rootkit activity",
                "SSDT entry overwrite in ntoskrnl.exe found",
                "Driver callback chain tampered - remediating",
            ],
        }
        while self._running:
            time.sleep(0.5)
            if not self.atk.active: continue
            dr = self.atk.ATTACK_MODES[self.atk.mode]["detection_risk"]
            for layer in list(self.active_layers):
                eff = self.DEFENSE_LAYERS[layer]["efficacy"]
                if random.randint(1, 100) < min(99, dr + eff // 3) // 4:
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    alert = {"time": ts, "layer": layer,
                             "message": random.choice(tpl.get(layer, ["Threat detected"]))}
                    with self._lock:
                        self.alerts.appendleft(alert)
                        self.detection_count += 1
                    self._fire("alert", alert)
                    if random.randint(1, 100) < eff:
                        with self._lock: self.blocked_count += 1
                        self._fire("blocked", layer)

    def analyze(self):
        with self.atk._lock:
            keys = list(self.atk.captured_keys)
            logs = list(self.atk.session_log)
        freq = Counter(e["data"][:10] for e in keys)
        return {"total": len(keys), "sensitive": len(logs),
                "top": freq.most_common(5),
                "risk": min(100, len(logs) * 15 + len(keys) // 5)}

    def get_stats(self):
        with self._lock:
            return {"detections": self.detection_count, "blocks": self.blocked_count,
                    "active_layers": len(self.active_layers)}


# ── GUI ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cyber Range — Keylogger Attack vs Keystroke Defense Simulator")
        self.configure(bg=BG_DARK)
        # Start maximized so there's definitely room for all panels
        self.state("zoomed")

        self.atk = KeyloggerAttackEngine()
        self.dfs = KeystrokeDefenseEngine(self.atk)
        self.atk.register_callback("keystroke_captured", lambda e: self.after(0, self._on_ks, e))
        self.atk.register_callback("sensitive_captured", lambda e: self.after(0, self._on_sens, e))
        self.dfs.register_callback("alert",   lambda a: self.after(0, self._on_alert, a))
        self.dfs.register_callback("blocked", lambda l: self.after(0, self._on_block))

        self._build()
        self._tick_stats()

    # ── build all ─────────────────────────────────────────────────────────────
    def _build(self):
        self._topbar()
        self._statrow()
        self._panels()

    # ── top bar ───────────────────────────────────────────────────────────────
    def _topbar(self):
        f = tk.Frame(self, bg=BG_PANEL, height=48)
        f.pack(side="top", fill="x")
        f.pack_propagate(False)
        tk.Label(f, text="CYBER RANGE", font=("Consolas",13,"bold"),
                 fg=ACCENT_BLUE, bg=BG_PANEL).pack(side="left", padx=14, pady=10)
        tk.Label(f, text="Keylogger Attack  <->  Keystroke Defense Simulator",
                 font=FONT_BODY, fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left")
        tk.Label(f, text="LIVE", font=("Consolas",10,"bold"),
                 fg=ACCENT_GREEN, bg=BG_PANEL).pack(side="right", padx=14)
        self._clk = tk.Label(f, text="", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL)
        self._clk.pack(side="right", padx=6)
        self._tick_clock()

    def _tick_clock(self):
        self._clk.config(text=datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000, self._tick_clock)

    # ── stat row ──────────────────────────────────────────────────────────────
    def _statrow(self):
        wrap = tk.Frame(self, bg=BG_DARK)
        wrap.pack(side="top", fill="x", padx=8, pady=(5,2))
        specs = [
            ("KEYSTROKES CAPTURED", "0",  ACCENT_RED,   "v_ks"),
            ("SENSITIVE DATA HITS",  "0",  ACCENT_RED,   "v_sens"),
            ("DEFENSES ACTIVE",      "0",  ACCENT_GREEN, "v_def"),
            ("THREATS DETECTED",     "0",  ACCENT_AMBER, "v_det"),
            ("ATTACKS BLOCKED",      "0",  ACCENT_GREEN, "v_blk"),
            ("RISK SCORE",           "0%", ACCENT_RED,   "v_risk"),
        ]
        for i, (lbl, val, col, attr) in enumerate(specs):
            wrap.columnconfigure(i, weight=1)
            c = tk.Frame(wrap, bg=BG_CARD, highlightthickness=1,
                         highlightbackground=BORDER)
            c.grid(row=0, column=i, sticky="ew", padx=3, pady=2)
            tk.Label(c, text=lbl, font=("Consolas",7,"bold"),
                     fg=TEXT_MUTED, bg=BG_CARD).pack(pady=(5,0))
            v = tk.Label(c, text=val, font=("Consolas",18,"bold"),
                         fg=col, bg=BG_CARD)
            v.pack(pady=(0,5))
            setattr(self, attr, v)

    # ── three panels using PanedWindow for guaranteed sizing ──────────────────
    def _panels(self):
        # Use a PanedWindow – it guarantees each pane gets a real size on Windows
        pane = tk.PanedWindow(self, orient="horizontal", bg=BG_DARK,
                              sashwidth=4, sashrelief="flat",
                              handlesize=0)
        pane.pack(side="top", fill="both", expand=True, padx=8, pady=(0,8))

        # ── LEFT: attack
        left = tk.Frame(pane, bg=BG_CARD,
                        highlightthickness=1, highlightbackground=ACCENT_RED)
        pane.add(left, stretch="always", minsize=320)
        self._atk_panel(left)

        # ── CENTRE: defense
        mid = tk.Frame(pane, bg=BG_CARD,
                       highlightthickness=1, highlightbackground=ACCENT_GREEN)
        pane.add(mid, stretch="always", minsize=320)
        self._def_panel(mid)

        # ── RIGHT: log
        right = tk.Frame(pane, bg=BG_CARD,
                         highlightthickness=1, highlightbackground=ACCENT_BLUE)
        pane.add(right, stretch="always", minsize=280)
        self._log_panel(right)

    # ── attack panel ──────────────────────────────────────────────────────────
    def _atk_panel(self, f):
        self._section_hdr(f, "ATTACK MODULE - Keylogger Engine", ACCENT_RED)

        tk.Label(f, text="Attack Mode:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=10, pady=(4,0))
        self._mode_var = tk.StringVar(value="User-Space Hook")
        self._mode_cb = ttk.Combobox(f, textvariable=self._mode_var,
                                     values=list(KeyloggerAttackEngine.ATTACK_MODES.keys()),
                                     state="readonly", font=FONT_BODY)
        self._mode_cb.pack(fill="x", padx=10, pady=4)
        self._mode_cb.bind("<<ComboboxSelected>>", self._mode_changed)

        self._mode_desc = tk.Label(f, text="", font=FONT_SMALL,
                                   fg=TEXT_MUTED, bg=BG_PANEL,
                                   wraplength=300, justify="left", anchor="w")
        self._mode_desc.pack(fill="x", padx=10, pady=2)

        br = tk.Frame(f, bg=BG_CARD)
        br.pack(fill="x", padx=10, pady=2)
        self._lbl_sev  = tk.Label(br, text="", font=FONT_SMALL, bg=BG_CARD)
        self._lbl_stl  = tk.Label(br, text="", font=FONT_SMALL, bg=BG_CARD)
        self._lbl_det  = tk.Label(br, text="", font=FONT_SMALL, bg=BG_CARD)
        self._lbl_sev.pack(side="left", padx=(0,8))
        self._lbl_stl.pack(side="left", padx=(0,8))
        self._lbl_det.pack(side="left")
        self._refresh_mode()

        self._btn_atk = tk.Button(f, text="  LAUNCH ATTACK",
                                  font=FONT_HEADER, bg=ACCENT_RED, fg="white",
                                  relief="flat", cursor="hand2",
                                  command=self._toggle_attack)
        self._btn_atk.pack(fill="x", padx=10, pady=6, ipady=6)

        tk.Label(f, text="Live Keystroke Feed", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=10, pady=(4,0))
        self._feed_ks = scrolledtext.ScrolledText(
            f, height=10, bg="#0a0e14", fg=ACCENT_RED,
            font=FONT_LOG, relief="flat", state="disabled")
        self._feed_ks.pack(fill="both", expand=True, padx=10, pady=(2,4))

        tk.Label(f, text="Sensitive Data Exfiltrated", font=FONT_SMALL,
                 fg=ACCENT_AMBER, bg=BG_CARD).pack(anchor="w", padx=10)
        self._feed_ex = scrolledtext.ScrolledText(
            f, height=5, bg="#0a0e14", fg=ACCENT_AMBER,
            font=FONT_LOG, relief="flat", state="disabled")
        self._feed_ex.pack(fill="x", padx=10, pady=(2,10))

    # ── defense panel ─────────────────────────────────────────────────────────
    def _def_panel(self, f):
        self._section_hdr(f, "DEFENSE MODULE - Keystroke Monitor", ACCENT_GREEN)

        tk.Label(f, text="Enable Defense Layers:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=10, pady=(4,2))

        self._layer_vars = {}
        for layer, cfg in KeystrokeDefenseEngine.DEFENSE_LAYERS.items():
            row = tk.Frame(f, bg=BG_CARD)
            row.pack(fill="x", padx=10, pady=1)
            var = tk.BooleanVar(value=False)
            tk.Checkbutton(row, text=layer, variable=var,
                           font=FONT_SMALL, fg=TEXT_PRIMARY, bg=BG_CARD,
                           selectcolor=BG_DARK, activebackground=BG_CARD,
                           cursor="hand2",
                           command=lambda l=layer, v=var: self._toggle_layer(l, v)
                           ).pack(side="left")
            ec = ACCENT_GREEN if cfg["efficacy"] >= 85 else ACCENT_AMBER
            tk.Label(row, text=f"{cfg['efficacy']}%",
                     font=FONT_SMALL, fg=ec, bg=BG_CARD).pack(side="right")
            tk.Label(f, text="   " + cfg["desc"],
                     font=("Consolas",7), fg=TEXT_MUTED, bg=BG_CARD
                     ).pack(anchor="w", padx=12)
            self._layer_vars[layer] = var

        qr = tk.Frame(f, bg=BG_CARD)
        qr.pack(fill="x", padx=10, pady=5)
        tk.Button(qr, text="Enable All", font=FONT_SMALL,
                  bg=ACCENT_GREEN, fg="white", relief="flat", cursor="hand2",
                  command=self._enable_all
                  ).pack(side="left", expand=True, fill="x", ipady=4, padx=(0,2))
        tk.Button(qr, text="Disable All", font=FONT_SMALL,
                  bg=BG_PANEL, fg=TEXT_MUTED, relief="flat", cursor="hand2",
                  command=self._disable_all
                  ).pack(side="left", expand=True, fill="x", ipady=4)

        self._btn_def = tk.Button(f, text="  START DEFENSE",
                                  font=FONT_HEADER, bg="#1f6b35", fg="white",
                                  relief="flat", cursor="hand2",
                                  command=self._toggle_defense)
        self._btn_def.pack(fill="x", padx=10, pady=4, ipady=6)

        tk.Label(f, text="Defense Alerts", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=10, pady=(6,0))
        self._feed_al = scrolledtext.ScrolledText(
            f, height=12, bg="#0a0e14", fg=ACCENT_GREEN,
            font=FONT_LOG, relief="flat", state="disabled")
        self._feed_al.pack(fill="both", expand=True, padx=10, pady=(2,4))

        tk.Button(f, text="Run Defense Analysis",
                  font=FONT_SMALL, bg=ACCENT_BLUE, fg="white",
                  relief="flat", cursor="hand2",
                  command=self._run_analysis
                  ).pack(fill="x", padx=10, pady=(0,10), ipady=5)

    # ── log panel ─────────────────────────────────────────────────────────────
    def _log_panel(self, f):
        self._section_hdr(f, "SIMULATION LOG & REPORT", ACCENT_BLUE)

        self._log_txt = scrolledtext.ScrolledText(
            f, bg="#0a0e14", fg=TEXT_PRIMARY,
            font=FONT_LOG, relief="flat", state="disabled")
        self._log_txt.pack(fill="both", expand=True, padx=10, pady=(4,4))

        for tag, col in [("R", ACCENT_RED), ("G", ACCENT_GREEN),
                         ("B", ACCENT_BLUE), ("A", ACCENT_AMBER),
                         ("M", TEXT_MUTED)]:
            self._log_txt.tag_config(tag, foreground=col)

        self._log("B", "=" * 50)
        self._log("B", "  CYBER RANGE INITIALIZED")
        self._log("B", "  Keylogger Attack vs Keystroke Defense")
        self._log("B", "=" * 50)
        self._log("M", "  1. Choose Attack Mode (left panel)")
        self._log("M", "  2. Enable Defense Layers (centre)")
        self._log("M", "  3. Launch Attack  then  Start Defense")
        self._log("M", "  4. Click Run Analysis for risk report")
        self._log("B", "-" * 50)

        br = tk.Frame(f, bg=BG_CARD)
        br.pack(fill="x", padx=10, pady=(0,10))
        tk.Button(br, text="Reset Simulation",
                  font=FONT_SMALL, bg=ACCENT_AMBER, fg="white",
                  relief="flat", cursor="hand2", command=self._reset
                  ).pack(side="left", expand=True, fill="x", ipady=5, padx=(0,2))
        tk.Button(br, text="Export Log (JSON)",
                  font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_PRIMARY,
                  relief="flat", cursor="hand2", command=self._export
                  ).pack(side="left", expand=True, fill="x", ipady=5)

    # ── section header helper ─────────────────────────────────────────────────
    def _section_hdr(self, parent, title, color):
        tk.Label(parent, text=title, font=FONT_HEADER,
                 fg=color, bg=BG_CARD).pack(anchor="w", padx=10, pady=(8,2))
        tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=10, pady=(0,4))

    # ── mode helpers ──────────────────────────────────────────────────────────
    def _refresh_mode(self):
        cfg = KeyloggerAttackEngine.ATTACK_MODES[self._mode_var.get()]
        self._mode_desc.config(text=cfg["desc"])
        sc = {"CRITICAL": ACCENT_RED, "HIGH": "#e07b39",
              "MEDIUM": ACCENT_AMBER, "LOW": ACCENT_GREEN}
        self._lbl_sev.config(text=f"Severity: {cfg['severity']}",
                             fg=sc.get(cfg["severity"], TEXT_MUTED))
        self._lbl_stl.config(text=f"Stealth: {cfg['stealth']}%", fg=ACCENT_PURPLE)
        self._lbl_det.config(text=f"DetRisk: {cfg['detection_risk']}%", fg=ACCENT_AMBER)

    def _mode_changed(self, _=None):
        self.atk.mode = self._mode_var.get()
        self._refresh_mode()

    # ── attack controls ───────────────────────────────────────────────────────
    def _toggle_attack(self):
        if not self.atk.active:
            self.atk.start_attack(self._mode_var.get())
            self._btn_atk.config(text="  STOP ATTACK", bg="#6e1a18")
            self._mode_cb.config(state="disabled")
            self._log("R", f"[ATTACK] Launched: {self._mode_var.get()}")
        else:
            self.atk.stop_attack()
            self._btn_atk.config(text="  LAUNCH ATTACK", bg=ACCENT_RED)
            self._mode_cb.config(state="readonly")
            self._log("M", "[ATTACK] Stopped.")

    # ── defense controls ──────────────────────────────────────────────────────
    def _toggle_defense(self):
        if not self.dfs._running:
            if not self.dfs.active_layers:
                messagebox.showwarning("No Layers", "Enable at least one defense layer first.")
                return
            self.dfs.start_defense()
            self._btn_def.config(text="  STOP DEFENSE", bg="#6e3018")
            self._log("G", "[DEFENSE] Monitoring started.")
        else:
            self.dfs.stop_defense()
            self._btn_def.config(text="  START DEFENSE", bg="#1f6b35")
            self._log("M", "[DEFENSE] Stopped.")

    def _toggle_layer(self, layer, var):
        if var.get():
            self.dfs.enable_layer(layer)
            self._log("G", f"[LAYER+]  {layer}")
        else:
            self.dfs.disable_layer(layer)
            self._log("M", f"[LAYER-]  {layer}")

    def _enable_all(self):
        for l, v in self._layer_vars.items():
            v.set(True); self.dfs.enable_layer(l)
        self._log("G", "[DEFENSE] All layers enabled.")

    def _disable_all(self):
        for l, v in self._layer_vars.items():
            v.set(False); self.dfs.disable_layer(l)
        self._log("M", "[DEFENSE] All layers disabled.")

    # ── analysis ──────────────────────────────────────────────────────────────
    def _run_analysis(self):
        r = self.dfs.analyze()
        self._log("B", "\n" + "=" * 50)
        self._log("B", "  DEFENSE ANALYSIS REPORT")
        self._log("B", "=" * 50)
        self._log("A", f"  Keystrokes intercepted : {r['total']}")
        self._log("R", f"  Sensitive captures     : {r['sensitive']}")
        self._log("R", f"  Risk score             : {r['risk']}%")
        for p, c in r["top"]:
            self._log("M", f"    '{p}' x{c}")
        if r["risk"] >= 60:   self._log("R", "  HIGH RISK - strengthen defenses!")
        elif r["risk"] >= 30: self._log("A", "  MEDIUM RISK - monitor closely.")
        else:                 self._log("G", "  LOW RISK - defense is effective.")
        self._log("B", "=" * 50 + "\n")
        self.v_risk.config(text=f"{r['risk']}%")

    # ── reset / export ────────────────────────────────────────────────────────
    def _reset(self):
        if not messagebox.askyesno("Reset", "Stop all engines and clear simulation?"): return
        self.atk.stop_attack(); self.dfs.stop_defense()
        self.atk.__init__(); self.dfs.__init__(self.atk)
        self.atk.register_callback("keystroke_captured", lambda e: self.after(0, self._on_ks, e))
        self.atk.register_callback("sensitive_captured", lambda e: self.after(0, self._on_sens, e))
        self.dfs.register_callback("alert",   lambda a: self.after(0, self._on_alert, a))
        self.dfs.register_callback("blocked", lambda l: self.after(0, self._on_block))
        for w in (self._feed_ks, self._feed_ex, self._feed_al, self._log_txt):
            w.config(state="normal"); w.delete("1.0","end"); w.config(state="disabled")
        for v in self._layer_vars.values(): v.set(False)
        self._btn_atk.config(text="  LAUNCH ATTACK", bg=ACCENT_RED)
        self._btn_def.config(text="  START DEFENSE", bg="#1f6b35")
        self._mode_cb.config(state="readonly")
        self._log("B", "[SIM] Reset complete. Ready.")

    def _export(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"cyber_range_log_{ts}.json"
        data = {"timestamp": ts, "attack_mode": self.atk.mode,
                "attack_stats": self.atk.get_stats(), "defense_stats": self.dfs.get_stats(),
                "captured_keys": self.atk.captured_keys[-50:],
                "exfil_log": self.atk.session_log,
                "alerts": list(self.dfs.alerts)[:50]}
        try:
            with open(fn, "w") as fp: json.dump(data, fp, indent=2)
            messagebox.showinfo("Exported", f"Saved to:\n{fn}")
            self._log("B", f"[LOG] Exported: {fn}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── feed helpers ──────────────────────────────────────────────────────────
    def _on_ks(self, e):
        self._append(self._feed_ks,
                     f"[{e['time']}] {e['mode'][:14]:<14} | {e['data'][:55]}\n")

    def _on_sens(self, e):
        self._append(self._feed_ex,
                     f"[{e['time']}] {e['type']:<12} | {e['data'][:38]} md5:{e['hash']}\n")
        self._log("R", f"[EXFIL] {e['type']}: {e['data'][:40]}")

    def _on_alert(self, a):
        self._append(self._feed_al,
                     f"[{a['time']}] [{a['layer'][:18]:<18}] {a['message']}\n")
        self._log("G", f"[DETECT] {a['layer']}: {a['message'][:50]}")

    def _on_block(self):
        pass  # counter updated in engine; stats refresh handles display

    def _append(self, w, txt):
        w.config(state="normal"); w.insert("end", txt); w.see("end")
        w.config(state="disabled")

    def _log(self, tag, msg):
        self._log_txt.config(state="normal")
        self._log_txt.insert("end", msg + "\n", tag)
        self._log_txt.see("end")
        self._log_txt.config(state="disabled")

    # ── stat refresh ──────────────────────────────────────────────────────────
    def _tick_stats(self):
        a = self.atk.get_stats(); d = self.dfs.get_stats()
        self.v_ks.config(text=str(a["total_keystrokes"]))
        self.v_sens.config(text=str(a["exfil_attempts"]))
        self.v_def.config(text=str(d["active_layers"]))
        self.v_det.config(text=str(d["detections"]))
        self.v_blk.config(text=str(d["blocks"]))
        self.after(1000, self._tick_stats)


if __name__ == "__main__":
    app = App()
    style = ttk.Style(app)
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=BG_PANEL, background=BG_PANEL,
                    foreground=TEXT_PRIMARY, selectbackground=ACCENT_BLUE,
                    bordercolor=BORDER, arrowcolor=TEXT_MUTED)
    app.mainloop()
