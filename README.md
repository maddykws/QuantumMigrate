# QuantumMigrate

Your codebase is probably already compromised — just not decrypted yet.

Nation-state actors are collecting encrypted traffic *right now*, storing it until quantum computers are powerful enough to crack it. Google's March 2026 paper showed it takes around 500,000 qubits to break Bitcoin's encryption. Those qubits are coming. RSA, ECC, SHA-1, Diffie-Hellman — all of it breaks under Shor's algorithm.

QuantumMigrate scans any codebase and tells you exactly where you're exposed.

![QuantumMigrate scanning paramiko and pycryptodome](demo.gif)

---

I scanned some popular Python repos. Here's what I found:

- **paramiko** — 19 findings. 16 CRITICAL. The SSH library half the internet depends on.
- **pycryptodome** — 485 findings. 420 CRITICAL. The crypto library people use *to be secure*.

Nobody has fixed this yet. NIST finalized the replacements in 2024. The deadline is 2030. Most teams haven't started.

---

## What it does

Point it at a repo. It walks every file, finds every line using vulnerable crypto, and tells you what to replace it with — including the exact import and function call.

```bash
pip install quantum-migrate

quantummigrate scan ./my-project
quantummigrate scan https://github.com/django/django
quantummigrate scan ./my-project --output markdown   # commits a QUANTUM_MIGRATION.md
quantummigrate scan ./my-project --no-ai             # pattern-only, no API key needed
```

With an Anthropic API key it uses Claude to explain *why* each specific usage is vulnerable and shows you the replacement code in the same language. Without a key it still runs — just pattern matching, still useful.

---

## What it finds

| Vulnerability | Why it matters | Replace with |
|---|---|---|
| RSA | Shor's algorithm breaks it in polynomial time | CRYSTALS-Dilithium (ML-DSA, FIPS 204) |
| ECC / ECDSA | Same — Shor's solves discrete log on elliptic curves | CRYSTALS-Kyber (ML-KEM, FIPS 203) |
| Diffie-Hellman | Same | CRYSTALS-Kyber (ML-KEM, FIPS 203) |
| DSA | Same | CRYSTALS-Dilithium (ML-DSA, FIPS 204) |
| SHA-1 | Grover's halves the security to ~40 bits. Already broken classically too | SHA-384 or SHA-512 |
| MD5 | Classically broken since 2004. Grover makes it worse | SHA-256 at minimum |
| AES-128 | Grover reduces effective key strength to 64 bits | AES-256 |

Scans Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, C#, Ruby, PHP, Swift, Kotlin.

---

## Output

Three formats:

**Terminal** — color-coded table, severity by severity, file by file.

**JSON** (`quantum_report.json`) — machine-readable, pipe it into whatever.

**Markdown** (`QUANTUM_MIGRATION.md`) — commit this to your repo. It's a migration checklist with the exact replacement code per finding.

---

## Web UI

```bash
pip install "quantum-migrate[web]"
ANTHROPIC_API_KEY=sk-ant-... streamlit run web/app.py
```

Paste a GitHub URL or drop in code directly. Downloads the report when done.

---

## Setup

```bash
git clone https://github.com/maddykws/QuantumMigrate
cd QuantumMigrate
pip install -e .

# no API key needed for basic scanning
quantummigrate scan ./some-project --no-ai

# with Claude analysis
export ANTHROPIC_API_KEY=sk-ant-...
quantummigrate scan ./some-project
```

---

## Why now

The threat isn't theoretical anymore. CISA issued an advisory. NSA issued an advisory. NIST published the replacement standards. The only thing most teams haven't done is check their own code.

This takes 30 seconds to run. Do it.

---

## Contributing

Open issues, open PRs. Run `pytest tests/` before you push.

```
quantum_migrate/patterns.py   — add new vulnerable patterns here
quantum_migrate/scanner.py    — file walker
quantum_migrate/analyzer.py   — Claude API integration
quantum_migrate/reporter.py   — output formats
```

MIT license.
