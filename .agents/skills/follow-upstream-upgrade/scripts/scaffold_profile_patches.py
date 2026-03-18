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
        raise SystemExit("Usage: scaffold_profile_patches.py <output_dir> <payload.json>")

    output_dir = Path(argv[1])
    payload_path = Path(argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    template_path = Path(__file__).resolve().parents[1] / "templates" / "profile-patch.md.j2"
    template_text = template_path.read_text(encoding="utf-8")

    generated_profiles: list[str] = []
    for profile in payload.get("profiles", []):
        profile_name = profile["name"]
        profile_dir = output_dir / "profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        draft_path = profile_dir / "patch-draft.md"
        rendered = render_template(
            template_text,
            {
                "profile": profile_name,
                "summary": profile.get("summary", ""),
                "suggested_changes": profile.get("suggested_changes", ""),
                "notes": profile.get("notes", ""),
            },
        )
        draft_path.write_text(rendered, encoding="utf-8")
        generated_profiles.append(profile_name)

    print(
        json.dumps(
            {
                "generated_profiles": generated_profiles,
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
