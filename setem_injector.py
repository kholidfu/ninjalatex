import pymongo

with open("fdp.txt") as f:
    terms = f.read()

terms = [term.strip() for term in terms.split("\n") if term]

c = pymongo.Connection()
db = c["semras"]

count = 1
for term in terms:
    if not db.term.find_one({"term": term}):
        print "inserting term #%d" % count
        db.term.insert({"term": term})
    count += 1
