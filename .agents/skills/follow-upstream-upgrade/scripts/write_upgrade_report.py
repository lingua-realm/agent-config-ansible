#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


def render_template(template_text: str, values: dict[str, str]) -> str:
    rendered = template_text
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    return rendered


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("Usage: write_upgrade_report.py <output_dir> <payload.json>")

    output_dir = Path(argv[1])
    payload_path = Path(argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    output_dir.mkdir(parents=True, exist_ok=True)
    template_path = Path(__file__).resolve().parents[1] / "templates" / "upgrade-report.md.j2"
    template_text = template_path.read_text(encoding="utf-8")
    report_path = output_dir / "upgrade-report.md"
    report_path.write_text(
        render_template(
            template_text,
            {
                "summary": payload.get("summary", ""),
                "impacted_tools": payload.get("impacted_tools", ""),
                "verification": payload.get("verification", ""),
                "next_steps": payload.get("next_steps", ""),
            },
        ),
        encoding="utf-8",
    )

    print(json.dumps({"report_path": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
