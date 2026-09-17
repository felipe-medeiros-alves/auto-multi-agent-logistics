import json

from logistics_crew.reporting.models import RunTrace


def render_markdown_report(trace: RunTrace) -> str:
    lines = [
        "# Execution report",
        "",
        "## Instruction",
        "",
        trace.instruction.strip(),
        "",
        "## Plan",
        "",
        trace.plan.strip() or "_No plan recorded._",
        "",
        "## Tool evidence",
        "",
    ]
    if not trace.tool_events:
        lines.append("_No tool calls recorded._")
    else:
        for event in trace.tool_events:
            lines.append(f"### {event.name}")
            lines.append("")
            lines.append("**Arguments:**")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(event.args, indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")
            lines.append("**Result:**")
            lines.append("")
            lines.append("```json")
            lines.append(event.result.strip())
            lines.append("```")
            lines.append("")

    lines.extend(["## Findings", "", trace.findings.strip() or "_None._", ""])
    lines.extend(["## Recommended next actions", ""])
    if trace.recommended_actions:
        for item in trace.recommended_actions:
            lines.append(f"- {item} (hypothetical; not executed)")
    else:
        lines.append("_None._")
    lines.append("")
    lines.extend(["## Gaps and risks", ""])
    if trace.gaps:
        for item in trace.gaps:
            lines.append(f"- {item}")
    else:
        lines.append("_None._")
    lines.append("")
    return "\n".join(lines)
