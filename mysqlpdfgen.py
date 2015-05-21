# python mysqlpdfgen.py wikimedianetwork.com books

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
from random import randrange
from datetime import timedelta
from datetime import datetime
import time


# set default encoding
reload(sys)  
sys.setdefaultencoding('utf8')

# STATIC VAR
LIM = 100000  # num of pdf generated
DOMAIN = sys.argv[1]

# logging conf
logging.basicConfig(filename="build.log", level=logging.DEBUG, 
                    format="%(asctime)s %(message)s", 
                    datefmt="%m/%d/%Y %I:%M:%S %p")

# dbase part global
con = MySQLdb.connect(host="localhost", user="root", passwd="vertigo")
# con.escape_string(")
cur = con.cursor()
# chandler.execute("SHOW DATABASES")
cur.execute("USE book")

# cleanup database from _ % { } \ & " ' # [ ] () <> `
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "_", " ") WHERE author LIKE "%_%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "%", " ") WHERE author LIKE "%\%%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "{", " ") WHERE author LIKE "%{%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "}", " ") WHERE author LIKE "%}%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "&", " ") WHERE author LIKE "%\&%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '"', ' ') WHERE author LIKE '%"%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '`', ' ') WHERE author LIKE '%`%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '^', ' ') WHERE author LIKE '%^%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '(', ' ') WHERE author LIKE '%(%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, ')', ' ') WHERE author LIKE '%)%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '[', ' ') WHERE author LIKE '%[%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, ']', ' ') WHERE author LIKE '%]%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '<', ' ') WHERE author LIKE '%<%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '>', ' ') WHERE author LIKE '%>%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '#', ' ') WHERE author LIKE '%#%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "'", " ") WHERE author LIKE "%'%";""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, '$', ' ') WHERE author LIKE '%$%';""")
cur.execute("""UPDATE thestranger SET author=REPLACE(author, "\\\\", " ") WHERE author LIKE '%\\\\\\\\%'""")

cur.execute("""UPDATE thestranger SET title=REPLACE(title, "_", " ") WHERE title LIKE "%_%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "%", " ") WHERE title LIKE "%\%%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "{", " ") WHERE title LIKE "%{%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "}", " ") WHERE title LIKE "%}%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "&", " ") WHERE title LIKE "%&%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '"', ' ') WHERE title LIKE '%"%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '`', ' ') WHERE title LIKE '%`%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '^', ' ') WHERE title LIKE '%^%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '(', ' ') WHERE title LIKE '%(%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, ')', ' ') WHERE title LIKE '%)%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, ']', ' ') WHERE title LIKE '%]%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '[', ' ') WHERE title LIKE '%[%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '<', ' ') WHERE title LIKE '%<%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '>', ' ') WHERE title LIKE '%>%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '#', ' ') WHERE title LIKE '%#%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "'", " ") WHERE title LIKE "%'%";""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, '$', ' ') WHERE title LIKE '%$%';""")
cur.execute("""UPDATE thestranger SET title=REPLACE(title, "\\\\", " ") WHERE title LIKE '%\\\\\\\\%'""")

