import os
from pathlib import Path


DESCRIPTION = "Report bytes used by common cache and build directories"
CACHE_DIRECTORIES = ("__pycache__", ".pytest_cache", "node_modules", "dist")


def register(parser) -> None:
    parser.add_argument("--path", default=".", help="Root directory to inspect (default: .)")


def _raise_walk_error(error: OSError) -> None:
    raise error


def _cache_sizes(root: Path) -> dict[str, int]:
    sizes = dict.fromkeys(CACHE_DIRECTORIES, 0)
    for directory, _, files in os.walk(root, onerror=_raise_walk_error, followlinks=False):
        folder = Path(directory)
        relative = folder.relative_to(root)
        # Attribute each file to its nearest matching directory.
        cache = next(
            (part for part in reversed((root.name, *relative.parts)) if part in sizes),
            None,
        )
        if cache is None:
            continue

        for name in files:
            path = folder / name
            try:
                if not path.is_symlink() and path.is_file():
                    sizes[cache] += path.stat(follow_symlinks=False).st_size
            except FileNotFoundError:
                # Build tools may remove files while an audit is running.
                continue
    return sizes


def run(args) -> int:
    root = Path(args.path)
    try:
        if root.is_symlink():
            print(f"[!] Cache audit root cannot be a symbolic link: {root}")
            return 1
        sizes = _cache_sizes(root.resolve(strict=True))
    except OSError as error:
        print(f"[!] Could not audit cache sizes: {error}")
        return 1

    for name, size in sizes.items():
        print(f"{name}: {size:,} bytes")
    print(f"Total: {sum(sizes.values()):,} bytes")
    return 0
