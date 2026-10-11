#!/usr/bin/env python3
"""Read saved diagnostic logs only; never executes a verifier or edits evidence."""
import argparse
import json
import re
from pathlib import Path


def inspect(text):
    nodes, visits, dead, pending = {}, set(), [], None
    for line in text.splitlines():
        if line.startswith('AST_STMT '):
            pending = line
        match = re.match(r'(REGISTER|EXEC|DEAD) (\d+) (.*)', line)
        if match:
            kind, identity, position = match.groups()
            identity = int(identity)
            if kind == 'REGISTER':
                if pending:
                    nodes.setdefault(identity, []).append(pending)
                pending = None
            elif kind == 'EXEC':
                visits.add(identity)
            else:
                dead.append({'physical_id': identity, 'position': position,
                             'registrations': nodes.get(identity, []),
                             'visited': identity in visits})
    return {'dead_nodes': dead, 'registered_physical_locations': len(nodes),
            'visited_physical_locations': len(visits),
            'diagnostic_complete': bool(dead) and all(
                x['registrations'] and not x['visited'] for x in dead),
            'proof_credit': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.log.read_text(errors='replace')), indent=2))


if __name__ == '__main__':
    main()
