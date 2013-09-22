# this script contains some tools for accessing and using our
# postgreSQL (pgs) database

import psycopg2
import getpass 
import sys
import tools4urls
import pickle
import time


class ConnSettings:
    """ really simple class to hold postgres connection settings
        (could have just used a dictionary)
        """
    h = ''
    p = None 
    d = ''
    u = ''

def getcs():
    """ returns instance of ConnSettings """
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
    """ returns PostGreSQL database connection
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

def close(conn):
	conn.close()
	print('connection closed')

def ex_cond1():
    return 'user_id = "521950319"'

def ex_cond2():
    return 'id = "262345490174181376"'



def writenativedb(filename):
    """ returns a rudimentary form of relational database as a list
        of dictionaries, which are both native python data types
        "ntwts" = number of tweets to retrieve
        """
    
    # get number of tweets from user:
    prompt = 'How many tweets do you want to get?'
    print(prompt)
    ntwts = int(sys.stdin.readline())

    pgconn = openconn(getcs())

    # get tweet ids and raw text from "tweets" database:
    twts_cur = pgconn.cursor()
    twts_query = 'SELECT id,text,user_id FROM tweets;'
    twts_cur.execute(twts_query)

    nativedb = []
    rcnt = 0
    for twt in twts_cur.fetchall():
        nativedb.append({})
        nativedb[rcnt].update({'twtid': twt[0]})
        nativedb[rcnt].update({'raw': twt[1].replace('\n',' ')})	
        nativedb[rcnt].update({'userid': twt[2]})	
        rcnt += 1
        # output progress: 
        readprogress = 'tweets read: %-8i' % rcnt
        sys.stdout.flush()
        sys.stdout.write('\r' + readprogress)
        # check limit:
        if rcnt >= ntwts:
            break
    print # close progress line

    # identify handles by looking up user id in "users" database:
    users_cur = pgconn.cursor()
    users_query = 'SELECT id,screen_name FROM users'
    users_cur.execute(users_query)
    ucnt = 0
    id2handle = dict(users_cur.fetchall())
    for inst in nativedb:
        inst.update({'handle': id2handle[inst['userid']]})
        ucnt += 1
        userprogress = 'user handles read: %-8i' % ucnt
        sys.stdout.flush()
        sys.stdout.write('\r' + userprogress)
    print
    users_cur.close()

    # close connection and pickle database:
    pgconn.close()
    pickle.dump(nativedb, open(filename, 'w'))
    print('pickling complete')
    return None



def writecheck4imgs(picklename, pullname='', pushname=''):
    """ wrapper for 'runcheck4imgs()' that checks connection """

    dummydb = pickle.load(open(picklename,'r'))
    if tools4urls.connectionOK():
        nativedb = runcheck4imgs(dummydb, pullname, pushname)
        pickle.dump(nativedb, open(picklename, 'w'))
    return None 



def runcheck4imgs(dummydb, pullname, pushname):
    """ removes tweets without native images 
        (this function was separted from main native db write 
        function because it takes a long time to run, and backs
        itself up to a text file)
        NOTE: only call if network connection is known to be OK !!!
        (will return all false negatives otherwise)
        """

    # handle backup files 
    if (pushname == ''):
        pushname = 'imgtwtids_backedup'
    if (pushname == pullname):
        print('error: pushfile and pullfile have the same name') 
    pushfile = open(pushname,'w')
    if (pullname != ''):
        pullfile = open(pullname,'r')
        # read in id:tag pairs as dictionary 
        # (tag = 'hasimg' or 'noimg')
        idtagpairs = pullfile.readlines()
        pullfile.close()
        idtagmap = {p.split()[0]:p.split()[1] for p in idtagpairs}  
    else:
        idtagmap = {}       

    # loop through instances
    nativedb = []
    icnt = 0
    lastpause = time.time()
    for icnt in range(len(dummydb)):
        thistwtid = dummydb[icnt].get('twtid')
        thistag = idtagmap.get(thistwtid)

        # check for image two ways:
        # by looking in the backed-up list:
        if (thistwtid in idtagmap.keys()):
            check4img = (thistag == 'hasimg')
        # by following url (only do if id is not in backup file)
        else:
            raw = dummydb[icnt].get('raw')
            imgstatus = 'looking for img in tweet '
            imgstatus += str(icnt+1) + ': ... %-35s' % raw[-35:]
            sys.stdout.write('\r' + imgstatus)
            sys.stdout.flush()
            # this is the time-consuming line:
            check4img = tools4urls.hasnimage(raw)

        # aggregate two checks and record appropriate result
        if (check4img):
            nativedb.append(dummydb[icnt])
            backup = thistwtid + ' hasimg' + '\n' 
            pushfile.write(backup)
        else:
            backup = thistwtid + ' noimg' + '\n' 
            pushfile.write(backup)          

        # pause to allow user to cancel if necessary:
        if ((time.time()-lastpause) > 30):
            pausecondition = True 
            lastpause = time.time()
        else:
            pausecondition = False 
        if pausecondition:
            print
            print('... pausing to quit (ctrl+c) if necessary ...')
            cntdown = 5
            while cntdown > 0:
                cntdownmsg = '(will automatically continue in '
                cntdownmsg += '%2i seconds)' % cntdown
                sys.stdout.write('\r' + cntdownmsg)
                sys.stdout.flush()
                time.sleep(1.0)
                cntdown -= 1
      
    print # close status
    print('tweets with images found: %-8i' % len(nativedb))
    pushfile.close()
    return nativedb


