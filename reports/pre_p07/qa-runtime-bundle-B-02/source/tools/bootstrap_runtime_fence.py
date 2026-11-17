#!/usr/bin/env python3
"""Build the minimal guarded legacy runner. This module never installs code."""
import ast
import hashlib
from pathlib import Path

LEGACY_SHA = '02b59b6d33b35b1eb147f889562be697519c648d48c19129ddb4af8747e19856'
FENCE_SHA = 'd700e88e585a2dfb4455290421109a7209acb34dd6fd6730afaf24bc3a6fe3a0'
ADDED_NAMES = {'HANDOFF_PENDING', 'RUNTIME_FILES', '_LOADED_RUNTIME',
               '_runtime_signature', '_require_current_runtime'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def legacy_ast(source, strip_fence=False):
    tree = ast.parse(source)
    if strip_fence:
        body = []
        for node in tree.body:
            names = {n.id for n in ast.walk(node.targets[0]) if isinstance(n, ast.Name)} if isinstance(node, ast.Assign) else set()
            if names & ADDED_NAMES or isinstance(node, ast.FunctionDef) and node.name in ADDED_NAMES:
                continue
            if isinstance(node, ast.If) and any(isinstance(n, ast.Name) and n.id == 'HANDOFF_PENDING' for n in ast.walk(node.test)):
                continue
            body.append(node)
        tree.body = body
        class StripCalls(ast.NodeTransformer):
            count = 0
            def visit_Expr(self, node):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == '_require_current_runtime':
                    self.count += 1
                    return None
                return node
        strip = StripCalls()
        tree = strip.visit(tree)
        if strip.count != 3:
            raise ValueError('Expected precisely three admission call sites')
    return ast.dump(tree, include_attributes=False)


def build(legacy, reviewed_fence):
    if sha(legacy) != LEGACY_SHA or sha(reviewed_fence) != FENCE_SHA:
        raise ValueError('Unreviewed input SHA; refuse approximate patch')
    old, current = legacy.decode(), reviewed_fence.decode()
    start = current.index('# Installation uses a separate, cold maintenance process')
    end = current.index('DEFAULT_PHASES=', start)
    patch = current[start:end]
    target = old.replace('DEFAULT_PHASES=', patch + 'DEFAULT_PHASES=', 1)
    replacements = [
        ('        self.state_path=self.root/', '        _require_current_runtime(self.root)\n        self.state_path=self.root/'),
        ('    def exclusive(self):\n', '    def exclusive(self):\n        _require_current_runtime(self.root)\n'),
        ('            self.fd=fd\n', '            _require_current_runtime(self.root)\n            self.fd=fd\n'),
    ]
    for before, after in replacements:
        if target.count(before) != 1:
            raise ValueError('Ambiguous legacy anchor')
        target = target.replace(before, after, 1)
    if legacy_ast(old) != legacy_ast(target, strip_fence=True):
        raise ValueError('Legacy behavior changed outside the admission fence')
    return target.encode()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('legacy', type=Path)
    p.add_argument('reviewed_fence', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    data = build(a.legacy.read_bytes(), a.reviewed_fence.read_bytes())
    # Never overwrite an installed runner or an existing review candidate.
    with a.output.open('xb') as stream:
        stream.write(data)
    print(sha(data))
