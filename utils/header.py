import shutil
import subprocess
import sys

TITLE_TEXT = "LABULIS"
SUBTITLE = "Analisis Kesesuaian Tanaman (Iklim • Tanah • Ketinggian)"


def ensure_pyfiglet():
    try:
        import pyfiglet
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfiglet", "--quiet"])
            import pyfiglet
            return True
        except Exception:
            return False


def center_line(s: str, width: int) -> str:
    s = s.rstrip("\n")
    if len(s) >= width:
        return s
    pad = (width - len(s)) // 2
    return " " * pad + s


def make_border(width: int) -> str:
    seg = "─" * max(2, width - 10)
    line = f"  9e  {seg}  9e  "
    return (line[:width]) if len(line) >= width else center_line(line, width)


def frame_block(lines, width):
    width = max(width, 20)
    top = "╭" + "─" * (width - 2) + "╮"
    bottom = "╰" + "─" * (width - 2) + "╯"
    body = []
    for ln in lines:
        ln = ln.rstrip("\n")
        pad = width - 2 - len(ln)
        body.append("│" + ln + " " * max(0, pad) + "│")
    return [top] + body + [bottom]


def render(width: int = 100) -> str:
    width = max(80, width)
    out = [make_border(width), ""]

    if ensure_pyfiglet():
        from pyfiglet import Figlet
        fig = Figlet(font="ansi_shadow")
        title = fig.renderText(TITLE_TEXT).rstrip("\n").splitlines()
    else:
        title = [
            r"  _          _           _     _ _     ",
            r" | |        | |         | |   (_) |    ",
            r" | |     ___| |__  _   _| |__  _| |___ ",
            r" | |    / _ \ '_ \| | | | '_ \| | / __|",
            r" | |___|  __/ |_) | |_| | |_) | | \__ \ ",
            r" |______\___|_.__/ \__,_|_.__/|_|_|___/ ",
        ]

    # cetak judul terpusat
    for ln in title:
        out.append(center_line(ln, width))

    # garis dekorasi tengah + subtitle
    out.append("")
    out.append(center_line(make_border(min(width, 90)), width))
    out.append(center_line(SUBTITLE, width))
    out.append("")

    return "\n".join(out)


def header():
    try:
        width = shutil.get_terminal_size().columns
    except Exception:
        width = 100
    print(render(width))
