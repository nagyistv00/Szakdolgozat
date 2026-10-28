"""Constrain analysis to an explicitly selected source directory."""

from pathlib import Path, PureWindowsPath


class TargetError(ValueError):
    pass


class TargetNotFound(TargetError):
    """The path is acceptable but does not exist; distinct from a rejected path."""


SKIPPED_DIRECTORIES = {"__pycache__", "venv", "node_modules", "site-packages"}


class SourceWorkspace:
    def __init__(self, root: Path, max_bytes: int = 262_144, max_files: int = 50):
        self.root = root.resolve(strict=True)
        if not self.root.is_dir():
            raise TargetError("Workspace must be a directory")
        self.max_bytes = max_bytes
        self.max_files = max_files

    def _check_syntax(self, relative_path: str) -> Path:
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
        return candidate

    def _resolve_any(self, relative_path: str) -> Path:
        candidate = self._check_syntax(relative_path)
        unresolved = self.root / candidate
        if not unresolved.exists():
            raise TargetNotFound("Target does not exist in the selected workspace")
        try:
            resolved = unresolved.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise TargetError("Target cannot be resolved") from exc
        if not resolved.is_relative_to(self.root):
            raise TargetError("Target escapes the workspace")
        return resolved

    def _check_file(self, resolved: Path) -> Path:
        if not resolved.is_file() or resolved.suffix.lower() != ".py":
            raise TargetError("Only Python source files can be analysed")
        if resolved.stat().st_size > self.max_bytes:
            raise TargetError("Target exceeds the configured size limit")
        return resolved

    def resolve(self, relative_path: str) -> Path:
        """Resolve one Python file inside the workspace."""
        return self._check_file(self._resolve_any(relative_path))

    def relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def collect(self, relative_path: str) -> list[str]:
        """Return the Python files of a file or directory target as workspace-relative paths.

        Directory traversal skips hidden and environment folders, refuses links that leave
        the workspace and enforces a file-count limit instead of silently truncating.
        """
        resolved = self._resolve_any(relative_path)
        if resolved.is_file():
            return [self.relative(self._check_file(resolved))]
        if not resolved.is_dir():
            raise TargetError("Target is neither a file nor a directory")
        files: list[str] = []
        for path in sorted(resolved.rglob("*.py")):
            inside = path.relative_to(resolved).parts[:-1]
            if any(part.startswith(".") or part in SKIPPED_DIRECTORIES for part in inside):
                continue
            real = path.resolve()
            if not real.is_relative_to(self.root):
                raise TargetError("A file inside the target links outside the workspace")
            files.append(self.relative(self._check_file(real)))
            if len(files) > self.max_files:
                raise TargetError(f"Target contains more than {self.max_files} Python files")
        if not files:
            raise TargetNotFound("The target directory contains no Python files")
        return files
