# this package contains some tools for applying labels

import webbrowser 
import sys
import random
import pickle
import time



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



def writelabels(dbfilename, labelsystem):
    """ adds labels to the native database """
    
    # unpickle db file:
    nativedb = pickle.load(open(dbfilename, 'r'))
    
    # get user options for replacement:
    prompt1 = 'Do you want the option to replace existing labels? [y/n]'
    prompt1 += '\n(if no, they will be automatically accepted)'
    print(prompt1)
    rawinput = sys.stdin.readline()
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        replace = True
    else:
        replace = False

    # get user options for recycling:
    prompt2 = 'On average, how often do you want to recycle?'
    prompt2 += '\n(express as integer per 100 tweets)'
    print(prompt2)
    rawinput = sys.stdin.readline()
    recyclefreq = int(rawinput)/100.0

    # loop through the input file
    start = time.time()
    totalcnt = 0
    labelcnt = 0
    rbin = []
    for inst in nativedb:
        # check whether this line has been labeled:
        isempty = (inst.get('label') == None)
        # if label is empty or u want to replace it, get label:
        if (isempty | replace):
            thistwtinfo = (inst['handle'], inst['twtid'], inst['raw'])
            existing = (inst.get('label'))
            uinput = getuserinput(thistwtinfo, existing, labelsystem) 
            if (uinput != None):
                inst['label'] = uinput
                labelcnt = labelcnt + 1
            else: 
                print('goodbye')
                break 

        # add to and draw from the recycle bin at a random time
        rbin.append(inst)
        if random.random() < recyclefreq:
            index = int(round(random.random()*(len(rbin)-1)))
            if len(rbin) > 1:
                recycled = rbin.pop(index)
            else:
                recycled = rbin[0]
            # execute 
            handle = recycled['handle']
            twtid = recycled['twtid']
            raw = recycled['raw']
            thistwtinfo = (handle, twtid, raw)
            existinglabel = recycled.get('label')
            rprompt = 'this is a recycle - changes will NOT be saved'
            print(rprompt)
            getuserinput(thistwtinfo, existinglabel, labelsystem) 

        # increment overall counter
        totalcnt += 1

    # print exit message:
    print(str(totalcnt - labelcnt) + ' previous instance labels accepted')
    print(str(labelcnt) + ' instances (re)labeled')
    stop = time.time()
    labelingtime = stop-start
    labelrate = labelcnt/labelingtime
    milliTz = labelrate*1000
    perminute = labelrate*60
    ratemsg = 'labeling rate: %.2f /minute ' % perminute 
    ratemsg += '(%.1f milliTwertz)' % milliTz 
    print(ratemsg)

    # do file dumps and exit:
    pickle.dump(nativedb, open(dbfilename, 'w'))
    writesnapshot(nativedb)
    return None 



def getuserinput(twtinfo, existinglabel, labelsystem):
    """ returns user-entered label or control command 
        twtinfo is a tuple of: handle, twtid, twttext
        """ 

    # construct url and open in browser:
    handle = twtinfo[0]
    twtid = twtinfo[1]
    twturl = 'https://twitter.com/' + handle + '/status/' + twtid
    webbrowser.open(twturl)
 
    # prepare initial text and prompt for user:
    twttext = twtinfo[2]
    initialtext = '"' + twttext[:40] + '..."'
    prompt = 'Enter [label]/help/quit for ' + initialtext 
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
        # quit option:
        elif rawinput in {'q','quit'}:
            break
        else:
            print('error: input not understood, retry ') 

    return label



def writesnapshot(nativedb):
    """ pickles twtids and labels every time labeling is run """

    snapshot = {t['twtid']: t.get('label') for t in nativedb}
    namestamp = time.strftime('%Y-%m-%d_%H:%m:%S')
    picklename = 'labelsnapshot_' + namestamp + '.p'
    pickle.dump(snapshot, open(picklename, 'w'))
    return None



def exhandle():
    return 'SportsCenter'



def exid():
    return '377305730291740672'




