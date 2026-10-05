#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright 2025 Jochen Eisinger
# Copyright 2026 oliver661 <oliver661@gmail.com>
# Ported from rusq/kbdctl (https://github.com/rusq/kbdctl), itself based on
# Jochen Eisinger's zuoya_gmk87.py. See LICENSE for the full license text.
"""Sync the ZUOYA GMK67-S (and GMK87, VID 0x320F / PID 0x5055) screen clock from macOS.

Requires: pip install hidapi
Works over USB cable, and over the 2.4GHz dongle if it exposes the same vendor interface.
"""
import sys, time, datetime
import hid

VID, PID, USAGE_PAGE = 0x320F, 0x5055, 0xFF1C
DATE_OFFSET = 35


def open_dev():
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == USAGE_PAGE:
            h = hid.device()
            h.open_path(d["path"])
            return h
    sys.exit("GMK67-S vendor interface not found (connect via USB cable or 2.4G dongle)")


def cmd(h, cid, data=b"", pos=0):
    if cid == 2:
        time.sleep(0.1)
    b = bytearray(64)
    b[0] = 0x04
    b[3], b[4] = cid, len(data)
    b[5:8] = (pos & 0xFF, (pos >> 8) & 0xFF, (pos >> 16) & 0xFF)
    b[8:8 + len(data)] = data
    c = sum(b[3:63])
    b[1], b[2] = c & 0xFF, (c >> 8) & 0xFF
    h.write(bytes(b))
    deadline = time.time() + 2
    while time.time() < deadline:
        r = h.read(64, 2000)
        if r and bytes(r[:3]) == bytes(b[:3]):
            return bytes(r[4:])
    raise TimeoutError(f"no response to command {cid}")


def bcd(v):
    return (v // 10) << 4 | (v % 10)


def main():
    h = open_dev()
    t0 = time.time()
    cmd(h, 1)
    for i in range(9):
        cmd(h, 3, bytes(4), i * 4)
    cmd(h, 3, b"\x00", 36)
    cmd(h, 2)
    cfg = bytearray()
    for i in range(12):
        cfg += cmd(h, 5, bytes(4), i * 4)[:4]
    cfg = cfg[:48]

    t = datetime.datetime.now() + datetime.timedelta(seconds=(time.time() - t0) * 2)
    cfg[DATE_OFFSET:DATE_OFFSET + 7] = bytes([
        bcd(t.second), bcd(t.minute), bcd(t.hour), t.isoweekday(),
        bcd(t.day), bcd(t.month), bcd(t.year - 2000)])

    cmd(h, 1)
    cmd(h, 6, bytes(cfg), 0)
    cmd(h, 2)
    h.close()
    print("Synced keyboard clock to", t.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
