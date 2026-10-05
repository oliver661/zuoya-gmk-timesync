# Zuoya GMK Time Sync

[简体中文](README-zh_CN.md)

Sync the clock on the screen of a **ZUOYA GMK67-S** keyboard from macOS, without the vendor's Windows-only "Image Custom Tool".

It should also work with the **ZUOYA GMK87**, which uses the same USB IDs and protocol.

## Requirements

- macOS (Linux should also work through hidapi, but it hasn't been tested)
- Python 3
- [hidapi](https://pypi.org/project/hidapi/) Python bindings

```bash
pip3 install hidapi
```

## Usage

Connect the keyboard with a USB cable, then run:

```bash
python3 timesync.py
```

Expected output:

```
Synced keyboard clock to 2026-10-05 13:18:13
```

The script uses the Mac's local time. It doesn't need root, drivers, or detaching the keyboard, and the keyboard keeps working while it runs.

## Connection modes

| Mode | Status |
| --- | --- |
| USB cable | Tested and working |
| 2.4 GHz dongle | Untested. It may work if the dongle exposes the same vendor HID interface (usage page `0xFF1C`). |
| Bluetooth | Not supported. Over Bluetooth, macOS only sees the standard keyboard interfaces, not the vendor interface. |

If the script can't find the vendor interface, it exits with:

```
GMK67-S vendor interface not found (connect via USB cable or 2.4G dongle)
```

## How it works

The keyboard (VID `0x320F`, PID `0x5055`) has a vendor HID interface on usage page `0xFF1C`, usage `0x92` (interface 3). Every command is a 64-byte output report:

| Byte | Meaning |
| --- | --- |
| 0 | Report ID `0x04` |
| 1–2 | Checksum: little-endian 16-bit sum of bytes 3–62 |
| 3 | Command ID |
| 4 | Data length |
| 5–7 | Offset (24-bit, little-endian) |
| 8– | Data |

The keyboard answers each command with a report that repeats bytes 0–2 of the command.

Sync sequence:

1. Load the config: command `1` (start), command `3` ×10, command `2` (end), then command `5` ×12 to read the 48-byte config, 4 bytes at a time.
2. Write the current time into config offset 35 as 7 bytes: second, minute, hour (BCD), weekday (1 = Monday … 7 = Sunday), then day, month, and year − 2000 (BCD).
3. Write the config back: command `1`, command `6` with the 48 bytes, command `2`.

## Credits

The protocol comes from [rusq/kbdctl](https://github.com/rusq/kbdctl), which is based on Jochen Eisinger's `zuoya_gmk87.py` (BSD license).

## Disclaimer

This is an unofficial tool and is not affiliated with ZUOYA. It writes to the keyboard's configuration memory. Use it at your own risk.
