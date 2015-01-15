import os
from jinja2 import Environment, FileSystemLoader
import hashlib
import subprocess
from unidecode import unidecode
import sys
import random
import logging
import pymongo


"""
source: http://pythonadventures.wordpress.com/2014/02/25/jinja2-example-for-generating-a-local-file-using-a-template/

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


# load the templates dir
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=True,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False,
    # extensions=["jinja2.ext.autoescape"],
)


# ready to render
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


# randomize template
# template_collection = ["index.tex", "index2.tex"]
template_collection = ["index3.tex"]


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
    # database call
    db = c["terms"]
    tags = db.command('text', 'term', search=title, limit=10)
    tags = [tag['obj'] for tag in tags['results']]
    tags = "\n\n".join(tag['term'] for tag in tags)
    # tags = "\n\n".join(["satu", "dua", "tiga"])
    # output/generated file
    fname = "output.tex"
    # variables we will use in template
    # title = "2001 ford taurus automatic transmission wiring schematic"
    # generate unique id for each book (mimic isbn)
    uid = hashlib.md5(title).hexdigest().upper()
    # generate random color for cover needs
    colors = ",".join([str(random.random())[:4] for i in range(4)])
    # keywords for pdf metada
    keywords = ",".join(["read online", "ebook"] + title.split() + ["free", "download"])
    # spinned content
    content = """ 
[from|through|coming from|via|by] [our|the|our own|each of
our|your] [library|collection|selection|catalogue|stockpile] [is|is
actually|will be|can be|is usually] [free|free of charge|totally
free|no cost|cost-free] [resource|source|useful
resource|reference|learning resource] [for|with regard
to|regarding|pertaining to|intended for] [public|open
public|community|general public|open].  [Our|The|Our own|Each of
our|Your] [library|collection|selection|catalogue|stockpile]
[Ebooks|E-books|Information products|Electronic books|Books]
[collection|selection|assortment|series|variety]
[delivers|provides|offers|gives|produces]
[complete|total|full|comprehensive|finish] [access to|use of|usage
of|entry to|having access to] [the largest|the biggest|the
greatest|the most important|the best] [collection of|assortment
of|number of|variety of|bunch of] [digital|electronic|electronic
digital|digital camera|a digital]
[publications|magazines|guides|journals|ebooks] [available
today|currently available|on the market|on the market today|now
available].

[04|04|2008|apr] \\textbf{%s} [Civic|Social]
[Hybrid|Crossbreed|Cross|A mix of both|Hybrid car]
[Service|Support|Program|Assistance|Services]
[Repair|Restore|Fix|Restoration|Mend] [Manual|Guide|Handbook|Guide
book|Information] [Pdf|Pdf file] [is available|can be obtained|can be
acquired|can be purchased|can be found] [through|via|by means of|by
way of|as a result of] [our|the|our own|each of our|your] [online|on
the internet|on the web|on-line|on the net] [libraries|your local
library] [and|as well as|and also|along with|in addition to] [we|all
of us|we all|many of us|most of us] [offer|provide|offer
you|present|deliver] [online|on the internet|on the web|on-line|on the
net] [access to|use of|usage of|entry to|having access to]
[worthwhile|useful|advantageous|worth it|rewarding]
[books|publications|guides|textbooks|ebooks]
[instantly|immediately|quickly|instantaneously|promptly]
[from|through|coming from|via|by] [multiple|several|numerous|a number
of|many] [locations|areas|places|spots|destinations], [including|such
as|which includes|which include|as well as]
[library|collection|selection|catalogue|stockpile],
[office|workplace|business office|place of work|company],
[home|house|residence|household|property] [or|or even|or perhaps|as
well as|or maybe] [wherever|where ever|exactly where|in
which|anywhere] [they are|theyre|they may be|these
are|therere]. [Our|The|Our own|Each of our|Your]
[Ebooks|E-books|Information products|Electronic books|Books]
[Collection|Selection|Assortment|Series|Variety] [uses|utilizes|makes
use of|employs|works by using] [the|the actual|the
particular|your|this] portability, searchability, [and|as well as|and
also|along with|in addition to]
[unparalleled|unequalled|unrivaled|unmatched] [ease
of|easy|simple|easier|simplicity of] [access|entry|accessibility|gain
access to|admittance] [of|associated
with|regarding|involving|connected with] [PDF|PDF FILE]
[data|information|info|files|facts]
[formats|platforms|types|forms|codecs] [to make|to create|to
produce|to generate|for making] [access|entry|accessibility|gain
access to|admittance] [for people|for individuals|for folks|for
those|if you are], [any time|whenever|any moment|at any time|every
time], [anywhere|anyplace|everywhere|wherever|at any place] [and|as
well as|and also|along with|in addition to] [on|upon|about|in|with]
[any|any kind of|virtually any|just about any|almost any]
[device|gadget|system|unit|product].

\\textbf{%s} [This page|This site|These pages] [provides an|has
an|offers an] [indexed|listed|found] [list of|listing of|set of|report
on|directory] [digital|electronic|electronic digital|digital camera|a
digital] [ebooks|e-books|information products|electronic books|books]
[for which|that|which is why|is actually|which is]
[has|offers|provides|features|possesses]
[publication|book|newsletter|guide|distribution]
metadata. [By|Through|Simply by|By simply|By means of]
[clicking|clicking on|pressing|hitting|simply clicking] [on the|about
the|around the|for the|within the] [link|hyperlink|website
link|url|web page link] bellow [you will be|you'll be|you will end
up|you may be|you can be] [presented
with|given|offered|assigned|exhibited] [the|the actual|the
particular|your|this] [portion of|part of|percentage of|area
of|component of] [the|the actual|the particular|your|this] [list
of|listing of|set of|report on|directory] [ebooks|e-books|information
products|electronic books|books] [related with|related to]
[04|04|2008|apr] [Honda|Ford|Kia|Toyota] [Civic|Social]
[Hybrid|Crossbreed|Cross|A mix of both|Hybrid car]
[Service|Support|Program|Assistance|Services]
[Repair|Restore|Fix|Restoration|Mend] [Manual|Guide|Handbook|Guide
book|Information] [Pdf|Pdf file].
    """ % (title, title)
    content = spin(content)
    # context is the container of our data
    context = {"title": title, "uid":uid, "colors": colors, 
               "keywords": keywords, "content": content, 
               "tags": tags}
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
            dirname = os.path.join(title[0], "".join(title.split())[:2])
            dirname = os.path.join(asset_dir, dirname)
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
