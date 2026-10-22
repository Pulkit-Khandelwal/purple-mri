Maintainer documentation and releases
=====================================

Python 1.1.0 is published on PyPI, and the source release is tagged ``v1.1.0``.
Documentation corrections on ``main`` do not replace those distributions, change
the installed package, rebuild the container, or move the release tag.

Documentation-only updates
--------------------------

Use a separate branch and pull request based on current ``main``. Keep runtime
code and package versions unchanged for documentation corrections. The package
README can be corrected in the repository, but the already published PyPI long
description remains part of the original release metadata.

The documentation has three entry points:

* ``README.md``: a short overview, install/run examples, and links.
* ``docs/source/``: the detailed user manual built by Read the Docs.
* ``docker/exvivo_docker.md``: the repository container guide, including the
  historical project-folder Docker layout.

``pkg_src/README.md`` documents the Python launcher. The maintainer build guide
is ``docker/docker_files/README.md``. Keep examples aligned with the actual CLI,
launcher environment variables, and output paths. Preserve the separate research
workflow guides and label their host requirements explicitly.

From a development environment at the repository root, check the package and
build the documentation:

.. code-block:: bash

   python -m pip install -e . -r docs/requirements.txt
   python -m unittest discover -s tests -v
   sphinx-build -W --keep-going -b html docs/source docs/_build/html

Review the generated installation, quick-start, Docker, output, and parcellation
pages. The existing GitHub workflow runs package checks and a strict Sphinx build;
it does not run MRI inference or publish packages. An optional external link
check is ``sphinx-build -b linkcheck docs/source docs/_build/linkcheck``; review
network/authentication failures separately from genuinely broken links.

Deploy to Read the Docs
-----------------------

The repository contains ``.readthedocs.yaml`` using ``docs/source/conf.py`` and
pinned documentation requirements. The matching ``readthedocs.yaml`` is retained
for the existing project's historical configuration path. Use the selected path
in the project settings and keep both files equivalent.

1. Merge the documentation pull request after checks pass.
2. In Read the Docs, confirm the project repository is
   ``Pulkit-Khandelwal/purple-mri`` and the default branch is ``main``.
3. Open **Builds** and check the ``latest`` build. If the Git integration has not
   triggered it, start a build for ``latest`` manually.
4. Verify the build's Git commit matches the merged change, then wait for a
   successful build before checking the public pages.
5. Open the live installation, quick-start, direct Docker, output, and
   parcellation pages. Confirm the new content and navigation are present.

``latest`` follows the default branch. The ``v1.1.0`` documentation version follows
its existing tag, so rebuilding that version will not include later commits on
``main``. ``stable`` normally follows the greatest stable release tag. Use the
current ``latest`` links for this documentation refresh; keep the tagged snapshot
as the release record. Do not force-move ``v1.1.0`` to update documentation.
A documentation maintenance branch can be configured separately if needed.

Enable the ``v1.1.0`` version under **Versions** if a tagged snapshot is desired.
A local successful Sphinx build establishes that the sources build; it does not
establish that the hosted site has deployed. See the official
`Read the Docs version guide <https://docs.readthedocs.com/platform/stable/versions.html>`_
and `build process <https://docs.readthedocs.com/platform/stable/builds.html>`_.

Future Python releases
----------------------

Use a new version for Python functionality changes. Keep the root and
``pkg_src/pyproject.toml`` versions aligned, update release notes, and test the
built wheel in a clean environment outside the checkout. The distribution
version has no leading ``v``; Git release tags use that prefix.

.. code-block:: bash

   python -m pip install build twine
   python -m build
   python -m twine check --strict dist/*

Run these commands in a clean release checkout so ``dist`` contains only the
intended release. Inspect the wheel and source archive: no MRI, model weights,
container images, personal license files, or credentials should be bundled.
Publish only the explicit reviewed artifacts for the new version, following the
`Python packaging guide <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_.
Do not rebuild and upload 1.1.0 again. Package publication, Docker publication,
and documentation deployment are separate operations.
