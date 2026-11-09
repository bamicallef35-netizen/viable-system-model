"""Run the bundled three-level factory: python examples/factory.py"""

from vsm import examples, propagate
from vsm.render import render_events, render_requisite, render_tree

root = examples.factory()
print(render_tree(root))
print()
print(render_requisite(examples.factory_requisite()))
print()
print(render_events(propagate(root, examples.factory_readings(), threshold=0.6, timeout=3)))
