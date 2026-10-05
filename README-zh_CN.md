# Zuoya GMK 时间同步工具

[English](README.md)

在 macOS 上给 **ZUOYA GMK67-S** 键盘屏幕上的时钟对时，不再需要厂商只有 Windows 版的「Image Custom Tool」。

**ZUOYA GMK87** 的 USB ID 和协议跟它一样，应该也能用。

## 环境要求

- macOS（Linux 理论上也能通过 hidapi 运行，但没有测试过）
- Python 3
- [hidapi](https://pypi.org/project/hidapi/) 的 Python 绑定

```bash
pip3 install hidapi
```

## 使用方法

用 USB 线连接键盘，然后运行：

```bash
python3 timesync.py
```

成功时会输出：

```
Synced keyboard clock to 2026-10-05 13:18:13
```

脚本会把 Mac 的本地时间写进键盘。不需要 root 权限，不用装驱动，也不用断开键盘，运行期间键盘照常可以打字。

## 连接方式

| 方式 | 状态 |
| --- | --- |
| USB 有线 | 已测试，可用 |
| 2.4G 接收器 | 未测试。如果接收器也提供同一个厂商 HID 接口（usage page `0xFF1C`），应该可以用。 |
| 蓝牙 | 不支持。蓝牙模式下 macOS 只能看到普通键盘接口，看不到厂商接口。 |

找不到厂商接口时，脚本会退出并提示：

```
GMK67-S vendor interface not found (connect via USB cable or 2.4G dongle)
```

## 原理

键盘（VID `0x320F`，PID `0x5055`）有一个厂商自定义的 HID 接口：usage page `0xFF1C`，usage `0x92`（第 3 号接口）。每条命令都是一个 64 字节的 output report：

| 字节 | 含义 |
| --- | --- |
| 0 | Report ID `0x04` |
| 1–2 | 校验和：第 3–62 字节相加得到的 16 位值，小端序 |
| 3 | 命令 ID |
| 4 | 数据长度 |
| 5–7 | 偏移量（24 位，小端序） |
| 8– | 数据 |

键盘对每条命令都会回一个 report，开头 3 个字节（第 0–2 字节）跟发出的命令相同。

同步流程：

1. 读取配置：发送命令 `1`（开始）、命令 `3` ×10、命令 `2`（结束），再发送命令 `5` ×12，每次读 4 字节，一共读出 48 字节配置。
2. 从配置的第 35 字节开始写入当前时间，共 7 个字节：秒、分、时（BCD 编码），星期（1 = 周一 … 7 = 周日），日、月、年减 2000（BCD 编码）。
3. 写回配置：发送命令 `1`，再发送命令 `6` 写入 48 字节，最后发送命令 `2`。

## 致谢

协议来自 [rusq/kbdctl](https://github.com/rusq/kbdctl)，该项目基于 Jochen Eisinger 的 `zuoya_gmk87.py`（BSD 许可）。

## 许可证

[BSD 3-Clause](LICENSE)，保留了原作者 Jochen Eisinger 的版权声明。

## 免责声明

本工具为非官方工具，与 ZUOYA 没有关系。它会写入键盘的配置存储，使用风险请自行承担。
