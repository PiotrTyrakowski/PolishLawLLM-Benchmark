from pathlib import Path


def get_data_path(*path_parts: str) -> Path:
    # Start from this file and go up to the project root
    file_path = Path(__file__).parent / ".." / ".." / ".." / "data"
    for part in path_parts:
        file_path = file_path / part
    return file_path.resolve()
