# this package contains some tools for applying labels

import webbrowser 
import sys
import random
import pickle
import time
import copy

import numpy as np
import pandas as pd 


# tweet info table columns:
#    NAME          DATATYPE 
#    twtid ....... string (of digits)
#    raw ......... string
#    filtered .... string
#    userid ...... string (of digits)
#    label ....... string

# user table columns (this can just be a map):
#    NAME          DATATYPE 
#    userid ...... string (of digits)
#    handle ...... string

# twt features columns:
#    NAME          DATATYPE 
#    twtid ....... string (of digits)
#    feature 1 ... TF-IDF scores for word 1
#    feature 2 ... TF-IDF scores for word 2
#       :
#    feature n ... TF-IDF scores for word n
#    label ....... string



def getlabelmap(labelfilename):
    """ returns a dictionary of label symbols and descriptions 
        from the specified file
        """

    labelfile = open(labelfilename, 'r')
    labelmap = {}
    # loop through the file
    for line in labelfile:
        # only parse line if nonempty and not a comment 
        notempty = (line.strip() != '')
        if notempty:
            notcomment = (line.strip()[0] != '#')
            if notcomment:
                parsedline = line.split('=')
                symbol = parsedline[0].strip()
                desc = parsedline[1].strip()
                labelmap.update({symbol: desc})
    labelfile.close()
    return labelmap



def explainlabels(labelmap):
    """ prints explanation of labeling system """ 
    
    print
    for k in labelmap.keys():
        start = '%3s = ' % k
        print(start + labelmap[k])
    print
    return None



def writelabels(infofilename, labelsystem):
    """ adds labels to the tweet info table """
    
    # un-pickle file with tweet info:
    twtinfo = pickle.load(open(infofilename, 'r'))
    
    # get user options for replacement:
    prompt1 = 'Do you want the option to replace existing labels? [y/n]'
    prompt1 += '\n(if no, they will be automatically accepted)'
    print(prompt1)
    rawinput = sys.stdin.readline()
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        doreplacement = True
    else:
        doreplacement = False

    # get user options for recycling:
    prompt2 = 'Average recycle frequency?'
    prompt2 += '\n(express as integer per 100 tweets)'
    print(prompt2)
    rawinput = sys.stdin.readline()
    recyclefreq = int(rawinput)/100.0

    # set up shuffling
    maybeshuffled = range(len(twtinfo))
    prompt3 = 'Label tweets in random sequence [y/n]?'
    print(prompt3)
    rawinput = sys.stdin.readline()  
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        random.shuffle(maybeshuffled)

    # set up shuffling
    browseropen = False 
    prompt4 = 'Automatically open tweet in browser [y/n]?'
    print(prompt4)
    rawinput = sys.stdin.readline()  
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        browseropen = True
    
    # check whether or not the data frame has a label column
    if ('label' not in list(twtinfo.columns)):
        ntwts = len(twtinfo)
        twtinfo['label'] = np.array(['no_label']*ntwts)

    # pseudocode for labeling execution:
    #    initialize counters
    #    while loopcnt < len(twtinfo):
    #        get the current instance in the table
    #        if it's empty OR user specified replacement:
    #            get user input
    #            if user input is 'back'
    #                de-increment loopcnt
    #            else if user input is 'quit'
    #                break
    #            else if user input is 'progress'
    #                display progress message
    #            else (assuming now that user input is valid)
    #                assign input to table
    #                handle recycling 
    #        else (i.e., if non-empty AND non-replacing)
    #            increment skip counter 

    start = time.time()
    loopcnt = 0
    skipcnt = 0
    rbin = [] # rbin is just a list of indices 
    while loopcnt < len(twtinfo):
        # if no shuffling, 'maybeshuffled' just returns identity
        index = maybeshuffled[loopcnt]
        # use selection by label (.iloc method)
        instMap = dict(copy.copy(twtinfo.loc[index]))
        # check whether this line has been labeled:
        isempty = (instMap['label'] in labelsystem.keys())
        # if label is empty or u want to doreplacement, get label:
        if (isempty | doreplacement):
            uinput = getuserinput(instMap, labelsystem, browseropen) 
            if (uinput == 'back'):
                print('going back ...')
                loopcnt -= 1
            elif(uinput == 'quit'):
                print('goodbye')
                break
            elif(uinput == 'progress'):
                progmsg = str(loopcnt) + ' instances (re)labeled'
                progmsg += progmsg + '(not counting recycles)'
                print('# ' + str(loopcnt) + ' instances (re)labeled')
            else:
                twtinfo.loc[index, 'label'] = uinput
                loopcnt += 1 
                # always add to the recycle bin
                rbin.append(index)
                # at random times, remove from recycle bin 
                if random.random() < recyclefreq:
                    localindex = random.randint(0,len(rbin)-1)
                    recycleindex = rbin.pop(localindex)
                    recycled = copy.copy(twtinfo.loc[recycleindex])
                    # execute 
                    print('recycling - changes will NOT be saved')
                    getuserinput(recycled, labelsystem, browseropen) 

        else:
            # if not replacing, just increment counter:
            skipcnt += 1

    
    # remove tweets labeled with zero
    prefiltercnt = len(twtinfo)
    twtinfo = twtinfo[twtinfo.label != '0']
    postfiltercnt = len(twtinfo)
    filtercnt = prefiltercnt - postfiltercnt
    
    # pickle database and snapshot
    pickle.dump(twtinfo, open(infofilename, 'w'))
    writesnapshot(twtinfo)

    # print exit message:    
    stop = time.time()
    labelingtime = stop-start
    labelrate = loopcnt/labelingtime
    milliTz = labelrate*1000
    perminute = labelrate*60
    ratemsg = '#    %.2f labels/minute ' % perminute 
    ratemsg += '(%.1f milliTwertz)' % milliTz 
    print
    print('######################## SUMMARY ########################')
    print('#    ' + str(filtercnt) + ' instances removed ("0" label)')
    print('#    ' + str(postfiltercnt) + ' instances written to file')
    print('#    ' + str(skipcnt) + ' labels automatically accepted')
    print('#    ' + str(loopcnt) + ' instances (re)labeled')
    print(ratemsg)
    print('#        (NOTE: not counting recycled instances)')
    print

    return None 



