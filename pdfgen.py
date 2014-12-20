import os
from jinja2 import Environment, FileSystemLoader


"""
source: http://pythonadventures.wordpress.com/2014/02/25/jinja2-example-for-generating-a-local-file-using-a-template/

1. create .tex template
2. put some variables in it
3. generate each .tex file
4. convert it to pdf with pdftolatex
5. done!
"""


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_tex():
    # output/generated file
    fname = "output.tex"
    # variables we will use in template
    title = "2001 ford taurus automatic transmission wiring schematic"
    # context is the container of our data
    context = {"title": title}

    # write to the file
    with open(fname, "w") as f:
        html = render_template("index.tex", context)
        f.write(html)


if __name__ == "__main__":
    create_tex()
