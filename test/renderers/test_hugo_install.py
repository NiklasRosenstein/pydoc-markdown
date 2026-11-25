import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from pydoc_markdown.contrib.renderers import hugo
from pydoc_markdown.contrib.renderers.hugo import install_hugo, select_hugo_asset

# Asset names published for Hugo v0.170.1 (excerpt). Recent releases ship both the current names and the legacy
# `Linux-64bit` style names for Linux, but no tarball for macOS.
CURRENT_ASSETS = {
    "hugo_0.170.1_darwin-universal.pkg",
    "hugo_0.170.1_freebsd-amd64.tar.gz",
    "hugo_0.170.1_linux-amd64.tar.gz",
    "hugo_0.170.1_linux-arm64.tar.gz",
    "hugo_0.170.1_windows-amd64.zip",
    "hugo_0.170.1_windows-arm64.zip",
    "hugo_extended_0.170.1_Linux-64bit.tar.gz",
    "hugo_extended_0.170.1_Linux-ARM64.tar.gz",
    "hugo_extended_0.170.1_linux-amd64.tar.gz",
    "hugo_extended_0.170.1_linux-arm64.tar.gz",
    "hugo_extended_0.170.1_windows-amd64.zip",
}

# Asset names published for Hugo v0.103.0 (excerpt), the first release with the current naming scheme.
V0_103_ASSETS = {
    "hugo_extended_0.103.0_darwin-universal.tar.gz",
    "hugo_extended_0.103.0_linux-amd64.tar.gz",
    "hugo_extended_0.103.0_windows-amd64.zip",
}

# Asset names published for Hugo v0.102.0 (excerpt), before the naming scheme changed.
LEGACY_ASSETS = {
    "hugo_0.102.0_Linux-ARM64.tar.gz",
    "hugo_extended_0.102.0_Linux-64bit.tar.gz",
    "hugo_extended_0.102.0_Windows-64bit.zip",
}


@pytest.mark.parametrize(
    ("assets", "version", "platform", "machine", "extended", "expected"),
    [
        (CURRENT_ASSETS, "0.170.1", "linux", "x86_64", True, "hugo_extended_0.170.1_linux-amd64.tar.gz"),
        (CURRENT_ASSETS, "0.170.1", "linux", "aarch64", True, "hugo_extended_0.170.1_linux-arm64.tar.gz"),
        (CURRENT_ASSETS, "0.170.1", "linux", "x86_64", False, "hugo_0.170.1_linux-amd64.tar.gz"),
        (CURRENT_ASSETS, "0.170.1", "win32", "AMD64", True, "hugo_extended_0.170.1_windows-amd64.zip"),
        (CURRENT_ASSETS, "0.170.1", "win32", "ARM64", True, "hugo_0.170.1_windows-arm64.zip"),
        (CURRENT_ASSETS, "0.170.1", "freebsd14", "amd64", True, "hugo_0.170.1_freebsd-amd64.tar.gz"),
        (CURRENT_ASSETS, "0.170.1", "darwin", "arm64", True, None),
        (CURRENT_ASSETS, "0.170.1", "linux", "riscv64", True, None),
        (CURRENT_ASSETS, "0.170.1", "sunos5", "x86_64", True, None),
        (V0_103_ASSETS, "0.103.0", "darwin", "arm64", True, "hugo_extended_0.103.0_darwin-universal.tar.gz"),
        (LEGACY_ASSETS, "0.102.0", "linux", "x86_64", True, "hugo_extended_0.102.0_Linux-64bit.tar.gz"),
        (LEGACY_ASSETS, "0.102.0", "linux", "aarch64", True, "hugo_0.102.0_Linux-ARM64.tar.gz"),
        (LEGACY_ASSETS, "0.102.0", "win32", "AMD64", True, "hugo_extended_0.102.0_Windows-64bit.zip"),
    ],
)
def test_select_hugo_asset(assets, version, platform, machine, extended, expected) -> None:
    assert select_hugo_asset(assets, version, platform, machine, extended) == expected


class FakeResponse:
    def __init__(self, json_data=None, content: bytes = b"", status_code: int = 200) -> None:
        self._json_data = json_data
        self._content = content
        self.status_code = status_code
        self.headers: dict = {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data

    def iter_content(self, chunk_size: int):
        yield self._content

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        pass


def _tar_gz(name: str, data: bytes) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def _zip(name: str, data: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, data)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("platform", "machine", "asset", "archive"),
    [
        ("linux", "x86_64", "hugo_extended_0.170.1_linux-amd64.tar.gz", _tar_gz("hugo", b"linux binary")),
        ("win32", "AMD64", "hugo_extended_0.170.1_windows-amd64.zip", _zip("hugo.exe", b"windows binary")),
    ],
)
def test_install_hugo_downloads_and_extracts_latest_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform: str, machine: str, asset: str, archive: bytes
) -> None:
    release = {
        "tag_name": "v0.170.1",
        "assets": [
            {"name": name, "browser_download_url": f"https://example.invalid/{name}"} for name in CURRENT_ASSETS
        ],
    }
    requested = []

    def fake_get(url: str, stream: bool = False) -> FakeResponse:
        requested.append(url)
        if url.endswith("/releases/latest"):
            return FakeResponse(json_data=release)
        assert url == f"https://example.invalid/{asset}"
        return FakeResponse(content=archive)

    monkeypatch.setattr(hugo.requests, "get", fake_get)
    monkeypatch.setattr(hugo.sys, "platform", platform)
    monkeypatch.setattr(hugo._platform, "machine", lambda: machine)

    target = tmp_path / ".bin" / "hugo"
    install_hugo(str(target))

    assert requested == [f"{hugo._HUGO_RELEASES_API}/latest", f"https://example.invalid/{asset}"]
    assert target.read_bytes() in (b"linux binary", b"windows binary")


def test_install_hugo_reports_unknown_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hugo.requests, "get", lambda url: FakeResponse(status_code=404))

    with pytest.raises(ValueError, match="no Hugo release for version '0.1.2' found"):
        install_hugo(str(tmp_path / "hugo"), version="v0.1.2")


def test_install_hugo_reports_missing_platform_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    release = {"tag_name": "v0.170.1", "assets": [{"name": "hugo_0.170.1_darwin-universal.pkg"}]}
    release["assets"][0]["browser_download_url"] = "https://example.invalid/hugo.pkg"
    monkeypatch.setattr(hugo.requests, "get", lambda url: FakeResponse(json_data=release))
    monkeypatch.setattr(hugo.sys, "platform", "darwin")
    monkeypatch.setattr(hugo._platform, "machine", lambda: "arm64")

    with pytest.raises(EnvironmentError, match="install Hugo yourself"):
        install_hugo(str(tmp_path / "hugo"))


def test_get_github_releases_handles_single_page(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hugo.requests, "get", lambda url: FakeResponse(json_data=[{"tag_name": "v1"}]))

    assert list(hugo.get_github_releases("owner/repo")) == [{"tag_name": "v1"}]
