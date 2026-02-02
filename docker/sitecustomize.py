import sys
import types
import importlib

try:
    import numpy  # just need numpy to be installed
except Exception as e:
    print("sitecustomize: numpy import failed:", e, file=sys.stderr)
else:
    core_name = "numpy._core"

    # Create or reuse numpy._core
    core_mod = sys.modules.get(core_name)
    if core_mod is None:
        core_mod = types.ModuleType(core_name)
        sys.modules[core_name] = core_mod

    # Mark it as a package so numpy._core.multiarray works
    if not hasattr(core_mod, "__path__"):
        core_mod.__path__ = []

    def alias_submodule(subname, real_mod_name):
        """
        Create numpy._core.<subname> that forwards to numpy.core.<something>.
        """
        full_alias = f"{core_name}.{subname}"
        try:
            real_mod = importlib.import_module(real_mod_name)
        except Exception as e:
            print(
                f"sitecustomize: could not import {real_mod_name} "
                f"for alias {full_alias}: {e}",
                file=sys.stderr,
            )
            alias_mod = types.ModuleType(full_alias)
        else:
            alias_mod = types.ModuleType(full_alias)
            alias_mod.__dict__.update(real_mod.__dict__)
        sys.modules[full_alias] = alias_mod

    # Alias the “new” NumPy 2.x-style paths to the old ones
    alias_submodule("multiarray", "numpy.core.multiarray")
    alias_submodule("overrides", "numpy.core.overrides")

    print("sitecustomize: created alias modules for numpy._core.*", file=sys.stderr)
