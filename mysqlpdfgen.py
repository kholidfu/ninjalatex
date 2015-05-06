import MySQLdb


con = MySQLdb.connect(host="localhost", user="root", passwd="vertigo")
cur = con.cursor()
# chandler.execute("SHOW DATABASES")
cur.execute("USE book")
# chandler.execute("SHOW TABLES")
cur.execute("SELECT COUNT(*) FROM coba")
print "Jumlah data: %s" % cur.fetchone()
