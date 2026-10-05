"""English reading copies must not replace the canonical numerical protocol."""
import gzip
from pathlib import Path

import pytest
from src.data import materials as main_materials
from verification import materials as independent_materials


@pytest.fixture(params=['main', 'independent'])
def reader(request, monkeypatch, tmp_path):
    if request.param == 'main':
        monkeypatch.setattr(main_materials, 'ROOT', tmp_path)
        return main_materials.protocol_bytes, tmp_path
    return lambda: independent_materials.protocol_bytes(tmp_path), tmp_path


def test_reads_exact_canonical_bytes_instead_of_reading_translation(reader):
    read, root = reader
    frozen = b'original frozen protocol\r\n'
    (root/'planning.md').write_bytes(b'English reading translation\n')
    (root/'manifests').mkdir()
    (root/'manifests/frozen_protocol.md.gz').write_bytes(gzip.compress(frozen, mtime=0))
    assert read() == frozen


def test_original_layout_without_archive_remains_supported(reader):
    read, root = reader
    frozen = b'original source specification\n'
    (root/'planning.md').write_bytes(frozen)
    assert read() == frozen


def test_invalid_archive_cannot_silently_fall_back_to_reading_copy(reader):
    read, root = reader
    (root/'planning.md').write_bytes(b'English reading translation\n')
    (root/'manifests').mkdir()
    (root/'manifests/frozen_protocol.md.gz').write_bytes(b'not a gzip archive')
    with pytest.raises(gzip.BadGzipFile):
        read()
