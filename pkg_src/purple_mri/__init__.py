"""Purple ex vivo MRI workflow launchers; importing never starts processing."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("purple-mri")
except PackageNotFoundError:
    __version__ = "1.1.0"
