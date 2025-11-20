def input_angka(prompt, tipe=float) -> float | int:
    """
    Inputan angka dengan tipe berubah-ubah
    :param prompt:
    :param tipe:
    :return float | int:
    """
    while True:
        nilai = input(prompt).strip()
        try:
            return tipe(nilai)
        except (ValueError, AttributeError):
            print("Input harus angka, coba lagi.\n")


def display(value, fallback="-"):
    return value if value is not None else fallback


def input_optional(prompt: str, default: str | None = None) -> str | None:
    """
    Input string, kalau user kosongin (Enter), balikin default.
    """
    val = input(prompt).strip()
    return val if val else default