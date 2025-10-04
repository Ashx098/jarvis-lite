# Minimal sandbox: no imports, only math ops, limited builtins


def calc(expr: str):
    allowed_names = {k: __builtins__[k] for k in ("abs","round")}
    return eval(expr, {"__builtins__": None}, allowed_names)