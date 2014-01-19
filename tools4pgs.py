# this script contains some tools for accessing and using our
# postgreSQL (pgs) database

import psycopg2
import getpass 
import sys
import tools4urls
import pickle
import time

import numpy as np
import pandas as pd


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


# psuedocode:
# 

def writetwtinfo(query, condition, filename, onlyNativeImgs=False):
    """ returns a pandas-style data frame """
    
    # tweet info data frame columns:
    #    NAME          DATATYPE 
    #    twtid ....... string (of digits)
    #    raw ......... string
    #    filtered .... string
    #    userid ...... string (of digits)
    #    handle ...... string
    #    label ....... string

    # get number of tweets from user:
    prompt = 'How many tweets do you want to get?'
    print(prompt)
    ntwts = int(sys.stdin.readline())

    pgconn = openconn(getcs())

    # get tweet ids and raw text from "tweets" database:
    twts_cur = pgconn.cursor()
    print 'running query'
    limitcondition = 'LIMIT %i' % ntwts
    # could also limits results by using fetchmany(ntwts)
    full_query = query + ' ' + condition + ' ' + limitcondition + ';'
    twts_cur.execute(full_query)
    print 'query complete'
    ntwts = min([ntwts, twts_cur.rowcount])

    # initialize 
    pandasDF = initializeInfoDF(ntwts)
    print 'data frame initialized'

    # twts_cur.fetchall() returns a list of lists [id,text,user_id] 
    rcnt = 0
    for twt in twts_cur.fetchall():
        pandasDF.loc[rcnt, 'twtid'] = twt[0]
        rawstring = twt[1]
        rawstring = rawstring.replace('\n',' ')
        rawstring = rawstring.replace('\r',' ')
        pandasDF.loc[rcnt, 'raw'] = rawstring 
        pandasDF.loc[rcnt, 'userid'] = twt[2]
        rcnt += 1
        # output progress: 
        readprogress = 'tweets read: %-8i' % rcnt
        sys.stdout.flush()
        sys.stdout.write('\r' + readprogress)
        # check limit:
        if rcnt >= ntwts:
            break
    print # close progress line

    # filter out tweets that lack native images:
    if bool(onlyNativeImgs):
        icnt = 0
        keeplist = []
        for icnt in range(ntwts):
            raw = pandasDF.loc[icnt, 'raw']
            imgstatus = 'looking for img in tweet '
            imgstatus += str(icnt+1) + ': ... %-35s' % raw[-35:]
            sys.stdout.flush()
            sys.stdout.write('\r' + imgstatus)
            check4img = tools4urls.hasnimage(raw)
            if check4img:
                keeplist.append(icnt)
        pandasDF = pandasDF.loc[keeplist]
        pandasDF.reset_index(drop=True, inplace=True)
        print # close status
        print('tweets with images found: %-8i' % len(pandasDF))

    # code below is a rudimentary way to get user handles - for some reason i can't access the table, so i'm commenting it out
    # identify handles by looking up user id in "users" database:
    #users_cur = pgconn.cursor()
    #Uquery = 
    #users_cur.execute(Uquery)
    #ucnt = 0
    #idHandleMap = dict(users_cur.fetchall())
    #for index in pandasDF:
    #    currentid = pandasDF.loc[index, 'userid']
    #    pandasDF.loc[index, 'handle'] = idHandleMap[currentid]
    #    ucnt += 1
    #    userprogress = 'user handles read: %-8i' % ucnt
    #    sys.stdout.flush()
    #    sys.stdout.write('\r' + userprogress)
    #print
    #users_cur.close()

	
    # close connection and pickle database:
    pgconn.close()
    pickle.dump(pandasDF, open(filename, 'w'))
    print('pickling complete')
    return None


def initializeInfoDF(ntwts):
    """ initializes the tweet info data frame """

    # initialize the dataframe
    # tweet IDs and user IDs are 64-bit integers
    templateMap = {'twtid':str(2**64)}
    templateMap.update({'userid':str(2**64)})
    # raw and filtered messages have max 140 chars 
    templateMap.update({'raw':'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad ....'})
    templateMap.update({'filtered':'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad ....'})
    # handles are max 15 chars
    templateMap.update({'handle': 'a'*15})
    # make labels (arbitrarily) 5-character string
    # setting to array will force entire data frame to length ntwts
    templateMap.update({'label':np.array(['no_label']*ntwts)})
    pandasDF = pd.DataFrame(templateMap)
    return pandasDF


