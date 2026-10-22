"""Support ``python -m purple_mri`` alongside the console command."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
