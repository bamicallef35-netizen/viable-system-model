"""``python -m vsm demo`` — run the bundled factory model end to end."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from . import examples
from .algedonic import propagate
from .render import render_events, render_requisite, render_tree

THRESHOLD = 0.6
TIMEOUT = 3


def demo() -> str:
    """The whole demo as one deterministic string."""
    root = examples.factory()
    sections: list[str] = []

    sections.append("THE RECURSION")
    sections.append(render_tree(root))
    sections.append(
        f"structurally viable: {'yes' if root.is_structurally_viable() else 'no'}"
        f"  (depth {root.depth()})"
    )

    sections.append("")
    sections.append("REQUISITE VARIETY (Ashby), per plant")
    sections.append(render_requisite(examples.factory_requisite()))

    before, after = examples.variety_engineering()
    sections.append("")
    sections.append("VARIETY ENGINEERING (Beer) on Plant South")
    sections.append(render_requisite([("before", before), ("after", after)]))
    sections.append("attenuate the environment by 1.5 bits, amplify the regulator by 1.0 bit")

    sections.append("")
    sections.append(f"ALGEDONIC CHANNEL  threshold {THRESHOLD}  timeout {TIMEOUT} readings")
    events = propagate(root, examples.factory_readings(), threshold=THRESHOLD, timeout=TIMEOUT)
    sections.append(render_events(events))

    broken = examples.imbalanced()
    sections.append("")
    sections.append("A STRUCTURALLY BROKEN SYSTEM")
    sections.append(render_tree(broken))
    missing = [
        f"{sub.name}: {', '.join(sub.missing_functions())}"
        for _, u in broken.walk()
        if (sub := u.subsystem) is not None and sub.missing_functions()
    ]
    sections.append("missing: " + ("; ".join(missing) if missing else "nothing"))
    sections.append(
        f"structurally viable: {'yes' if broken.is_structurally_viable() else 'no'}"
    )
    return "\n".join(sections)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["demo"]:
        print(demo())
        return 0
    print("usage: python -m vsm demo", file=sys.stderr)
    return 2
