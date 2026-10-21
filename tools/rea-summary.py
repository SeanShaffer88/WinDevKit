#!/usr/bin/env python3
"""Summarize REA JSON without turning partial/error evidence into success.

rea-summary.py report.json --out summary.json
Returns 0 only for a complete evidence envelope, 1 for blocked/partial output,
and 2 for malformed or unknown envelopes. Does not run target applications.
"""
import argparse
import json
from pathlib import Path
import sys


def summarize(payload):
    if not isinstance(payload, dict):
        raise ValueError('expected a JSON object')
    blocked = bool(payload.get('error'))
    observation = payload.get('details', {}).get('partial_observation') if blocked else payload
    if not isinstance(observation, dict) or not observation.get('evidence_id'):
        if blocked:
            return {'status': 'blocked', 'code': payload.get('code'), 'reason': payload.get('message') or payload['error'], 'evidence_id': None}
        raise ValueError('unrecognized REA evidence envelope; inspect raw report')
    normalized = observation.get('normalized_result') or {}
    return {
        'status': 'partial' if blocked else 'evidence-returned',
        'code': payload.get('code') if blocked else None,
        'reason': payload.get('message') if blocked else None,
        'evidence_id': observation['evidence_id'],
        'subject_digest': observation.get('subject', {}).get('digest'),
        'operation': observation.get('operation'),
        'confidence': observation.get('confidence'),
        'source_selection': normalized.get('source_selection'),
        'limitations': observation.get('limitations', []),
        'interpretation': 'Static evidence does not establish runtime behavior; review selection and limitations before drawing feature conclusions.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        if args.report.stat().st_size > 32 * 1024 * 1024:
            raise ValueError('report exceeds 32 MiB; reduce REA selection or output')
        result = summarize(json.loads(args.report.read_text(encoding='utf-8')))
        text = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if args.out:
            args.out.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
    except (OSError, ValueError, TypeError, AttributeError) as err:
        print(f'REA SUMMARY FAILED: {err}', file=sys.stderr)
        return 2
    return 1 if result['status'] in ('blocked', 'partial') else 0


if __name__ == '__main__':
    sys.exit(main())
