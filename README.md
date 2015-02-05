ninjalatex
==========

the marriage of jinja2 templating engine with latex

Goals
-----

built beautiful pdf file with latex type-setting

How to Use:
-----------

#### Dependencies

You MUST have texlive installed in your Ubuntu, the package is quite
huge, ~900Mb.

``sudo apt-get install texlive texlive-base texlive-latex-extra
texlive-pstricks``

#### Clone and install

1. ``git clone https://github.com/sopier/ninjalatex``
2. ``cd ninjalatex``
3. ``virtualenv .``
4. ``. bin/activate``
5. ``pip install -r requirements.txt``

#### Usage

``python pdfgen.py path/to/your/setem.txt assets_dir``

#### Note

setem.txt example:

``wiring diagram satu``

``dua wiring diagram``

``wiring tiga diagram``
