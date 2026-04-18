import re
import os
from pathlib import Path
from typing import Generator
from dataclasses import dataclass, field

from .patterns import VULNERABLE_PATTERNS, SKIP_DIRS, LANGUAGE_EXTENSIONS


@dataclass
class Finding:
    file: str
    line_number: int
    line_content: str
    vuln_type: str
    severity: str
    nist_replacement: str
    library: str
    timeline: str
    why: str
    language: str
    pattern_matched: str = ""


def _is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
        return b"\x00" in chunk
    except OSError:
        return True


def _walk_files(root: Path) -> Generator[Path, None, None]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix in LANGUAGE_EXTENSIONS and not _is_binary(p):
                yield p


def _scan_file(path: Path) -> list[Finding]:
    language = LANGUAGE_EXTENSIONS.get(path.suffix, "Unknown")
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    compiled = {
        vtype: [(re.compile(p), p) for p in info["patterns"]]
        for vtype, info in VULNERABLE_PATTERNS.items()
    }

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue
        for vtype, pattern_list in compiled.items():
            for regex, raw_pattern in pattern_list:
                if regex.search(line):
                    info = VULNERABLE_PATTERNS[vtype]
                    findings.append(
                        Finding(
                            file=str(path),
                            line_number=lineno,
                            line_content=line.rstrip(),
                            vuln_type=vtype,
                            severity=info["severity"],
                            nist_replacement=info["nist_replacement"],
                            library=info["library"],
                            timeline=info["timeline"],
                            why=info["why"],
                            language=language,
                            pattern_matched=raw_pattern,
                        )
                    )
                    break  # one match per vuln type per line

    return findings


def scan_directory(path: str | Path, severity_filter: str | None = None) -> list[Finding]:
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    all_findings: list[Finding] = []
    for fpath in _walk_files(root):
        all_findings.extend(_scan_file(fpath))

    if severity_filter:
        sev = severity_filter.upper()
        all_findings = [f for f in all_findings if f.severity == sev]

    return all_findings


def clone_and_scan(github_url: str, severity_filter: str | None = None) -> tuple[list[Finding], Path]:
    import tempfile
    import git

    tmp = tempfile.mkdtemp(prefix="qm_")
    repo_dir = Path(tmp) / "repo"
    git.Repo.clone_from(github_url, repo_dir, depth=1)
    return scan_directory(repo_dir, severity_filter), repo_dir
