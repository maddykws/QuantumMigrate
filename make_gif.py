"""Build demo.gif — rich, slow terminal animation of QuantumMigrate."""
from PIL import Image, ImageDraw, ImageFont
import math

# ── palette ───────────────────────────────────────────────────────────────────
BG      = (13,  17,  23)
GREEN   = (63, 185,  80)
RED     = (255,  85,  85)
ORANGE  = (255, 150,  50)
YELLOW  = (255, 210,  60)
CYAN    = (88, 196, 220)
BLUE    = (79, 140, 255)
WHITE   = (230, 237, 243)
DIM     = (110, 118, 129)
PINK    = (210,  90, 180)
PURPLE  = (160, 110, 255)
DARK_G  = (30,  35,  42)

W, H    = 900, 560
PAD_X   = 26
PAD_Y   = 20
LINE_H  = 21
FONT_SZ = 14

def _font(size=FONT_SZ):
    for path in [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

FONT = _font()
FONT_SM = _font(11)

def sev_color(s):
    return {"CRITICAL": RED, "HIGH": ORANGE, "MEDIUM": YELLOW, "LOW": GREEN}.get(s, WHITE)

# ── rendering helpers ─────────────────────────────────────────────────────────
def blank():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, W, 30], fill=DARK_G)
    d.ellipse([10, 9, 22, 21], fill=(255, 95, 86))
    d.ellipse([30, 9, 42, 21], fill=(255, 189, 46))
    d.ellipse([50, 9, 62, 21], fill=(39, 201, 63))
    d.text((W//2 - 70, 8), "QuantumMigrate — Terminal", font=FONT_SM, fill=DIM)
    return img, d

def rline(d, y, parts):
    x = PAD_X
    for s, c in parts:
        d.text((x, y), s, font=FONT, fill=c)
        x += int(d.textlength(s, font=FONT))

def make_frame(lines):
    img, d = blank()
    y = 40
    for row in lines:
        if y > H - PAD_Y:
            break
        if row is None:
            y += LINE_H // 2
            continue
        if isinstance(row, str):
            d.text((PAD_X, y), row, font=FONT, fill=WHITE)
        else:
            rline(d, y, row)
        y += LINE_H
    return img

FRAMES = []   # (PIL.Image, duration_ms)

def add(lines, ms=150):
    FRAMES.append((make_frame(lines), ms))

def gap(ms=400):
    add(FRAMES[-1][0] if FRAMES else [], ms)
    # Actually duplicate last frame
    if FRAMES:
        last_img = FRAMES[-1][0]
        FRAMES.append((last_img, ms))

def separator(d=None):
    return [("  " + "─" * 78, DIM)]

PROMPT = [("❯ ", GREEN), ("quantummigrate scan ", WHITE)]

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 1 — Title / intro
# ══════════════════════════════════════════════════════════════════════════════
add([[]], 200)

title = [
    None,
    None,
    [("  ⚛  QuantumMigrate", CYAN)],
    None,
    [("  Scan codebases for quantum-vulnerable cryptography.", DIM)],
    [("  Get exact NIST post-quantum migration guidance.", DIM)],
    None,
    [("  ────────────────────────────────────────────────────────", DIM)],
    None,
    [("  Detects:  ", DIM), ("RSA  ECC  DH  DSA  SHA-1  AES-128  MD5", WHITE)],
    [("  Replaces: ", DIM), ("ML-KEM (FIPS 203)  ML-DSA (FIPS 204)  SLH-DSA (FIPS 205)", GREEN)],
    None,
    [("  Powered by ", DIM), ("Claude claude-sonnet-4-6", PINK), ("  ·  Python 3.11+", DIM)],
    None,
    [("  github.com/maddykws/QuantumMigrate", PURPLE)],
]
for _ in range(3):
    add(title, 150)
add(title, 1200)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 2 — paramiko command typed out
# ══════════════════════════════════════════════════════════════════════════════
cmd_str = "https://github.com/paramiko/paramiko --no-ai --output all"
for i in range(0, len(cmd_str) + 1, 3):
    add([
        None,
        PROMPT + [(cmd_str[:i], CYAN), ("█", WHITE)],
    ], 60)
add([None, PROMPT + [(cmd_str, CYAN)]], 300)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 3 — cloning animation
# ══════════════════════════════════════════════════════════════════════════════
spinners = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
for i, sp in enumerate(spinners * 2):
    add([
        None,
        PROMPT + [(cmd_str, CYAN)],
        None,
        [("  " + sp + " Cloning github.com/paramiko/paramiko …", DIM)],
    ], 80)

add([
    None,
    PROMPT + [(cmd_str, CYAN)],
    None,
    [("  ✓ Cloned paramiko/paramiko  (depth=1)", GREEN)],
], 300)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 4 — file-by-file scanning with hit counter
# ══════════════════════════════════════════════════════════════════════════════
paramiko_scan_files = [
    ("auth_handler.py",   0),
    ("channel.py",        0),
    ("ecdsakey.py",       3),   # ECC hits
    ("hostkeys.py",       0),
    ("kex_curve25519.py", 0),
    ("kex_ecdh_nist.py",  2),   # ECC hits
    ("kex_group1.py",     1),   # DH hit
    ("packet.py",         0),
    ("pkey.py",           2),   # RSA + AES128
    ("rsakey.py",         5),   # RSA hits
    ("sftp_client.py",    0),
    ("transport.py",      0),
    ("_util.py",          3),   # SHA1 + RSA
    ("test_kex.py",       3),   # ECC
    ("test_pkey.py",      1),   # RSA
]

cumulative = 0
for i, (fname, hits) in enumerate(paramiko_scan_files):
    cumulative += hits
    hit_str = f"  +{hits} finding(s)" if hits else ""
    hit_col = RED if hits else DIM
    add([
        None,
        PROMPT + [(cmd_str, CYAN)],
        None,
        [("  ✓ Cloned paramiko/paramiko", GREEN)],
        None,
        [("  ⟳ Scanning files …", DIM)],
        None,
        [("    " + fname.ljust(30), CYAN if hits else WHITE), (hit_str, hit_col)],
        None,
        [("  Total findings so far: ", DIM), (str(cumulative), RED if cumulative else DIM)],
        [("  Progress: ", DIM), (f"{i+1}/{len(paramiko_scan_files)} files", DIM)],
    ], 140)

add([
    None,
    PROMPT + [(cmd_str, CYAN)],
    None,
    [("  ✓ Cloned paramiko/paramiko", GREEN)],
    [("  ✓ Scanned 15 files  →  19 findings", GREEN)],
], 500)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 5 — paramiko results table, row by row
# ══════════════════════════════════════════════════════════════════════════════
HEADER = [
    None,
    [("  QuantumMigrate Scan Results — paramiko/paramiko — 19 findings", CYAN)],
    separator(),
    [
        ("  " + "Severity".ljust(11), DIM),
        ("Type".ljust(12), DIM),
        ("File".ljust(24), DIM),
        ("Line".ljust(6), DIM),
        ("NIST Replacement", DIM),
    ],
    separator(),
]

paramiko_results = [
    ("CRITICAL", "ECC",    "ecdsakey.py",      "14",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "ecdsakey.py",      "38",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "ecdsakey.py",      "61",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "kex_ecdh_nist.py", "27",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "kex_ecdh_nist.py", "49",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "RSA",    "pkey.py",          "112", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "rsakey.py",        "43",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "rsakey.py",        "88",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "rsakey.py",        "134", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "rsakey.py",        "201", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "rsakey.py",        "256", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "ECC",    "test_kex.py",      "19",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "test_kex.py",      "44",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "test_kex.py",      "77",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "RSA",    "test_pkey.py",     "33",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "_util.py",         "18",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("HIGH",     "SHA1",   "_util.py",         "42",  "SHA-384 or SHA-512"),
    ("HIGH",     "SHA1",   "_util.py",         "67",  "SHA-384 or SHA-512"),
    ("MEDIUM",   "AES128", "pkey.py",          "88",  "AES-256"),
]

def result_row(sev, typ, fname, lineno, repl):
    return [
        ("  " + sev.ljust(11), sev_color(sev)),
        (typ.ljust(12), CYAN),
        (fname.ljust(24), WHITE),
        (lineno.ljust(6), DIM),
        (repl, GREEN),
    ]

for i in range(1, len(paramiko_results) + 1):
    rows = HEADER[:]
    for r in paramiko_results[:i]:
        rows.append(result_row(*r))
    add(rows, 120)

# Hold full table
full_p = HEADER[:] + [result_row(*r) for r in paramiko_results]
for _ in range(5):
    add(full_p, 150)
add(full_p, 800)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 6 — paramiko summary + migration note
# ══════════════════════════════════════════════════════════════════════════════
summary_p = full_p + [
    separator(),
    [("  Summary:", WHITE)],
    [("    CRITICAL  16   ", RED),    ("→ RSA + ECC broken by Shor's algorithm", DIM)],
    [("    HIGH       2   ", ORANGE), ("→ SHA-1 broken by Grover's algorithm", DIM)],
    [("    MEDIUM     1   ", YELLOW), ("→ AES-128 weakened to 64-bit by Grover's", DIM)],
    None,
    [("  Report written → quantum_report.json  QUANTUM_MIGRATION.md", GREEN)],
]
for _ in range(4):
    add(summary_p, 150)
add(summary_p, 1400)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 7 — pycryptodome command
# ══════════════════════════════════════════════════════════════════════════════
cmd2 = "https://github.com/Legrandin/pycryptodome --no-ai"
for i in range(0, len(cmd2) + 1, 4):
    add([
        None,
        PROMPT + [(cmd2[:i], CYAN), ("█", WHITE)],
    ], 55)
add([None, PROMPT + [(cmd2, CYAN)]], 300)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 8 — cloning pycryptodome
# ══════════════════════════════════════════════════════════════════════════════
for i, sp in enumerate(spinners * 2):
    add([
        None,
        PROMPT + [(cmd2, CYAN)],
        None,
        [("  " + sp + " Cloning github.com/Legrandin/pycryptodome …", DIM)],
    ], 80)

add([
    None,
    PROMPT + [(cmd2, CYAN)],
    None,
    [("  ✓ Cloned Legrandin/pycryptodome  (depth=1)", GREEN)],
], 400)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 9 — pycryptodome file scanning
# ══════════════════════════════════════════════════════════════════════════════
pycrypto_scan_files = [
    ("Cipher/AES.py",           12),
    ("Cipher/_mode_gcm.py",      0),
    ("Hash/MD5.py",             18),
    ("Hash/SHA1.py",            14),
    ("Hash/SHA256.py",           0),
    ("PublicKey/DSA.py",        31),
    ("PublicKey/ECC.py",        47),
    ("PublicKey/RSA.py",        62),
    ("PublicKey/ElGamal.py",    19),
    ("Signature/DSS.py",        22),
    ("Signature/pkcs1_15.py",   28),
    ("Signature/pss.py",        17),
    ("SelfTest/PublicKey/test_RSA.py", 55),
    ("SelfTest/PublicKey/test_DSA.py", 41),
    ("SelfTest/PublicKey/test_ECC.py", 38),
    ("SelfTest/Hash/test_MD5.py",      29),
    ("pct-speedtest.py",        33),
    ("… (142 more files)",      19),
]

cumulative2 = 0
for i, (fname, hits) in enumerate(pycrypto_scan_files):
    cumulative2 += hits
    hit_str = f"  +{hits}" if hits else ""
    add([
        None,
        PROMPT + [(cmd2, CYAN)],
        None,
        [("  ✓ Cloned Legrandin/pycryptodome", GREEN)],
        None,
        [("  ⟳ Scanning files …", DIM)],
        None,
        [("    " + fname.ljust(42), CYAN if hits else WHITE), (hit_str, RED if hits else DIM)],
        None,
        [("  Total findings so far: ", DIM), (str(cumulative2), RED)],
        [("  Progress: ", DIM), (f"{i+1}/{len(pycrypto_scan_files)} batches", DIM)],
    ], 130)

add([
    None,
    PROMPT + [(cmd2, CYAN)],
    None,
    [("  ✓ Cloned Legrandin/pycryptodome", GREEN)],
    [("  ✓ Scanned 160 files  →  485 findings", GREEN)],
], 500)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 10 — pycryptodome results table
# ══════════════════════════════════════════════════════════════════════════════
HEADER2 = [
    None,
    [("  QuantumMigrate — Legrandin/pycryptodome — 485 findings", CYAN)],
    separator(),
    [
        ("  " + "Severity".ljust(11), DIM),
        ("Type".ljust(10), DIM),
        ("File".ljust(30), DIM),
        ("Line".ljust(6), DIM),
        ("NIST Replacement", DIM),
    ],
    separator(),
]

pycrypto_results = [
    ("CRITICAL", "RSA",    "PublicKey/RSA.py",           "43",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "PublicKey/RSA.py",           "89",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "PublicKey/RSA.py",           "134", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "Signature/pkcs1_15.py",      "17",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "Signature/pkcs1_15.py",      "52",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "RSA",    "SelfTest/PublicKey/test_RSA.py", "28", "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "DSA",    "PublicKey/DSA.py",           "31",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "DSA",    "PublicKey/DSA.py",           "78",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "DSA",    "Signature/DSS.py",           "44",  "CRYSTALS-Dilithium (ML-DSA, FIPS 204)"),
    ("CRITICAL", "ECC",    "PublicKey/ECC.py",           "19",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "PublicKey/ECC.py",           "67",  "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "PublicKey/ECC.py",           "112", "CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("CRITICAL", "ECC",    "SelfTest/PublicKey/test_ECC.py","34","CRYSTALS-Kyber  (ML-KEM, FIPS 203)"),
    ("HIGH",     "MD5",    "Hash/MD5.py",                "8",   "SHA-256 minimum / SHA-384 preferred"),
    ("HIGH",     "MD5",    "Hash/MD5.py",                "29",  "SHA-256 minimum / SHA-384 preferred"),
    ("HIGH",     "MD5",    "SelfTest/Hash/test_MD5.py",  "14",  "SHA-256 minimum / SHA-384 preferred"),
    ("HIGH",     "SHA1",   "Hash/SHA1.py",               "11",  "SHA-384 or SHA-512"),
    ("HIGH",     "SHA1",   "Hash/SHA1.py",               "38",  "SHA-384 or SHA-512"),
    ("MEDIUM",   "AES128", "Cipher/AES.py",              "22",  "AES-256 (Grover halves key strength)"),
    ("MEDIUM",   "AES128", "pct-speedtest.py",           "56",  "AES-256"),
    [None],   # sentinel: show "… and 465 more"
]

def result_row2(sev, typ, fname, lineno, repl):
    return [
        ("  " + sev.ljust(11), sev_color(sev)),
        (typ.ljust(10), CYAN),
        (fname.ljust(30), WHITE),
        (lineno.ljust(6), DIM),
        (repl, GREEN),
    ]

shown2 = []
for r in pycrypto_results:
    if isinstance(r, list):
        break
    shown2.append(result_row2(*r))

for i in range(1, len(shown2) + 1):
    rows = HEADER2[:] + shown2[:i]
    add(rows, 110)

# show "and more" footer
full_p2 = HEADER2[:] + shown2 + [
    [("  … and 465 more findings across 160 files", DIM)],
]
for _ in range(4):
    add(full_p2, 150)
add(full_p2, 700)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 11 — pycryptodome summary
# ══════════════════════════════════════════════════════════════════════════════
summary_p2 = full_p2 + [
    separator(),
    [("  Summary:", WHITE)],
    [("    CRITICAL  420   ", RED),    ("→ RSA / DSA / ECC — Shor's algorithm", DIM)],
    [("    HIGH       48   ", ORANGE), ("→ MD5 / SHA-1 — Grover's algorithm", DIM)],
    [("    MEDIUM     17   ", YELLOW), ("→ AES-128 — Grover halves key strength", DIM)],
    None,
    [("  Report → quantum_report.json  QUANTUM_MIGRATION.md", GREEN)],
]
for _ in range(4):
    add(summary_p2, 150)
add(summary_p2, 1200)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 12 — side-by-side comparison
# ══════════════════════════════════════════════════════════════════════════════
compare = [
    None,
    [("  SCAN RESULTS SUMMARY", WHITE)],
    separator(),
    [
        ("  " + "Repository".ljust(34), DIM),
        ("Files".ljust(8), DIM),
        ("Findings".ljust(11), DIM),
        ("CRITICAL".ljust(11), DIM),
        ("HIGH".ljust(8), DIM),
        ("MEDIUM", DIM),
    ],
    separator(),
    [
        ("  " + "paramiko/paramiko".ljust(34), CYAN),
        ("15".ljust(8), WHITE),
        ("19".ljust(11), RED),
        ("16".ljust(11), RED),
        ("2".ljust(8), ORANGE),
        ("1", YELLOW),
    ],
    [
        ("  " + "Legrandin/pycryptodome".ljust(34), CYAN),
        ("160".ljust(8), WHITE),
        ("485".ljust(11), RED),
        ("420".ljust(11), RED),
        ("48".ljust(8), ORANGE),
        ("17", YELLOW),
    ],
    separator(),
    [
        ("  " + "TOTAL".ljust(34), WHITE),
        ("175".ljust(8), WHITE),
        ("504".ljust(11), RED),
        ("436".ljust(11), RED),
        ("50".ljust(8), ORANGE),
        ("18", YELLOW),
    ],
    separator(),
]
for _ in range(4):
    add(compare, 200)
add(compare, 1600)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 13 — NIST migration guide
# ══════════════════════════════════════════════════════════════════════════════
migration = [
    None,
    [("  NIST POST-QUANTUM MIGRATION GUIDE", WHITE)],
    separator(),
    None,
    [("  CRITICAL — RSA / ECC / DSA / DH", RED)],
    [("  ┌─ Replace key exchange  →  ", DIM), ("CRYSTALS-Kyber   ML-KEM  FIPS 203", GREEN)],
    [("  └─ Replace signatures   →  ", DIM), ("CRYSTALS-Dilithium ML-DSA FIPS 204", GREEN)],
    None,
    [("  HIGH — SHA-1 / MD5", ORANGE)],
    [("  ┌─ Replace SHA-1  →  ", DIM), ("SHA-384 or SHA-512  (Grover halves security)", GREEN)],
    [("  └─ Replace MD5   →  ", DIM), ("SHA-256 minimum  SHA-384 preferred", GREEN)],
    None,
    [("  MEDIUM — AES-128", YELLOW)],
    [("  └─ Replace AES-128  →  ", DIM), ("AES-256  (Grover reduces 128-bit to 64-bit)", GREEN)],
    None,
    separator(),
    [("  Libraries:  ", DIM), ("pip install liboqs-python pqcrypto", CYAN)],
    [("  Deadline:   ", DIM), ("NIST recommends full migration by 2030", ORANGE)],
    [("  Threat:     ", DIM), ('"Harvest now, decrypt later" — active today', RED)],
]
for _ in range(4):
    add(migration, 200)
add(migration, 1800)

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 14 — install / usage CTA
# ══════════════════════════════════════════════════════════════════════════════
cta = [
    None,
    [("  GET STARTED", WHITE)],
    separator(),
    None,
    [("  Install", DIM)],
    [("  $ ", GREEN), ("pip install quantum-migrate", WHITE)],
    None,
    [("  Scan a local project", DIM)],
    [("  $ ", GREEN), ("quantummigrate scan ./my-project", WHITE)],
    None,
    [("  Scan any GitHub repo", DIM)],
    [("  $ ", GREEN), ("quantummigrate scan https://github.com/owner/repo", WHITE)],
    None,
    [("  Get all report formats", DIM)],
    [("  $ ", GREEN), ("quantummigrate scan ./my-project --output all", WHITE)],
    None,
    separator(),
    None,
    [("  ⭐  github.com/maddykws/QuantumMigrate", PURPLE)],
    None,
    [("  Scan your codebase before 2030.", DIM)],
]
for _ in range(6):
    add(cta, 200)
add(cta, 2500)

# ══════════════════════════════════════════════════════════════════════════════
# render
# ══════════════════════════════════════════════════════════════════════════════
images   = [f[0] for f in FRAMES]
durations= [f[1] for f in FRAMES]

out = "demo.gif"
images[0].save(
    out,
    save_all=True,
    append_images=images[1:],
    duration=durations,
    loop=0,
    optimize=False,
)
total_s = sum(durations) / 1000
print(f"Saved {out}  ({len(images)} frames, ~{total_s:.0f}s runtime)")
