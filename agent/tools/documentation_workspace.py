"""Bounded descriptor-based filesystem access for explicit local workspaces."""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat


class WorkspaceRefused(ValueError):
    pass


def relative_path(value):
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise WorkspaceRefused("invalid relative path")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or parsed.as_posix() != value or any(
        part in (".", "..", "") or part.startswith(".") for part in value.split("/")
    ):
        raise WorkspaceRefused("unsafe relative path")
    return parsed.parts


def directory_flags():
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise WorkspaceRefused("descriptor/no-follow access unavailable on this platform")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


@contextmanager
def directory(path):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise WorkspaceRefused("workspace root must be an absolute canonical path")
    flags = directory_flags()
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            replacement = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = replacement
        yield descriptor
    finally:
        os.close(descriptor)


@contextmanager
def parent(root_fd, relative, create=False):
    parts = relative_path(relative)
    descriptor = os.dup(root_fd)
    try:
        for component in parts[:-1]:
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=descriptor)
                    os.fsync(descriptor)
                except FileExistsError:
                    pass
            replacement = os.open(component, directory_flags(), dir_fd=descriptor)
            os.close(descriptor)
            descriptor = replacement
        yield descriptor, parts[-1]
    finally:
        os.close(descriptor)


def read(root_fd, relative, maximum):
    with parent(root_fd, relative) as (parent_fd, leaf):
        # Do not block opening a FIFO before the regular-file check below.
        descriptor = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise WorkspaceRefused("not a bounded regular file")
        chunks, size = [], 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > maximum:
                raise WorkspaceRefused("file grew beyond bound")
        after = os.fstat(descriptor)
        fields = lambda st: (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
        if fields(before) != fields(after) or size != after.st_size:
            raise WorkspaceRefused("file changed while reading")
        data = b"".join(chunks)
        return data, {
            "sha256": hashlib.sha256(data).hexdigest(), "size": size,
            "mode": stat.S_IMODE(after.st_mode), "mtime_ns": after.st_mtime_ns,
            "atime_ns": before.st_atime_ns,
        }
    finally:
        os.close(descriptor)


def census(root_fd, maximum=128):
    result = []
    visited = 0

    def walk(descriptor, prefix, depth=0):
        nonlocal visited
        if depth > 16:
            raise WorkspaceRefused("workspace directory depth exceeds bound")
        for name in sorted(os.listdir(descriptor)):
            visited += 1
            if visited > 512:
                raise WorkspaceRefused("workspace entry budget exceeded")
            value = prefix + name
            if len(value.encode("utf-8")) > 1024:
                raise WorkspaceRefused("workspace path exceeds bound")
            relative_path(value)
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name, directory_flags(), dir_fd=descriptor)
                try:
                    walk(child, value + "/", depth + 1)
                finally:
                    os.close(child)
            elif stat.S_ISREG(info.st_mode):
                result.append(value)
                if len(result) > maximum:
                    raise WorkspaceRefused("workspace inventory exceeds bound")
            else:
                raise WorkspaceRefused("symlink or special file in workspace")

    walk(root_fd, "")
    return result


def write_new(root_fd, relative, data, metadata=None):
    with parent(root_fd, relative, create=True) as (parent_fd, leaf):
        descriptor = os.open(
            leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=parent_fd,
        )
        try:
            view = memoryview(data)
            while view:
                written = os.write(descriptor, view)
                if not written:
                    raise WorkspaceRefused("short artifact write")
                view = view[written:]
            if metadata:
                os.fchmod(descriptor, metadata["mode"])
                os.utime(descriptor, ns=(metadata["atime_ns"], metadata["mtime_ns"]))
            os.fsync(descriptor)
            os.fsync(parent_fd)
        finally:
            os.close(descriptor)


def same_root(path, descriptor):
    current = os.stat(path, follow_symlinks=False)
    opened = os.fstat(descriptor)
    return stat.S_ISDIR(current.st_mode) and (
        current.st_dev, current.st_ino
    ) == (opened.st_dev, opened.st_ino)
