Maintainer release process
==================================

Version 1.1.0 is already published on PyPI. Do not upload rebuilt files under
that version. Preserve its Python source when creating the matching Git tag;
documentation may be updated to reflect subsequent validation results.
The build/upload procedure below is a reference for preparing releases, not an
instruction to upload 1.1.0 again.

Keep the root and ``pkg_src`` project versions aligned at ``1.1.0``. The Git tag
and Docker tag use ``v1.1.0``. The Python distribution version has no leading v.
Run from a clean checkout containing the intended release changes:

.. code-block:: bash

   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install build twine -r docs/requirements.txt
   python -m pip install -e .
   python -m unittest discover -s tests -v
   sphinx-build -W --keep-going -b html docs/source docs/_build/html
   python -m build
   python -m twine check --strict dist/purple_mri-1.1.0-py3-none-any.whl dist/purple_mri-1.1.0.tar.gz

Inspect the wheel and sdist. They must not contain MRI, model weights, container
images, personal license files, or credentials. Test the wheel in a clean virtual
environment outside the checkout. The added CI validates package builds and docs;
it does not publish to PyPI automatically.

Commit and merge the reviewed release changes in the repository, then create
and push ``v1.1.0`` on that commit. Do not move an existing tag silently. Publish
only if this version is available under the maintained PyPI project. PyPI does
not allow replacing an existing uploaded distribution with different bytes.

.. code-block:: bash

   python -m twine upload --username __token__ \
     dist/purple_mri-1.1.0-py3-none-any.whl \
     dist/purple_mri-1.1.0.tar.gz

Use the PyPI project's authorized token at the local prompt, or a configured
trusted publishing workflow. Never paste tokens into chat or commit them.
Confirm the intended project licensing before distribution; this refactor does
not invent a new license for the repository or its dependencies.

Read the Docs
---------------------

The repository includes ``.readthedocs.yaml`` using ``docs/source/conf.py`` and
pinned documentation requirements. A matching ``readthedocs.yaml`` is retained
for the existing project's historical configuration path. Use one selected path
in the Read the Docs project settings and keep their contents equivalent.

Confirm the project points to the correct repository and default branch, trigger
a build after merge, and enable the ``v1.1.0`` version after tagging. Inspect the
hosted build log and verify installation, quick-start, and CLI pages. A local
successful Sphinx build does not mean the hosted site was deployed.

References
------------------

* `Python packaging and upload guide <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_
* `Read the Docs configuration reference <https://docs.readthedocs.com/platform/stable/config-file/v2.html>`_
