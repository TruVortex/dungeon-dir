import os
import platform
import subprocess

from pathlib import Path


class FilesystemExplorer:
    def __init__(self):
        self.current_path = Path.cwd()

    def get_contents(self):
        folders = []
        files = []
        try:
            for item in self.current_path.iterdir():
                if item.name.startswith('.'):
                    continue
                if item.is_dir():
                    folders.append(item)
                else:
                    files.append(item)
        except PermissionError:
            pass
        folders.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())
        return folders, files

    def change_directory(self, target_path: Path):
        if target_path.exists() and target_path.is_dir():
            self.current_path = target_path.resolve()

    def open_file(self, filepath: Path) -> str | None:
        """Opens a file using the host OS's default application."""
        try:
            current_os = platform.system().lower()
            if "windows" in current_os:
                os.startfile(filepath)
            elif "darwin" in current_os:
                subprocess.run(["open", str(filepath)], check=True)
            else:
                subprocess.run(["xdg-open", str(filepath)], check=True)
        except Exception as e:
            return f"Failed to open: {str(e)}"
        return None
