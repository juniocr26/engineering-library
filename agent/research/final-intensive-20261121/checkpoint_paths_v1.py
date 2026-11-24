"""Resolve recorded research dependencies before assigning archive names."""
from pathlib import Path
def resolve_relative_regular(root,recorded_path):
    root=Path(root).resolve(strict=True)
    if not isinstance(recorded_path,str) or not recorded_path or '\x00' in recorded_path:
        raise ValueError('invalid recorded relative path')
    relative=Path(recorded_path)
    if relative.is_absolute():
        raise ValueError('recorded dependency must be relative')
    lexical=root/relative
    if lexical.is_symlink():
        raise ValueError('symlink leaf is not an admitted regular dependency')
    resolved=lexical.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError('resolved dependency escapes recorded root')
    if not resolved.is_file():
        raise ValueError('resolved dependency is not a regular file')
    return resolved
