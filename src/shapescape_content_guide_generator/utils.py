from pathlib import Path

def filter_paths(
        root_path: Path,
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None) -> list[Path]:
    '''
    Returns a list FILE of paths starting from root_path that matched the
    search patterns but didn't match exclude_patterns
    '''
    if isinstance(search_patterns, str):
        search_patterns = [search_patterns]
    if exclude_patterns is None:
        exclude_patterns = []
    elif isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    paths: list[Path] = []
    for pattern in search_patterns:
        for path in root_path.glob(pattern):
            if not path.is_file():
                continue
            paths.append(path)
    for pattern in exclude_patterns:
        for path in root_path.glob(pattern):
            if not path.is_file():
                continue
            paths.remove(path)
    return sorted(list(set(paths) - set(exclude_patterns)))
