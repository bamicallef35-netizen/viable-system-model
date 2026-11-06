"""Write docs/index.html from the library's own demo output.

The live page is the model's output, not a re-implementation: `python -m vsm
demo` is rendered into a <pre>, so the page can never drift from the code.
Run after any change:  python scripts/make_docs.py
"""

from __future__ import annotations

import html
from pathlib import Path

from vsm.cli import demo

ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "docs" / "index.html"
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>viable-system-model / Benjamin Micallef</title>
<meta name="description" content="Stafford Beer's Viable System Model as a tested Python library, with Ashby's variety arithmetic done exactly. This page is the library's own demo output.">
<link rel="stylesheet" href="./style.css">
</head>
<body>
<main>
  <header class="site">
    <h1>viable-system-model</h1>
    <p class="meta">Stafford Beer's Viable System Model as a typed, tested Python library / Ashby's requisite variety done exactly / this page is the output of <code>python -m vsm demo</code>, rendered by scripts/make_docs.py / <a href="https://github.com/benmicallef/viable-system-model">source</a> / <a href="https://benmicallef.github.io/">benmicallef</a></p>
  </header>

  <figure class="demo">
    <pre class="readout" style="padding: var(--s-3); border: 0; white-space: pre; font-size: var(--fs-0); line-height: 1.5;">{html.escape(demo())}</pre>
    <figcaption>a three-level factory: the recursion and its functions; Ashby's requisite-variety test per plant; Beer's variety engineering bringing the short plant into balance; the algedonic alarm escalating from line-S2 to the top; and a structurally broken system flagged.</figcaption>
  </figure>

  <section class="text">
    <h2>what this can and cannot prove</h2>
    <p>It can demonstrate the internal logic of the VSM as Beer specified it; compute Ashby's variety and the requisite-variety inequality exactly over a finite state space you stipulate; show, by test, that an algedonic alarm propagates up the recursion exactly when the model's own rule says it should; and serve as an executable, cited glossary of cybernetic regulation.</p>
    <p>It cannot prove any real organization is viable or predict its behaviour, validate the VSM as a theory of organizations, control any robot, or measure real-world variety. The algedonic rule — a threshold held for a timeout — is my operationalization; Beer described the channel and wrote no algorithm.</p>
    <p class="meta">37 tests, two of them Hypothesis properties / mypy --strict / zero runtime dependencies / MIT / <a href="https://github.com/benmicallef/viable-system-model">README, THEORY.md and citations</a></p>
  </section>
</main>
</body>
</html>
"""
out.write_text(page)
print(f"wrote {out.relative_to(ROOT)} ({len(page)} bytes)")
