import tempfile
from pathlib import Path

import pytest

from quantum_migrate.scanner import scan_directory, _scan_file, Finding
from quantum_migrate.patterns import VULNERABLE_PATTERNS


PYTHON_VULNERABLE = """\
import hashlib
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.asymmetric import ec

key = RSA.generate(2048)
private_key = ec.generate_private_key(ec.SECP256K1())
digest = hashlib.md5(b"hello").hexdigest()
digest2 = hashlib.sha1(b"world").hexdigest()
"""

JS_VULNERABLE = """\
const crypto = require('crypto');
const sign = crypto.createSign('RSA-SHA256');
const hash = crypto.createHash('md5');
const ecdh = crypto.createECDH('prime256v1');
"""

CLEAN_PYTHON = """\
import hashlib
digest = hashlib.sha256(b"safe").hexdigest()
digest2 = hashlib.sha512(b"also safe").hexdigest()
"""


def write_file(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def test_scan_python_finds_vulnerabilities():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "vuln.py", PYTHON_VULNERABLE)
        findings = scan_directory(tmp)
    assert len(findings) > 0
    types = {f.vuln_type for f in findings}
    assert "RSA" in types
    assert "ECC" in types
    assert "MD5" in types
    assert "SHA1" in types


def test_scan_js_finds_vulnerabilities():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "crypto.js", JS_VULNERABLE)
        findings = scan_directory(tmp)
    assert len(findings) > 0
    types = {f.vuln_type for f in findings}
    assert "RSA" in types
    assert "MD5" in types
    assert "ECC" in types


def test_clean_code_has_no_findings():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "safe.py", CLEAN_PYTHON)
        findings = scan_directory(tmp)
    assert findings == []


def test_severity_filter():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "vuln.py", PYTHON_VULNERABLE)
        findings = scan_directory(tmp, severity_filter="CRITICAL")
    for f in findings:
        assert f.severity == "CRITICAL"


def test_finding_fields():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "vuln.py", PYTHON_VULNERABLE)
        findings = scan_directory(tmp)
    for f in findings:
        assert isinstance(f, Finding)
        assert f.file
        assert f.line_number > 0
        assert f.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
        assert f.nist_replacement
        assert f.language


def test_skip_comment_lines():
    commented = "# RSA.generate(2048)  # this is a comment\n"
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_file(tmp, "commented.py", commented)
        findings = scan_directory(tmp)
    assert findings == []


def test_nonexistent_path_raises():
    with pytest.raises(FileNotFoundError):
        scan_directory("/nonexistent/path/xyz")
