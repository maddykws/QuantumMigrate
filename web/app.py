import os
import sys
import json
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from quantum_migrate.scanner import scan_directory, clone_and_scan
from quantum_migrate.reporter import write_json, write_markdown
from quantum_migrate.patterns import VULNERABLE_PATTERNS

st.set_page_config(
    page_title="QuantumMigrate",
    page_icon="⚛️",
    layout="wide",
)

SEVERITY_COLORS = {
    "CRITICAL": "#ff4b4b",
    "HIGH": "#ffa500",
    "MEDIUM": "#ffd700",
    "LOW": "#00cc44",
}

st.title("⚛️ QuantumMigrate")
st.markdown(
    "**Scan any GitHub repo or code snippet for quantum-vulnerable cryptography "
    "and get NIST post-quantum migration guidance.**"
)

with st.expander("What is post-quantum cryptography?"):
    st.markdown(
        """
**The threat:** Quantum computers running Shor's algorithm can break RSA, ECC, and
Diffie-Hellman — the cryptographic foundations of HTTPS, SSH, and code signing — in
polynomial time. Google's March 2026 paper showed Bitcoin's encryption could fall
with ~500,000 qubits.

**"Harvest now, decrypt later":** Nation-state actors are already collecting encrypted
traffic today, planning to decrypt it once quantum computers are powerful enough.

**The fix:** NIST finalized post-quantum standards in 2024:
- **CRYSTALS-Kyber (ML-KEM, FIPS 203)** — key encapsulation (replaces RSA/DH/ECC for key exchange)
- **CRYSTALS-Dilithium (ML-DSA, FIPS 204)** — digital signatures (replaces RSA/DSA/ECDSA)
- **SPHINCS+ (SLH-DSA, FIPS 205)** — hash-based signatures (conservative backup)

**Timeline:** NIST recommends completing migration by 2030. Start now.
"""
    )

st.divider()

tab_url, tab_code = st.tabs(["Scan GitHub URL", "Scan Pasted Code"])

with tab_url:
    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/owner/repo",
        help="Public GitHub repositories only.",
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        sev_filter = st.selectbox("Min Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with col2:
        no_ai = st.checkbox("Disable AI analysis (pattern-only, faster)", value=False)

    if st.button("Scan Repository", type="primary", use_container_width=True):
        if not github_url.strip():
            st.error("Please enter a GitHub URL.")
        else:
            sev = None if sev_filter == "All" else sev_filter
            with st.spinner(f"Cloning and scanning {github_url}…"):
                try:
                    findings, repo_dir = clone_and_scan(github_url, severity_filter=sev)
                    st.session_state["findings"] = findings
                    st.session_state["repo_dir"] = str(repo_dir)
                    st.session_state["analyses"] = None
                except Exception as e:
                    st.error(f"Failed to clone repository: {e}")
                    findings = []

            if findings and not no_ai and os.environ.get("ANTHROPIC_API_KEY"):
                from quantum_migrate.analyzer import analyze_findings
                with st.spinner("Analysing findings with Claude…"):
                    analyses = analyze_findings(findings, max_ai=10)
                    st.session_state["analyses"] = analyses

with tab_code:
    code_input = st.text_area(
        "Paste code here",
        height=250,
        placeholder="# Paste any Python, JavaScript, Go, Java, etc. code here",
    )
    lang_ext = st.selectbox(
        "Language",
        [".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp"],
        format_func=lambda x: x.lstrip(".").upper(),
    )

    if st.button("Scan Code Snippet", type="primary", use_container_width=True):
        if not code_input.strip():
            st.error("Please paste some code to scan.")
        else:
            with tempfile.TemporaryDirectory() as tmp:
                snippet = Path(tmp) / f"snippet{lang_ext}"
                snippet.write_text(code_input, encoding="utf-8")
                findings = scan_directory(tmp)
                st.session_state["findings"] = findings
                st.session_state["analyses"] = None
                st.session_state["repo_dir"] = tmp

findings = st.session_state.get("findings")
analyses = st.session_state.get("analyses")

if findings is not None:
    st.divider()
    if not findings:
        st.success("No quantum-vulnerable cryptography found!")
    else:
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1

        cols = st.columns(len(counts) + 1)
        cols[0].metric("Total Findings", len(findings))
        for i, (sev, cnt) in enumerate(sorted(counts.items(), key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW"].index(x[0]) if x[0] in ["CRITICAL","HIGH","MEDIUM","LOW"] else 9), start=1):
            cols[i].metric(sev, cnt)

        st.subheader("Findings")
        rows = []
        for f in sorted(findings, key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW"].index(x.severity) if x.severity in ["CRITICAL","HIGH","MEDIUM","LOW"] else 9):
            rows.append({
                "Severity": f.severity,
                "Type": f.vuln_type,
                "File": Path(f.file).name,
                "Line": f.line_number,
                "NIST Replacement": f.nist_replacement,
                "Timeline": f.timeline,
            })
        st.dataframe(rows, use_container_width=True)

        if analyses:
            st.subheader("AI Analysis")
            analysis_map = {(a.finding.file, a.finding.line_number): a for a in analyses}
            for f in sorted(findings, key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW"].index(x.severity) if x.severity in ["CRITICAL","HIGH","MEDIUM","LOW"] else 9):
                a = analysis_map.get((f.file, f.line_number))
                if a:
                    color = SEVERITY_COLORS.get(f.severity, "#888")
                    with st.expander(f"**{f.vuln_type}** — `{Path(f.file).name}:{f.line_number}`"):
                        st.markdown(f"**Severity:** :{color}[{f.severity}]")
                        st.markdown(f"**Why it's vulnerable:** {a.explanation}")
                        if a.replacement_code:
                            st.markdown("**Replacement:**")
                            st.code(a.replacement_code, language=f.language.lower())

        st.subheader("Download Reports")
        report_dir = st.session_state.get("repo_dir", "/tmp")
        json_path = str(Path(report_dir) / "quantum_report.json")
        md_path = str(Path(report_dir) / "QUANTUM_MIGRATION.md")

        write_json(findings, analyses, json_path)
        write_markdown(findings, analyses, md_path)

        col_j, col_m = st.columns(2)
        with col_j:
            with open(json_path, "rb") as f:
                st.download_button("Download JSON Report", f, file_name="quantum_report.json", mime="application/json", use_container_width=True)
        with col_m:
            with open(md_path, "rb") as f:
                st.download_button("Download Markdown Report", f, file_name="QUANTUM_MIGRATION.md", mime="text/markdown", use_container_width=True)

st.divider()
st.caption(
    "QuantumMigrate — open source | "
    "[GitHub](https://github.com/maddykws/QuantumMigrate) | "
    "Powered by Claude (claude-sonnet-4-6) + NIST PQC Standards"
)
