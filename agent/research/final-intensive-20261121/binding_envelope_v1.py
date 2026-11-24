"""Finite caller-owned receipt integrity profile. Not semantic admission."""
from pathlib import Path, PurePosixPath
import hashlib
import json


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def validate(raw_envelope, trusted, root, overlays=None, missing=None, symlinks=None):
    """Return refusal reasons; source semantics must be reviewed separately.

    Overlays/missing/symlinks are inert research injections. Production integration
    would need race-safe open semantics and independently authorized trust storage.
    """
    overlays = overlays or {}
    missing = missing or set()
    symlinks = symlinks or set()
    reasons = []
    try:
        envelope = json.loads(raw_envelope, object_pairs_hook=unique_object)
    except (ValueError, TypeError, UnicodeError) as error:
        return ['invalid envelope: '+str(error)]
    if canonical(envelope) != canonical(trusted):
        reasons.append('envelope differs from caller-owned frozen anchor')
    if not isinstance(envelope, dict) or not isinstance(envelope.get('dependencies'), list):
        return reasons+['missing dependency inventory']
    seen = set()
    for item in envelope['dependencies']:
        if not isinstance(item, dict):
            reasons.append('invalid dependency entry')
            continue
        name = item.get('path')
        if not isinstance(name, str):
            reasons.append('invalid dependency path')
            continue
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            reasons.append('unsafe dependency path: '+name)
            continue
        if name in seen:
            reasons.append('duplicate dependency: '+name)
        seen.add(name)
        target = root / name
        parts = [root.joinpath(*relative.parts[:i]) for i in range(1, len(relative.parts)+1)]
        if name in symlinks or any(path.is_symlink() for path in parts):
            reasons.append('symlink dependency refused: '+name)
            continue
        if name in missing or not target.is_file():
            reasons.append('missing dependency: '+name)
            continue
        raw = overlays[name] if name in overlays else target.read_bytes()
        if digest(raw) != item.get('sha256') or len(raw) != item.get('bytes'):
            reasons.append('dependency bytes mismatch: '+name)
    return reasons
