# Package changelog

## 1.1.0

- Align package version 1.1.0 with the v1.1.0 container release.
- Track container identity before start and record its actual exit status.
- Stop only the verified run container on Ctrl+C; retain failed/uncertain runs.
- Add full installation, workflow, output, QC, Singularity, and publishing docs.
- Configure strict Read the Docs builds and package/documentation CI.
- Add a lightweight `purple-mri` CLI: run, pull, doctor, models and legacy-surface.
- Route current workflows through the combined `v1.1.0` Docker image; preserve
  Task2732 selection in the repository launcher for future image builds.
- Validate inputs, stages, hemisphere/license and fresh output directories.
- Use subprocess argument lists, propagate errors and record immutable image IDs.
- Keep the old seven-argument RH-only native entry point and installed shell tools.
- Resolve native helper scripts relative to their installed location, use the
  package Python interpreter for mesh decimation, remove a private FreeSurfer
  template path, and stop native helpers on command failures.
- Move heavy native dependencies into the `legacy` extra and include missing pandas.
- Replace conflicting root Flit configuration with the same setuptools package
  definition used by `pkg_src`; include shell resources in wheels and sdists.
- Replace old CRUISE/two-container instructions with current usage and limitations.

This is a packaging/launcher refactor, not a change to scientific label mappings,
surface placement parameters or trained weights. No PyPI release has been made.
