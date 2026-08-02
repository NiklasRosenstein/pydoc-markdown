import types

import docspec_python

from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.interfaces import Context


def init_loader(loader: PythonLoader, directory: str) -> PythonLoader:
    loader.init(Context(directory))
    return loader


def test_automatic_discovery_sorts_loaded_modules_by_exact_name(monkeypatch, tmp_path) -> None:
    discovered = [
        docspec_python.DiscoveryResult.Module("alpha", "alpha.py"),
        docspec_python.DiscoveryResult.Package("package", "package"),
        docspec_python.DiscoveryResult.Module("Beta", "Beta.py"),
    ]
    expanded_package = False
    consumed = False

    def iter_package_files(package, search_path):
        nonlocal expanded_package
        expanded_package = True
        yield "package.z", "package/z.py"
        yield "package", "package/__init__.py"
        yield "package.a", "package/a.py"

    def load_python_modules(**kwargs):
        def generate():
            nonlocal consumed
            consumed = True
            yield from (types.SimpleNamespace(name=name) for name, _ in kwargs["files"])

        return generate()

    monkeypatch.setattr(docspec_python, "discover", lambda path: iter(discovered))
    monkeypatch.setattr(docspec_python, "iter_package_files", iter_package_files)
    monkeypatch.setattr(docspec_python, "load_python_modules", load_python_modules)
    loader = init_loader(PythonLoader(search_path=["."]), str(tmp_path))
    loaded_modules = loader.load()

    assert expanded_package is False
    assert consumed is False
    assert [module.name for module in loaded_modules] == ["Beta", "alpha", "package", "package.a", "package.z"]
    assert expanded_package is True
    assert consumed is True


def test_explicit_module_and_package_order_is_preserved(monkeypatch, tmp_path) -> None:
    captured = {}

    def load_python_modules(**kwargs):
        captured.update(kwargs)
        names = [*kwargs["modules"], *kwargs["packages"]]
        return iter(types.SimpleNamespace(name=name) for name in names)

    monkeypatch.setattr(docspec_python, "load_python_modules", load_python_modules)
    loader = init_loader(
        PythonLoader(
            search_path=["."],
            modules=["z_module", "a_module"],
            packages=["z_package", "a_package"],
        ),
        str(tmp_path),
    )

    assert [module.name for module in loader.load()] == ["z_module", "a_module", "z_package", "a_package"]
    assert captured["modules"] == ["z_module", "a_module"]
    assert captured["packages"] == ["z_package", "a_package"]


def test_automatic_discovery_preserves_member_source_order(monkeypatch, tmp_path) -> None:
    members = [types.SimpleNamespace(name="z_member"), types.SimpleNamespace(name="a_member")]
    discovered = [
        docspec_python.DiscoveryResult.Module("z_module", "z_module.py"),
        docspec_python.DiscoveryResult.Module("a_module", "a_module.py"),
    ]

    def load_python_modules(**kwargs):
        return iter(
            types.SimpleNamespace(name=name, members=members if name == "a_module" else [])
            for name, _ in kwargs["files"]
        )

    monkeypatch.setattr(docspec_python, "discover", lambda path: iter(discovered))
    monkeypatch.setattr(docspec_python, "load_python_modules", load_python_modules)
    loader = init_loader(PythonLoader(search_path=["."]), str(tmp_path))

    loaded_modules = list(loader.load())

    assert [module.name for module in loaded_modules] == ["a_module", "z_module"]
    assert [member.name for member in loaded_modules[0].members] == ["z_member", "a_member"]
