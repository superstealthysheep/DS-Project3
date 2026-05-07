import io
import functools

CSI = "\033["
RESET = CSI+"0m"
BOLD = CSI+"1m"
ITALIC = CSI+"3m"
UNDERLINE = CSI+"4m"

def get_color(color, background=False, bright=False):
    base = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'default'].index(color)
    assert base in range(10)
    return f"{CSI}{30 + base + 10*background + 60*bright}m"

def format_print(*args, color=None, bold=None, italic=None, underline=None, **kwargs):
    so = io.StringIO()

    pre_args = []
    if color is not None:
        pre_args.append(get_color(color))
    if bold: pre_args.append(BOLD)
    if italic: pre_args.append(ITALIC)
    if underline: pre_args.append(UNDERLINE)
    post_args = [RESET] if pre_args else []

    new_kwargs = {k:v for k,v in kwargs.items() if k != 'file'}
    print(*args, file=so, **new_kwargs)
    s = "".join([*pre_args, so.getvalue(), *post_args])
    print(s, **kwargs)

@functools.lru_cache(32)
def format_string(*args, **kwargs):
    so = io.StringIO()
    format_print(*args, file=so, end="", **kwargs)
    return so.getvalue()

def info(*args, **kwargs):
    print(format_string("[INFO]", color="yellow", bold=True), *args, **kwargs)

def warn(*args, **kwargs):
    print(format_string("[WARN]", color="red", bold=True), *args, **kwargs)

if __name__ == "__main__":
    # format_print("hello world", color="red", bold=True, underline=True, italic=True)
    # print(format_string("[WARN]", color="red", bold=True))
    info("info test")
    warn("warn test")