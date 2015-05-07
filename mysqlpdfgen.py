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

lim = 1  # num of pdf generated
results = [i for i in results if i[3]][:lim]

# build clean slug for filename
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

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


from random import randrange
from datetime import timedelta
from datetime import datetime

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

        
def create_tex(template, title, author):
    """
    built a tex file using database and spinned content (*.txt)
    """
    # define data needed
    uid = hashlib.md5(title).hexdigest().upper()
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    image = "thumb.jpg"
    # spinned content goes here
    # book_fafifu.txt
    with open("book_fafifu.txt") as f:
        tex1 = f.read()
        tex1 = tex1.split("\n\n")
        random.shuffle(tex1)
        tex11 = spin(tex1[0]) % (title, author)
        tex12 = spin(tex1[1]) % (title, title)
        tex13 = spin(tex1[2]) % (title, title)

    # book_related_fafifu.txt
    
    # generate random date
    d1 = datetime.strptime('1/1/2009 4:50 AM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.strptime(datetime.now().strftime("%m/%d/%Y %I:%M %p"), '%m/%d/%Y %I:%M %p')

    import time
    t = time.localtime()
    suffix = 'st' if t.tm_mday in [1,21,31] else 'nd' if t.tm_mday in [2, 22] else 'rd' if t.tm_mday in [3, 23] else 'th'

    rand_date = random_date(d1, d2).strftime('%d%%s of %B %Y %I:%M:%S %p') % suffix

    # ini variable ngambil dari related search di mysql lho ya
    with open("book_related_fafifu.txt") as f:
        related_text_raw = f.read()
        related_text = spin(related_text_raw) % (title, author, rand_date, title)

    # context is the container of our data
    context = {
        "title": title,
        "colors": colors,
        "image": image,
        "author": author,
        "uid": uid,
        "tex11": tex11,
        "tex12": tex12,
        "tex13": tex13,
        "related": related_text,
    }
    # write to the file
    fname = "output.tex"
    with open(fname, "w") as f:
        tex = render_template(template, context)
        f.write(tex)


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


if __name__ == "__main__":
    """
    """
    titles = [i[1] for i in results]

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
            authors = [i[2] for i in results]
            create_tex(choosen_template, title, authors[count-1])
            # download the image
            url = [i[3] for i in results][count-1]
            io = urllib2.urlopen(url).read()
            with open("thumb.jpg", "w") as f:
                f.write(io)
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