def getuserinput(instMap, labelsystem, browseropen):
    """ returns user-entered label or control command 
        "instMap" is the tweet instance - dictionary w/ standard fields
        "labelsystem" is the dictionary of labels
        "browseropen" is a boolean variable for whether or not to
        open the browser automatically - if false, tweets will print
        to console and user must manually open any urls
        """ 

    # open url or prepare prompt:
    twttext = instMap['raw']
    if browseropen:
        handle = instMap['handle'] 
        twtid = instMap['twtid'] 
        twturl = 'https://twitter.com/' + handle + '/status/' + twtid
        webbrowser.open(twturl)
        text = '"' + twttext[:40] + '..."'         
    else:
        text = '" ' + twttext + ' "'
 
    # prepare initial text and prompt for user:
    existinglabel = instMap['label']
    prompt = 'Enter [label]/help/back/quit/progress for ' + text 
    prompt += '\n(current label: "' + str(existinglabel) + '")'

    # interact with user:
    label = None
    while (label == None):
        print(prompt)
        rawinput = sys.stdin.readline().strip()
        # save input if it matches a valid symbol: 
        if rawinput in labelsystem.keys():
            label = rawinput
        # print symbols and descriptions of labels if users asks:
        elif rawinput in {'h', 'he', 'hel', 'help'}:
            explainlabels(labelsystem)
        # escape options:
        elif rawinput in {'b','ba','bac','back'}:
            label = 'back'
        elif rawinput in {'q','qu','qui','quit'}:
            label = 'quit'
        elif rawinput in {'p','pr','prog','progress'}:
            label = 'progress'
        else:
            print('error: input not understood, retry ') 

    return label



def writesnapshot(twtinfo):
    """ pickles twtid-label map every time labeling is run """

    ids = copy.copy(twtinfo.twtid)
    labels = copy.copy(twtinfo.label)
    # use dictionary comprehension:
    snapshot = {ids[ii]:labels[ii] for ii in twtinfo.index}
    namestamp = time.strftime('%Y-%m-%d_%H-%m')
    picklename = 'labelsnapshot_' + namestamp + '.p'
    pickle.dump(snapshot, open(picklename, 'w'))
    return None



def exhandle():
    return 'SportsCenter'


def exid():
    return '377305730291740672'




