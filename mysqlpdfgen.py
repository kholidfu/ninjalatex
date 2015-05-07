import MySQLdb
import os
from jinja2 import Environment, FileSystemLoader
import hashlib
import subprocess
from unidecode import unidecode
import sys
import random
import re
import logging
import urllib2


# dbase part global
con = MySQLdb.connect(host="localhost", user="root", passwd="vertigo")
cur = con.cursor()
# chandler.execute("SHOW DATABASES")
cur.execute("USE book")
# chandler.execute("SHOW TABLES")
cur.execute("SELECT * FROM coba")
results = cur.fetchall()
results = [i for i in results if i[3]]

# latext part
# latex escaper
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)


def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval


# load the templates dir
PATH = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    autoescape=True,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False,
    variable_start_string = '(((',
    variable_end_string = ')))',
)

# custom filter for latex
env.filters['escape_tex'] = escape_tex

# ready to render
def render_template(template_filename, context):
    return env.get_template(template_filename).render(context)

# randomize template
template_collection = ["book1.tex"]


def spin(content):
    """takes a string like
 
    {Hi|Hello|Good morning}, my name is Matt and I have {something {important|special} to say|a favorite book}.
 
    and randomly selects from the options in curly braces
    to produce unique strings.
    """
    start = content.find('[')
    end = content.find(']')
 
    if start == -1 and end == -1:
        #none left
        return content
    elif start == -1:
        return content
    elif end == -1:
        raise "unbalanced brace"
    elif end < start:
        return content
    elif start < end:
        rest = spin(content[start+1:])
        end = rest.find(']')
        if end == -1:
            raise "unbalanced brace"
        return content[:start] + random.choice(rest[:end].split('|')) + spin(rest[end+1:])

        
def create_tex(template, title):
    """
    built a tex file using database and spinned content (*.txt)
    """
    # define data needed
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    # download the image
    url = [i[3] for i in results][0]
    io = urllib2.urlopen(url).read()
    with open("thumb.jpg", "w") as f:
        f.write(io)
    image = "thumb.jpg"
    # context is the container of our data
    context = {
        "title": title,
        "colors": colors,
        "image": image,
    }
    # write to the file
    fname = "output.tex"
    with open(fname, "w") as f:
        tex = render_template(template, context)
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
    """
    """
    titles = [i[1] for i in results][:1]

    # build path and pdf container dir if not exists
    home = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(home, sys.argv[1])  # dibikin flexible dari cmd
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)

    # supress the subprocess output
    FNULL = open(os.devnull, 'w')
    count = 1
    for title in titles:
        if title:
            logging.info("%s. generating pdf for: %s" % (count, title))
            # choose randomed template
            choosen_template = random.choice(template_collection)
            # generate the tex file
            create_tex(choosen_template, title)
            # generate the pdf file
            subprocess.call(["pdflatex", "--shell-escape", "output.tex"])
            # subprocess.call(["pdflatex", "--shell-escape", "output.tex"], 
            #               stdout=FNULL, stderr=subprocess.STDOUT)
            # move the pdf into separate folder
            # folder path => /assets/a/aa
            fname = "%s.pdf" % slugify(unicode(title))
            # build dirpath
            # dirname = os.path.join(title[0], "".join(title.split())[:2])
            dirname = os.path.join(asset_dir, title[0])  # lgsg 1 dir saja
            # build dir if not exists
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fpath = os.path.join(asset_dir, dirname, fname)
            subprocess.call(["mv", "output.pdf", fpath])
            count += 1
            logging.info("sukses")
            logging.info("==================================================")
        else:
            # prevent processing empty line
            logging.warning("baris kosong bang")
    FNULL.close()
