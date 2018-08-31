import csv, sqlite3

con = sqlite3.connect("geo.sq3")
cur = con.cursor()
cur.execute("CREATE TABLE GEO (id INTEGER PRIMARY KEY, zip_code INTEGER, city TEXT, state TEXT, county TEXT);")

reader = csv.reader(open('resources/zip_codes_states.csv', 'r'), delimiter=',')

for row in reader:
    to_db = [row[0], row[3], row[4], row[5]]
    cur.execute("INSERT INTO GEO (zip_code, city, state, county) VALUES (?, ?, ?, ?);", to_db)

# for row in cur.execute("SELECT * from geo"):
#     print(row)

z = "02186"

for row in cur.execute("SELECT * from geo where zip_code = '02186'"):
    	print(row)

con.commit()
con.close()