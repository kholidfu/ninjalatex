import os
from jinja2 import Environment, FileSystemLoader
import hashlib
import subprocess
from unidecode import unidecode
import sys
import random
import logging
import pymongo
import re


"""
credit: http://pythonadventures.wordpress.com/2014/02/25/jinja2-example-for-generating-a-local-file-using-a-template/

1. create .tex template
2. put some variables in it
3. generate each .tex file
4. convert it to pdf with pdftolatex
5. done!
"""

# mongo conf
c = pymongo.Connection()

# logging conf
logging.basicConfig(filename="build.log", level=logging.DEBUG, 
                    format="%(asctime)s %(message)s", 
                    datefmt="%m/%d/%Y %I:%M:%S %p")


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
# template_collection = ["index.tex", "index2.tex"]  # <= wiring + auto templates
template_collection = ["index3.tex", "index4.tex"]  # <= hanan+maxi
# template_collection = ["index5.tex", "index6.tex"]  # <= general + database connected


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
    # database call
    # dbterms = c["terms"]
    dbterms = c["semras"]
    dbpdfs = c["pdfs"]
    tags = dbterms.command('text', 'term', search=title, limit=25)
    tags = [tag['obj'] for tag in tags['results']]
    prewords = [tag['term'] for tag in tags]  # related title from database

    # calling pdfs
    snippets = dbpdfs.command("text", "pdf", search=title, limit=50)
    snippets = [snippet['obj'] for snippet in snippets['results']]

    # pake slugify biar bersih dari non char
    snippets = [slugify(unidecode(snippet['snippet'])).replace("-", " ") for snippet in snippets]  # related snippet from dbase
    tags = "\n\n".join(tag['term'] for tag in tags)

    # output/generated file
    fname = "output.tex"

    # generate unique id for each book (mimic isbn)
    uid = hashlib.md5(title).hexdigest().upper()
    # generate random color for cover needs
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    # keywords for pdf metada
    keywords = ",".join(["read online", "ebook"] + title.split() + ["free", "download"])

    # spinned content goes here
    # tex1.txt
    with open("tex1.txt") as f:
        tex1 = f.read()
    tex1 = tex1.split("\n\n")
    random.shuffle(tex1)
    tex11 = spin(tex1[0]) % (prewords[0], prewords[1])
    tex12 = spin(tex1[1]) % (prewords[0], prewords[1])
    tex13 = spin(tex1[2]) % (prewords[0], prewords[1])
    tex14 = spin(tex1[3]) % (prewords[0], prewords[1])

    # tex2.txt
    with open("tex2.txt") as f:
        tex2 = f.read()
    tex2 = tex2.split("\n\n")
    random.shuffle(tex2)
    tex2 = tex2[0]
    tex2 = spin(tex2)
    tex2 = tex2 % prewords[0]

    # tex3.txt
    with open("tex3.txt") as f:
        tex3 = f.read()
    tex3 = tex3.split("\n\n")
    random.shuffle(tex3)
    tex31 = spin(tex3[0])
    tex32 = spin(tex3[1])
    tex33 = spin(tex3[2])

    # construct landing page url ambil dari prewords
    lander = ["http://www.seepdf.com/download/%s" % w.title().strip() for w in prewords]

    # context is the container of our data
    context = {"title": title, 
               "uid":uid, 
               "colors": colors,
               "keywords": keywords, 
               "tex11": tex11,  # paragraf 1
               "tex12": tex12,  # paragraf 2
               "tex13": tex13,  # paragraf 3
               "tex14": tex14,  # paragraf 4
               "tex2": tex2,
               "tex31": tex31,  # paragraf 1
               "tex32": tex32,  # paragraf 2
               "tex33": tex33,  # paragraf 3
               "tags": tags, 
               "prewords": prewords,
               "snippets": snippets, 
               "lander": lander}
    # write to the file
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
    usage:
    python pdfgen.py setem.txt assets1
    setem.txt <= source setem
    assets1   <= destination folder to prevent collision
    """
    # build path and pdf container dir if not exists
    home = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(home, sys.argv[2])  # dibikin flexible dari cmd
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)
    # build list of titles
    fsource = sys.argv[1]
    with open(fsource) as f:
        titles = [title.strip() for title in f.readlines()]
    # loop through list of bunch setem
    # supress the subprocess output
    FNULL = open(os.devnull, 'w')
    count = 1
    for title in titles:
        if title:
            logging.info("%s. generating pdf for: %s" % (count, title))
            logging.info(sys.argv[1])
            # choose randomed template
            choosen_template = random.choice(template_collection)
            # generate the tex file
            create_tex(choosen_template, title)
            # generate the pdf file
            # subprocess.call(["pdflatex", "--shell-escape", "output.tex"])
            subprocess.call(["pdflatex", "--shell-escape", "output.tex"], 
                           stdout=FNULL, stderr=subprocess.STDOUT)
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
