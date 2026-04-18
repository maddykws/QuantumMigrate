import os
from dataclasses import dataclass

import anthropic

from .scanner import Finding

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


@dataclass
class Analysis:
    finding: Finding
    explanation: str
    replacement_code: str
    urgency: str


_SYSTEM = (
    "You are a post-quantum cryptography expert helping developers migrate to "
    "NIST post-quantum standards (FIPS 203/204/205). Be concise, precise, and practical."
)

_PROMPT = """\
File: {file}
Language: {language}
Line {line_number}: {line_content}
Vulnerability: {vuln_type}
NIST replacement: {nist_replacement}

Respond in this exact JSON structure (no markdown fences):
{{
  "explanation": "2-3 sentences explaining specifically why this code is quantum-vulnerable.",
  "replacement_code": "The exact import statement(s) and replacement function call in {language}.",
  "urgency": "IMMEDIATE | NEAR_TERM | MONITOR"
}}
"""


def analyze_finding(finding: Finding) -> Analysis:
    client = _get_client()
    prompt = _PROMPT.format(
        file=finding.file,
        language=finding.language,
        line_number=finding.line_number,
        line_content=finding.line_content.strip(),
        vuln_type=finding.vuln_type,
        nist_replacement=finding.nist_replacement,
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    import json

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "explanation": raw[:300],
            "replacement_code": f"# Replace with {finding.nist_replacement}",
            "urgency": "NEAR_TERM",
        }

    return Analysis(
        finding=finding,
        explanation=data.get("explanation", ""),
        replacement_code=data.get("replacement_code", ""),
        urgency=data.get("urgency", "NEAR_TERM"),
    )


def analyze_findings(findings: list[Finding], max_ai: int = 20) -> list[Analysis]:
    results: list[Analysis] = []
    # Prioritise CRITICAL findings for AI analysis
    sorted_findings = sorted(findings, key=lambda f: (f.severity != "CRITICAL", f.severity != "HIGH"))
    for i, finding in enumerate(sorted_findings):
        if i >= max_ai:
            results.append(
                Analysis(
                    finding=finding,
                    explanation=finding.why,
                    replacement_code=f"# Replace with {finding.nist_replacement} ({finding.library})",
                    urgency="NEAR_TERM",
                )
            )
        else:
            try:
                results.append(analyze_finding(finding))
            except Exception:
                results.append(
                    Analysis(
                        finding=finding,
                        explanation=finding.why,
                        replacement_code=f"# Replace with {finding.nist_replacement} ({finding.library})",
                        urgency="NEAR_TERM",
                    )
                )
    return results
