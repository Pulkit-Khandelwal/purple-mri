Python entry point
==========================

The supported public interface is the command line. It can also be invoked as
``python -m purple_mri``. Internal orchestration functions are not a stable
scientific Python API.

.. autofunction:: purple_mri.cli.main

The callable returns an integer status when execution reaches its handler;
argument parsing can raise ``SystemExit`` for help or invalid arguments. For
external orchestration, prefer a subprocess argument list invoking ``purple-mri``
and inspect its return code and ``purple_run.json``.
