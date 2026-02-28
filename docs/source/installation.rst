Installation
============

Local prerequisites
-------------------

Most workflows require:

* FreeSurfer (for surface and atlas resources)
* Python 3.10+ recommended
* Common neuroimaging CLIs (exact tools depend on the scripts you run)

Clone the repository
--------------------

.. code-block:: console

   git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
   cd purple-mri

Python dependencies
-------------------

.. code-block:: console

   python -m venv .venv
   source .venv/bin/activate
   pip install -r dependencies.txt

Documentation dependencies
--------------------------

.. code-block:: console

   pip install -r docs/requirements.txt
