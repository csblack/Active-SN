import re
import urllib
from BeautifulSoup import *
from pprint import pprint
import sqlite3
import json

conn=sqlite3.connect('ActiveSN.sqlite')
cur=conn.cursor()

####Setting up tables
cur.executescript('''

    Create Table if Not Exists Type
       (id Integer Not null Primary Key Autoincrement Unique,
       SNType Text Unique);
    Create Table if Not Exists Mag
       (id Integer Not null Primary Key Autoincrement Unique,
       Mag Text Unique);
    Create Table if Not Exists SN
       (SNname Text Unique,
       mag_id Integer,
       type_id Integer);


''')

####Reading in page with Beautiful Soup
LatestSNpage=urllib.urlopen("http://www.rochesterastronomy.org/supernova.html").read()
LatestSN=BeautifulSoup(LatestSNpage)

####Pulling out specific tags
tables=LatestSN('table')
ListSN=tables[1]('a')
Stats=tables[1]('td')


####Find current active SN with their mag and type and add to tables
currentSN={}
stats=[]

for i in range(0,len(Stats),3):
    SNname=Stats[i]('a')[0].contents[0]
    i+=1
    mag=Stats[i].contents[0]
    i+=1
    SNtype=Stats[i].contents[0]
    stats=[str(mag),str(SNtype)]
    currentSN[str(SNname)]=stats
    
    cur.execute('''Insert or Ignore into Type (SNType)
       Values (?)''',(SNtype,))
    cur.execute('Select id from Type where SNtype = ?',(SNtype,))
    type_id=cur.fetchone()[0]

    cur.execute('''Insert or Ignore into Mag (mag)
       Values (?)''',(mag,))
    cur.execute('Select id from Mag where mag = ?',(mag,))
    mag_id=cur.fetchone()[0]

    cur.execute('''Insert or Ignore into SN (SNname,mag_id,type_id)
       Values (?,?,?)''',(SNname,mag_id,type_id))
    ####If SN is new, print SN name
    if cur.rowcount > 0:
        print 'New SN!'
        print SNname, '    ', mag
        print ' '
    
    conn.commit()


####Pulling out Ia type, mag, and name from sqlite tables
cur.execute('''Select Distinct id,SNType from Type''')
type_ids=list()
for row in cur: 
    type_ids.append(row)
    if row[1].strip() == 'Ia':
        Ia_id=row[0]

cur.execute('''Select Distinct id,Mag from Mag''')
mag_ids=list()
for row in cur:
    mag_ids.append(row)

cur.execute('''Select SNname,mag_id from SN Where type_id = ?''',(Ia_id,))

####Building dictionary of active Ia's and printing info to terminal
Ias={}
namelen=0

for row in cur:
    for mag in mag_ids:
        if row[1] == mag[0]:
            Ia = str(row[0].strip())
            Ialen = len(Ia)
            if Ialen > namelen:
                namelen = Ialen
            while len(Ia) < namelen:
                Ia = Ia + ' '
            Ias[Ia]= mag[1].strip()

print '   '
print 'All Active Ia SN:'
for Ia in Ias:
    print Ia, '   ', Ias[Ia]


print '   '
print 'Observable Ia SN:'
for Ia in Ias:
    if float(Ias[Ia].strip('*')) < 15.0:
        print Ia, '   ', Ias[Ia]
print '   '
