# ⚛️ QuantumMigrate

> **Point it at any GitHub repo or local directory. It finds every line of code using RSA, ECC, SHA-1, AES-128, or MD5 and tells you exactly what to replace it with before quantum computers break it.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![NIST PQC](https://img.shields.io/badge/NIST-Post--Quantum-purple.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)

![QuantumMigrate demo — scanning paramiko and pycryptodome](demo.gif)

---

## Why This Matters Now

Google's March 2026 paper demonstrated that Bitcoin's encryption could be broken with ~500,000 qubits. CISA and NSA have issued advisories about **"harvest now, decrypt later"** attacks — adversaries collecting encrypted traffic today to decrypt once quantum computers arrive. Every organisation must migrate to NIST post-quantum standards before 2030.

No open-source scanner exists to help developers find where to start. QuantumMigrate fills that gap.

---

## Install

```bash
pip install quantum-migrate
```

Or from source:

```bash
git clone https://github.com/maddykws/QuantumMigrate.git
cd QuantumMigrate
pip install -e .
```

---

## Usage

```bash
# Scan a local directory
quantummigrate scan ./my-project

# Scan a GitHub repo
quantummigrate scan https://github.com/owner/repo

# Output JSON report
quantummigrate scan ./my-project --output json

# Output Markdown report (ready to commit)
quantummigrate scan ./my-project --output markdown

# All formats at once
quantummigrate scan ./my-project --output all

# Filter by severity
quantummigrate scan ./my-project --severity critical

# Skip Claude API (pattern matching only, no API key needed)
quantummigrate scan ./my-project --no-ai
```

### Web UI

```bash
pip install "quantum-migrate[web]"
ANTHROPIC_API_KEY=sk-ant-... streamlit run web/app.py
```

---

## What It Finds

| Vulnerability | Severity | Quantum Attack | NIST Replacement |
|--------------|----------|----------------|-----------------|
| RSA | CRITICAL | Shor's algorithm | CRYSTALS-Dilithium (ML-DSA, FIPS 204) |
| ECC / ECDSA | CRITICAL | Shor's algorithm | CRYSTALS-Kyber (ML-KEM, FIPS 203) |
| Diffie-Hellman | CRITICAL | Shor's algorithm | CRYSTALS-Kyber (ML-KEM, FIPS 203) |
| DSA | CRITICAL | Shor's algorithm | CRYSTALS-Dilithium (ML-DSA, FIPS 204) |
| SHA-1 | HIGH | Grover's algorithm | SHA-384 or SHA-512 |
| MD5 | HIGH | Already broken + Grover's | SHA-256 minimum |
| AES-128 | MEDIUM | Grover's (halves key strength) | AES-256 |

Scans: Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, C#, Ruby, PHP, Swift, Kotlin.

---

## What To Do

1. **Run the scan** — identify all vulnerable usages in your codebase
2. **Read the report** — `QUANTUM_MIGRATION.md` has exact replacement code for each finding
3. **Prioritise CRITICAL** — RSA, ECC, and DH are broken by Shor's algorithm, no workaround
4. **Migrate key exchange first** — replace with CRYSTALS-Kyber using [liboqs](https://openquantumsafe.org/) or [pqcrypto](https://pypi.org/project/pqcrypto/)
5. **Replace signatures** — migrate to CRYSTALS-Dilithium or SPHINCS+
6. **Upgrade hash functions** — SHA-1/MD5 → SHA-256+; AES-128 → AES-256

---

## Example Output

```
╭──────────────────────────────────────────────────────────────╮
│        QuantumMigrate Scan Results — 7 finding(s)            │
├──────────┬────────────────────┬────────────┬──────┬──────────┤
│ Severity │ Type               │ File       │ Line │ Replace  │
├──────────┼────────────────────┼────────────┼──────┼──────────┤
│ CRITICAL │ RSA                │ auth.py    │   42 │ ML-DSA   │
│ CRITICAL │ ECC                │ keys.py    │   17 │ ML-KEM   │
│ HIGH     │ SHA1               │ utils.py   │   88 │ SHA-512  │
│ HIGH     │ MD5                │ legacy.py  │  103 │ SHA-256  │
╰──────────┴────────────────────┴────────────┴──────┴──────────╯
```

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...        # Required for AI analysis
QUANTUM_MIGRATE_NO_AI=true          # Disable Claude API (pattern-only mode)
```

---

## NIST PQC Resources

- [CRYSTALS-Kyber (ML-KEM, FIPS 203)](https://pq-crystals.org/kyber/) — key encapsulation
- [CRYSTALS-Dilithium (ML-DSA, FIPS 204)](https://pq-crystals.org/dilithium/) — digital signatures
- [SPHINCS+ (SLH-DSA, FIPS 205)](https://sphincs.org/) — hash-based signatures
- [Open Quantum Safe / liboqs](https://openquantumsafe.org/) — production-ready library
- [CISA PQC Initiative](https://www.cisa.gov/quantum)
- [Google March 2026 quantum paper](https://arxiv.org/abs/2603.00659)

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
pip install -e ".[web]"
pytest tests/
```

---

## License

MIT © QuantumMigrate Contributors
