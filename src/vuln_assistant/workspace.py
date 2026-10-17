"""Constrain connector diagnostics to an explicitly selected source directory."""

from pathlib import Path, PureWindowsPath


class TargetError(ValueError):
    pass


class SourceWorkspace:
    def __init__(self, root: Path, max_bytes: int = 262_144):
        self.root = root.resolve(strict=True)
        if not self.root.is_dir():
            raise TargetError("Workspace must be a directory")
        self.max_bytes = max_bytes

    def resolve(self, relative_path: str) -> Path:
        windows_path = PureWindowsPath(relative_path)
        candidate = Path(relative_path)
        if (
            not relative_path
            or candidate.is_absolute()
            or windows_path.drive
            or windows_path.root
            or ".." in windows_path.parts
            or ".." in candidate.parts
            or ":" in relative_path
        ):
            raise TargetError("Target must be a relative path inside the selected workspace")
        try:
            resolved = (self.root / candidate).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise TargetError("Target cannot be resolved") from exc
        if not resolved.is_relative_to(self.root):
            raise TargetError("Target escapes the workspace")
        if not resolved.is_file() or resolved.suffix.lower() != ".py":
            raise TargetError("The current connector accepts individual Python files only")
        if resolved.stat().st_size > self.max_bytes:
            raise TargetError("Target exceeds the configured size limit")
        return resolved
