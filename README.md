# 🧠 FocusMode - Distraction Killer + Timeboxer

A terminal-native productivity booster that blocks distracting apps and websites while locking you into focused work sessions.

---

## 🔥 Features

* ⏳ Timeboxed focus sessions (`--duration`)
* 🛑 Kills and re-kills distracting apps during session (`--block`)
* 🌐 Temporarily blocks websites via `hosts` file (`--websites`)
* 🔒 Strict mode prevents early exit (`--strict`)
* 📜 Logs sessions to `.focus_history.json` (`--log-history`)
* 📊 Weekly analytics summary (`--summary`)
* 🧠 Terminal-native, no GUI bloat

---

## 🚀 Usage

### 🔧 Install Requirements

```bash
pip install rich
```

### 🧪 Start a Focus Session

```bash
python focusmode.py --duration 45 --block chrome discord --websites youtube.com reddit.com --log-history
```

### ⛔ Strict Mode (Prevents Ctrl+C skip)

```bash
python focusmode.py --duration 30 --block steam whatsapp --strict
```

### 📈 Weekly Summary

```bash
python focusmode.py --summary
```

---

## ✅ Example

```bash
# 25 minute focus with app & site block
python focusmode.py --duration 25 \
  --block chrome discord spotify \
  --websites youtube.com reddit.com \
  --strict --log-history
```

---

## 🔍 File Overview

| File                  | Purpose                                     |
| --------------------- | ------------------------------------------- |
| `focusmode.py`        | Main CLI app                                |
| `.focus_history.json` | Session history log                         |
| `hosts` file          | System-level site blocking (requires admin) |

---

## ⚠️ Notes

* To block websites, you **must run as administrator/root**
* Only apps listed in the internal map can be blocked
* Doesn’t prevent manual re-opening of apps *unless running watchdog* (already included)

---

