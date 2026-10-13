"""REQ-010: conversions use built-in factors and no networking."""
import ast
import pathlib
import socket

from inches_to_metric_converter.core import convert_text

PKG_DIR = pathlib.Path(__file__).resolve().parents[2] / "src" / "inches_to_metric_converter"

NETWORK_MODULES = {
    "socket", "ssl", "urllib", "http", "requests", "urllib3", "httpx",
    "ftplib", "smtplib", "xmlrpc", "socketserver", "asyncio",
}


def test_req_010_converts_with_network_blocked(monkeypatch):
    def blocked(*args, **kwargs):
        raise OSError("network disabled for test")

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    assert convert_text("1", "inches", "millimeters") == "25.40"


def test_req_010_source_imports_no_network_modules():
    files = sorted(PKG_DIR.glob("*.py"))
    assert files, "no source files found"
    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # relative import within the package
                    continue
                roots = [(node.module or "").split(".")[0]]
            else:
                continue
            bad = set(roots) & NETWORK_MODULES
            assert not bad, f"{path.name} imports {bad}"
