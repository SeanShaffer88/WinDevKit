#!/usr/bin/env python3
"""Validate portfolio v1 records and, optionally, local release bytes. Stdlib only."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

SCHEMA = Path(__file__).resolve().parents[1] / 'schemas/release-evidence-v1.schema.json'


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def contract(value, schema, location='$'):
    """Check the exact small keyword set used by our committed v1 schema.

    This is not a general-purpose JSON Schema implementation. Schema changes
    require reviewing this function and its supported keywords together.
    """
    supported = {'$schema', '$id', 'title', 'type', 'properties', 'required',
                 'additionalProperties', 'items', 'minItems', 'minLength',
                 'minimum', 'pattern', 'enum', 'const'}
    if set(schema) - supported:
        raise ValueError(f'{location}: unsupported schema keywords')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int}
    if 'type' in schema and type(value) is not types[schema['type']]:
        raise ValueError(f'{location}: expected {schema["type"]}')
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{location}: wrong contract version')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{location}: unsupported value')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - value.keys():
            raise ValueError(f'{location}: missing required fields')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and value.keys() - properties.keys():
            raise ValueError(f'{location}: unknown fields')
        for key, child in value.items():
            contract(child, properties[key], f'{location}.{key}')
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ValueError(f'{location}: too few entries')
        for index, child in enumerate(value):
            contract(child, schema['items'], f'{location}[{index}]')
    elif isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            raise ValueError(f'{location}: empty text')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValueError(f'{location}: invalid format')
    elif type(value) is int and value < schema.get('minimum', value):
        raise ValueError(f'{location}: below minimum')


def artifact_path(root, name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or path.is_absolute()
            or '..' in path.parts or str(path) != name or path == PurePosixPath('.')):
        raise ValueError('artifact path must be normalized and relative')
    root = Path(root).resolve(strict=True)
    current = root
    for part in path.parts:
        current = current / part
        attributes = getattr(current.lstat(), 'st_file_attributes', 0)
        if current.is_symlink() or attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
            raise ValueError('artifact links/junctions are not accepted')
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('artifact must be a regular file inside artifact directory')
    return resolved


def validate(record, artifacts_dir=None, preflight=False):
    contract(record, read_json(SCHEMA))
    date.fromisoformat(record['recorded_on'])
    for field, entries in [('checks', record['checks']), ('artifacts', record['artifacts'])]:
        key = 'id' if field == 'checks' else 'path'
        if len({entry[key] for entry in entries}) != len(entries):
            raise ValueError(f'duplicate {field} identity')
    # Validate path syntax even when bytes are not provided.
    for artifact in record['artifacts']:
        name = artifact['path']
        path = PurePosixPath(name)
        if ('\\' in name or ':' in name or path.is_absolute() or '..' in path.parts
                or str(path) != name or path == PurePosixPath('.')):
            raise ValueError('invalid artifact path')
        if artifacts_dir is not None:
            target = artifact_path(artifacts_dir, name)
            with target.open('rb') as stream:
                observed = hashlib.file_digest(stream, 'sha256').hexdigest()
            if observed != artifact['sha256'] or target.stat().st_size != artifact['size']:
                raise ValueError(f'artifact bytes differ: {name}')
    if preflight:
        if artifacts_dir is None:
            raise ValueError('release preflight requires --artifacts-dir')
        if record['source']['tree_state'] != 'clean':
            raise ValueError('release preflight requires recorded clean source')
        if any(c['status'] != 'passed' for c in record['checks']):
            raise ValueError('release preflight requires all listed checks passed')
        if record['release']['maturity'] == 'stable' and record['real_machine']['status'] != 'passed':
            raise ValueError('stable preflight requires recorded real-machine acceptance')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('--artifacts-dir', type=Path)
    parser.add_argument('--release-preflight', action='store_true')
    args = parser.parse_args()
    try:
        validate(read_json(args.record), args.artifacts_dir, args.release_preflight)
    except (ValueError, OSError, KeyError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 1
    mode = 'record and local artifact bytes' if args.artifacts_dir else 'record structure only'
    print(f'Validated {mode}; execution claims, tag/source binding, notices and signatures need independent review.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
