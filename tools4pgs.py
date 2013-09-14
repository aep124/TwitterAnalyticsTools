# this script contains some tools for accessing and using our
# postgreSQL (pgs) database

import psycopg2
import getpass 
import sys

class ConnSettings:
    h = ''
    p = None 
    d = ''
    u = ''

def getcs():
    """ Returns instance of ConnSettings """
    cs = ConnSettings()
    print('enter host name: ')
    cs.h = sys.stdin.readline().strip()
    print('enter port number: ')
    cs.p = sys.stdin.readline().strip()
    print('enter database name: ')
    cs.d = sys.stdin.readline().strip()
    print('enter username: ')
    cs.u = sys.stdin.readline().strip()
    return cs

def openconn(settings):
    """ return PostGreSQL database connection
    settings = a ConnSettings object
    """
    print('initiating connection to database ...')
    thishost = settings.h
    thisport = settings.p
    thisdb = settings.d
    thisusername = settings.u
    pw = getpass.getpass()
    conn = psycopg2.connect(database=thisdb, user=thisusername, 
                            password=pw, host=thishost, port=thisport)
    if(conn.status==1):
        print('connection established successfully')
    return conn

def runuserquery(usersfilename, iandtfilename, tfilename):
    # usersfilename is the name of the file from which to get users
    # iandtfilename is the name of the file to which to write ids and tweets
    # tfilename is the name of the file to which to write tweets only

    # open connection to PostGreSQL server
    newconn = openconn()
    # manually specify user ids & handles (that order) in file called 'users':
    usersfile = open(usersfilename, 'r')
    # initialize dictionary for mapping 
    handlemap = {} 
    # open/close files to erase previous contents ('append' flag used later)
    open(iandtfilename,'w').close()
    open(tfilename,'w').close()
    # loop through all the users write their tweets to file
    for line in usersfile:
        # get user id and handle (screen name)
        userid = line.split()[0]
        userhandle = line.split()[1].strip()
        # construct query and get data from postgreSQL
        cond = "user_id = '" + userid + "'"
        twtids = writeidandtwt(newconn, cond, iandtfilename, tfilename)
        # get mapping 
        newhandlemap  = {i: userhandle for i in twtids}
        handlemap.update(newhandlemap)
    usersfile.close()
    close(newconn)
    return handlemap

def getstuff(conn, myquery):
    cur = conn.cursor()
    print('running query ...\n') 
    cur.execute(myquery)
    # fetchall returns a list of tuples
    qresults = cur.fetchall()
    cur.close()
    print('... query complete') 
    return qresults

def gettext(conn, cond):
    # this function returns lists of strings
    cur = conn.cursor()
    myquery = 'SELECT text FROM tweets WHERE ' + cond + ';'
    cur.execute(myquery)
    qresults = cur.fetchall()
    cur.close()
    textlist = [list(t)[0] for t in qresults]
    return textlist

def writeidandtwt(conn, cond, idandtwtfilename, twtfilename):
    # this function gets ids and tweets and writes them to a file
    # it also writes only tweets to another file
    cur = conn.cursor()
    myquery = 'SELECT id,text FROM tweets WHERE ' + cond + ';'
    cur.execute(myquery)
    qresults = cur.fetchall()
    idandtwtfile = open(idandtwtfilename, 'a')
    twtfile = open(twtfilename, 'a')
    for qr in qresults:
        idandtwtfile.write(str(qr[0]) + ' ' + str(qr[1]) + '\n')
        twtfile.write(qr[1] + '\n')
    cur.close()
    ids = [qr[0] for qr in qresults]
    return ids

def close(conn):
	conn.close()
	print('connection closed')

def ex_cond1():
    return 'user_id = "521950319"'

def ex_cond2():
    return 'id = "262345490174181376"'

