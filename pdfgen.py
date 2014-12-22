import os
from jinja2 import Environment, FileSystemLoader
import hashlib
import subprocess
from unidecode import unidecode
import sys
import random


"""
source: http://pythonadventures.wordpress.com/2014/02/25/jinja2-example-for-generating-a-local-file-using-a-template/

1. create .tex template
2. put some variables in it
3. generate each .tex file
4. convert it to pdf with pdftolatex
5. done!
"""


# load the templates dir
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)


# ready to render
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_tex(title):
    # output/generated file
    fname = "output.tex"
    # variables we will use in template
    # title = "2001 ford taurus automatic transmission wiring schematic"
    # generate unique id for each book (mimic isbn)
    uid = hashlib.md5(title).hexdigest().upper()
    # generate random color for cover needs
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    # context is the container of our data
    context = {"title": title, "uid":uid, "colors": colors}

    # write to the file
    with open(fname, "w") as f:
        tex = render_template("index.tex", context)
        f.write(tex)


# build clean slug for filename
import re
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


if __name__ == "__main__":
    # build path and pdf container dir if not exists
    home = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(home, "assets")
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)
    # build list of titles
    fsource = sys.argv[1]
    with open(fsource) as f:
        titles = [title.strip() for title in f.readlines()]
    # loop through list of bunch setem
    for title in titles:
        # generate the tex file
        create_tex(title)
        # generate the pdf file
        subprocess.call(["pdflatex", "--shell-escape", "output.tex"])
        # move the pdf into separate folder
        # folder path => /assets/a/aa
        fname = "%s.pdf" % slugify(unicode(title))
        # build dirpath
        dirname = os.path.join(title[0], "".join(title.split())[:2])
        dirname = os.path.join(asset_dir, dirname)
        # build dir if not exists
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        fpath = os.path.join(asset_dir, dirname, fname)
        subprocess.call(["mv", "output.pdf", fpath])