cur.execute("SELECT * FROM thestranger")
results = cur.fetchall()
# exclude first 2 data, since it's only keyword pancing.
results = [i for i in results if i[3]][:LIM]

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
 
    {Hi|Hello|Good morning}, my name is Matt and 
    I have {something {important|special} to say|a favorite book}.
 
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


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

        
def create_tex(template, title, author, relatedtitle):
    """
    built a tex file using database and spinned content (*.txt)
    """
    # define data needed
    uid = hashlib.md5(title).hexdigest().upper()[:15]
    pretitle = title.upper()[:2]
    vote = random.randint(2, 40)
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    image = "thumb.jpg"
    # spinned content goes here
    # book_fafifu.txt
    with open("book_fafifu2.txt") as f:
        tex1 = f.read()
        tex1 = tex1.split("\n\n")
        random.shuffle(tex1)
        tex11 = spin(tex1[0]) % (title, author)
        tex12 = spin(tex1[1]) % (title, title)
        tex13 = spin(tex1[2]) % (title, title)

    # book_related_fafifu.txt

    # ini variable ngambil dari related search di mysql lho ya
    with open("book_related_fafifu.txt") as f:
        related_text_raw = f.read()
        # relatedtext = spin(related_text_raw) % (title, author, rand_date, title)

    # construct the string
    container = ""
    for i in relatedtitle:
        # generate random date
        d1 = datetime.strptime('1/1/2009 4:50 AM', '%m/%d/%Y %I:%M %p')
        d2 = datetime.strptime(datetime.now().strftime("%m/%d/%Y %I:%M %p"), 
                               '%m/%d/%Y %I:%M %p')

        t = time.localtime()
        suffix = 'st' if t.tm_mday in [1,21,31] else 'nd' if t.tm_mday in [2, 22] else 'rd' if t.tm_mday in [3, 23] else 'th'
        rand_date = random_date(d1, d2).strftime('%d%%s of %B %Y %I:%M:%S %p') % suffix

        container += "\\noindent\\textbf{\\href{http://%s/download/%s.pdf}{%s}}" % (sys.argv[1], i.replace(" ", "-"), i.upper())
        container += "\n\n"
        container += "\\noindent " + spin(related_text_raw % (i, author, rand_date, i))
        container += "\n\n"
        container += "\\noindent \\href{http://%s/download/%s.pdf}{http://%s/download/%s.pdf}" % (sys.argv[1], i.replace(" ", "-"), sys.argv[1], i.replace(" ", "-"))
        container += "\n\n"
        container += "\\vspace{16pt}"

    # context is the container of our data
    context = {
        "title": title,
        "colors": colors,
        "image": image,
        "author": unicode(author, errors="replace"),
        "uid": uid,
        "vote": vote,
        "pretitle": pretitle,
        "tex11": tex11,
        "tex12": tex12,
        "tex13": tex13,
        "domain": DOMAIN,
        "related": container,
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
    steps:
    1. fetchall semua data dari table di mysql
    2. loop:
    - get title, author
    - download the thumbnail
    - get related title
    """
    titles = [i[1] for i in results]

    # build path and pdf container dir if not exists
    home = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(home, sys.argv[2])  # dibikin flexible dari cmd
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)

    # supress the subprocess output
    FNULL = open(os.devnull, 'w')
    count = 1
    for title in titles:
        # check file size, recreate if > 1000
        fsize = os.path.getsize("build.log")
        if fsize > 1000:
            with open("build.log", "w") as f:
                pass
        if title:
            logging.info("%s. generating pdf for: %s" % (count, title))
            # choose randomed template
            choosen_template = random.choice(template_collection)
            # get related data
            query = "SELECT title FROM thestranger WHERE MATCH (title) AGAINST ('%s' IN BOOLEAN MODE) > 0 LIMIT 8;" % title
            cur.execute(query)
            related_results = cur.fetchall()  # hasilnya tuple of string length 8
            related_results = [i[0] for i in related_results]  # list of string with length of max. 8
            # generate the tex file
            authors = [i[2] for i in results]

            create_tex(choosen_template, title, authors[count-1], related_results)
            # download the image
            url = [i[3] for i in results][count-1]
            logging.info("url: %s" % url)
            if url:
                try:
                    logging.info("downloading image")
                    io = urllib2.urlopen(url, timeout=10).read()
                    logging.info("thum sukses")
                except:
                    logging.info("thumb failed downloaded")
                    count += 1
                    continue
            else:
                logging.info("image url not exist!")
                count += 1
                continue
            with open("thumb.jpg", "w") as f:
                f.write(io)
            # generate the pdf file
            subprocess.call(["pdflatex", "--shell-escape", "output.tex"])
            # subprocess.call(["pdflatex", "--shell-escape", "output.tex"], 
            #                 stdout=FNULL, stderr=subprocess.STDOUT)
            # move the pdf into separate folder
            # folder path => /assets/a/aa
            # fname = "%s.pdf" % unicode(re.sub(" +", " ", title).title().replace(" ", "-"))
            fname = "%s.pdf" % slugify(title).title().replace("+", "")
            # build dirpath
            # dirname = os.path.join(title[0], "".join(title.split())[:2])
            dirname = os.path.join(asset_dir, title[0].upper())  # lgsg 1 dir saja
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
            count += 1
            logging.warning("title is empty, so leave this!")
    FNULL.close()
