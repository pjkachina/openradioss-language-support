"""Claude AI explainer: converts a list of Changes into engineering analysis."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..diff.engine import Change

SYSTEM_PROMPT = """You are a senior CAE (Computer-Aided Engineering) analyst reviewing structural simulation model changes.

Your role:
- Interpret engineering significance of parameter changes, not just numeric differences
- Identify downstream effects on simulation results (stiffness, mass, stress, failure modes)
- Flag changes that could invalidate previous correlation or result in non-conservative simulations
- Be concise and technical; your audience is experienced FEA engineers

Output format:
- Use markdown with clear sections
- Lead with a brief executive summary (2-3 sentences)
- Group related changes by engineering impact
- For critical changes, explicitly state the physical consequence
- Use SI notation where appropriate

Language: Respond in the same language the input is written in."""


def _format_changes(changes: list[Change], before_file: str, after_file: str) -> str:
    lines = [
        f"## Deck Comparison",
        f"**Before**: `{before_file}`  ",
        f"**After**: `{after_file}`",
        "",
        f"### Changes ({len(changes)} total)",
        "",
    ]

    for ch in changes:
        sev_icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(ch.severity, "⚪")
        old_str = str(ch.old_value) if ch.old_value is not None else "—"
        new_str = str(ch.new_value) if ch.new_value is not None else "—"
        unit = f" {ch.unit}" if ch.unit else ""
        pct_str = f" ({ch.percent_change:+.1f}%)" if ch.percent_change is not None else ""

        lines.append(
            f"{sev_icon} **[{ch.severity}]** `{ch.item_type}/{ch.item_id}` ({ch.item_name}) "
            f"— **{ch.field}**: {old_str}{unit} → {new_str}{unit}{pct_str}"
        )

    lines += [
        "",
        "### Analysis Request",
        "Please provide:",
        "1. Executive summary of the engineering significance of these changes",
        "2. Physical consequences for simulation results (stiffness, mass, stress distribution, failure modes)",
        "3. Any concerns about simulation validity or non-conservative changes",
        "4. Recommendations for the reviewer",
    ]

    return "\n".join(lines)


class ClaudeExplainer:
    def __init__(self, api_key: str | None = None, model: str = "claude-opus-4-8") -> None:
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    def explain(
        self,
        changes: list[Change],
        before_file: str,
        after_file: str,
        console=None,
    ) -> str:
        """Generate engineering analysis for the given changes.

        Streams to console if provided, returns the full text.
        """
        from rich.markdown import Markdown

        user_message = _format_changes(changes, before_file, after_file)

        if console:
            console.print()
            console.rule("[bold blue]AI Engineering Analysis")
            console.print()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text = "".join(
            block.text
            for block in response.content
            if hasattr(block, "text") and block.text
        )

        if console:
            console.print(Markdown(text))

        return text
