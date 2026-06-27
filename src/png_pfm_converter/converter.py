import struct
from pathlib import Path

import numpy as np
from PIL import Image


def png_to_pfm(png_path: str | Path, pfm_path: str | Path) -> None:
    img = Image.open(png_path)

    if img.mode == "RGBA":
        img = img.convert("RGB")

    is_grayscale = img.mode == "L"
    if not is_grayscale and img.mode != "RGB":
        img = img.convert("RGB")

    arr = np.asarray(img, dtype=np.float32) / 255.0

    _write_pfm(pfm_path, arr)


def pfm_to_png(pfm_path: str | Path, png_path: str | Path) -> None:
    arr = _read_pfm(pfm_path)

    clipped = np.clip(arr, 0.0, 1.0)
    pixels = (clipped * 255.0 + 0.5).astype(np.uint8)

    if pixels.ndim == 2:
        img = Image.fromarray(pixels, mode="L")
    else:
        img = Image.fromarray(pixels, mode="RGB")

    img.save(png_path)


def _write_pfm(path: str | Path, arr: np.ndarray) -> None:
    """Write a float32 HxW or HxWx3 array as a PFM file (little-endian)."""
    if arr.ndim == 2:
        tag = "Pf"
    elif arr.ndim == 3 and arr.shape[2] == 3:
        tag = "PF"
    else:
        raise ValueError(f"Unsupported array shape for PFM: {arr.shape}")

    h, w = arr.shape[:2]

    # PFM stores rows bottom-to-top
    flipped = np.flipud(arr).astype(np.float32)

    with open(path, "wb") as f:
        f.write(f"{tag}\n{w} {h}\n-1.0\n".encode("ascii"))
        f.write(flipped.tobytes())


def _read_pfm(path: str | Path) -> np.ndarray:
    """Read a PFM file and return a float32 array (HxW or HxWx3), rows top-to-bottom."""
    with open(path, "rb") as f:
        tag = f.readline().decode("ascii").strip()
        if tag not in ("PF", "Pf"):
            raise ValueError(f"Not a PFM file (got tag '{tag}')")

        w, h = map(int, f.readline().decode("ascii").split())
        scale = float(f.readline().decode("ascii").strip())

        little_endian = scale < 0
        channels = 3 if tag == "PF" else 1

        data = np.frombuffer(f.read(), dtype=np.float32)

        if not little_endian:
            data = data.byteswap()

        if channels == 1:
            arr = data.reshape(h, w)
        else:
            arr = data.reshape(h, w, channels)

    # PFM is stored bottom-to-top; flip to top-to-bottom
    return np.flipud(arr)
