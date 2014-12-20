import os
from jinja2 import Environment, FileSystemLoader


"""
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


def create_index_html():
    fname = "output.html"
    urls = ["example.com", "example.net", "example.co.id"]
    context = {
        "urls": urls
        }

    with open(fname, "w") as f:
        html = render_template("index.html", context)
        f.write(html)


if __name__ == "__main__":
    create_index_html()
