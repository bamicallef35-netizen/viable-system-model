"""A deliberately non-viable structure, flagged: python examples/imbalanced.py"""

from vsm import examples
from vsm.render import render_tree

root = examples.imbalanced()
print(render_tree(root))
for _, unit in root.walk():
    if unit.subsystem is not None and unit.subsystem.missing_functions():
        print(f"{unit.subsystem.name} is missing: {', '.join(unit.subsystem.missing_functions())}")
print("structurally viable:", root.is_structurally_viable())
