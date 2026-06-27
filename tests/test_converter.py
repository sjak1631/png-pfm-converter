import numpy as np
import pytest
from PIL import Image

from png_pfm_converter.converter import _read_pfm, _write_pfm, pfm_to_png, png_to_pfm


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def make_png(path, mode="RGB", size=(4, 4)):
    rng = np.random.default_rng(42)
    if mode == "L":
        data = rng.integers(0, 256, size, dtype=np.uint8)
    else:
        data = rng.integers(0, 256, (*size, 3), dtype=np.uint8)
    Image.fromarray(data, mode=mode).save(path)
    return data


class TestRoundTrip:
    def test_rgb_png_pfm_png(self, tmp_dir):
        png_in = tmp_dir / "in.png"
        pfm = tmp_dir / "mid.pfm"
        png_out = tmp_dir / "out.png"

        orig = make_png(png_in, mode="RGB")
        png_to_pfm(png_in, pfm)
        pfm_to_png(pfm, png_out)

        result = np.asarray(Image.open(png_out))
        np.testing.assert_array_equal(orig, result)

    def test_gray_png_pfm_png(self, tmp_dir):
        png_in = tmp_dir / "in_gray.png"
        pfm = tmp_dir / "mid_gray.pfm"
        png_out = tmp_dir / "out_gray.png"

        orig = make_png(png_in, mode="L")
        png_to_pfm(png_in, pfm)
        pfm_to_png(pfm, png_out)

        result = np.asarray(Image.open(png_out))
        np.testing.assert_array_equal(orig, result)


class TestPfmIO:
    def test_write_read_rgb(self, tmp_dir):
        path = tmp_dir / "test.pfm"
        arr = np.random.default_rng(0).random((8, 6, 3), dtype=np.float32)
        _write_pfm(path, arr)
        loaded = _read_pfm(path)
        np.testing.assert_allclose(arr, loaded, atol=1e-6)

    def test_write_read_gray(self, tmp_dir):
        path = tmp_dir / "test_gray.pfm"
        arr = np.random.default_rng(1).random((5, 7), dtype=np.float32)
        _write_pfm(path, arr)
        loaded = _read_pfm(path)
        np.testing.assert_allclose(arr, loaded, atol=1e-6)

    def test_pfm_header(self, tmp_dir):
        path = tmp_dir / "header.pfm"
        arr = np.zeros((3, 4, 3), dtype=np.float32)
        _write_pfm(path, arr)

        with open(path, "rb") as f:
            tag = f.readline().decode().strip()
            dims = f.readline().decode().strip()
            scale = f.readline().decode().strip()

        assert tag == "PF"
        assert dims == "4 3"
        assert float(scale) < 0  # little-endian

    def test_invalid_tag_raises(self, tmp_dir):
        path = tmp_dir / "bad.pfm"
        path.write_bytes(b"P6\n4 4\n255\n" + b"\x00" * 48)
        with pytest.raises(ValueError, match="Not a PFM file"):
            _read_pfm(path)

    def test_clamp_on_pfm_to_png(self, tmp_dir):
        path = tmp_dir / "hdr.pfm"
        arr = np.array([[[2.0, -0.5, 0.5]]], dtype=np.float32)
        _write_pfm(path, arr)
        png_out = tmp_dir / "hdr_out.png"
        pfm_to_png(path, png_out)
        result = np.asarray(Image.open(png_out))
        assert result[0, 0, 0] == 255   # clamped from 2.0
        assert result[0, 0, 1] == 0     # clamped from -0.5
        assert result[0, 0, 2] == 128   # 0.5 * 255 rounded
