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
    
    # get user options for replacementment:
    prompt1 = 'Do you want the option to replace existing labels? [y/n]'
    prompt1 += '\n(if no, they will be automatically accepted)'
    print(prompt1)
    rawinput = sys.stdin.readline()
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        doreplacement = True
    else:
        doreplacement = False

    # get user options for recycling:
    prompt2 = 'On average, how often do you want to recycle?'
    prompt2 += '\n(express as integer per 100 tweets)'
    print(prompt2)
    rawinput = sys.stdin.readline()
    recyclefreq = int(rawinput)/100.0

    # set up shuffling
    maybeshuffled = range(len(nativedb))
    prompt3 = 'Do you want to label tweets in random sequence [y/n]?'
    print(prompt3)
    rawinput = sys.stdin.readline()  
    if (rawinput.strip() in {'y', 'ye', 'yes'}):
        random.shuffle(maybeshuffled)

    # loop through the input file
    start = time.time()
    loopcnt = 0
    labelcnt = 0
    skipcnt = 0
    rbin = []
    while loopcnt < len(nativedb):
        # if no shuffling, 'maybeshuffled' just returns identity
        index = maybeshuffled[loopcnt]
        inst = nativedb[index]
        # check whether this line has been labeled:
        isempty = (inst.get('label') == None)
        # if label is empty or u want to doreplacement, get label:
        if (isempty | doreplacement):
            thistwtinfo = (inst['handle'], inst['twtid'], inst['raw'])
            existing = (inst.get('label'))
            uinput = getuserinput(thistwtinfo, existing, labelsystem) 
            if (uinput != None):
                inst['label'] = uinput
                # because this is a normal label, increment counters:
                labelcnt += 1
                loopcnt += 1
            else: 
                print('quit? [y/n] (if no, will go back)')
                rawinput = sys.stdin.readline().strip()
                if rawinput in {'y','yes','q','qu','quit'}:
                    print('goodbye')
                    break
                else:
                    print('going back ...')
                    # de-increment counters to go back:
                    labelcnt -= 1
                    loopcnt -= 1
        else:
            # if not replacing, just increment counter:
            skipcnt += 1

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

    
    

    # remove tweets labeled with zero
    prefiltercnt = len(nativedb)
    nativedb = [ndb for ndb in nativedb if ndb.get('label') != '0']
    postfiltercnt = len(nativedb)
    filtercnt = prefiltercnt - postfiltercnt
    
    # pickle database and snapshot
    pickle.dump(nativedb, open(dbfilename, 'w'))
    writesnapshot(nativedb)

    # print exit message:    
    stop = time.time()
    labelingtime = stop-start
    labelrate = labelcnt/labelingtime
    milliTz = labelrate*1000
    perminute = labelrate*60
    ratemsg = '#    %.2f labels/minute ' % perminute 
    ratemsg += '(%.1f milliTwertz)' % milliTz 
    print
    print('######################## SUMMARY ########################')
    print('#    ' + str(filtercnt) + ' instances removed ("0" label)')
    print('#    ' + str(postfiltercnt) + ' instances written to file')
    print('#    ' + str(skipcnt) + ' labels automatically accepted')
    print('#    ' + str(labelcnt) + ' instances (re)labeled')
    print(ratemsg)
    print('#        (NOTE: not counting recycled instances)')
    print

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
    prompt = 'Enter [label]/help/escape for ' + initialtext 
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
        # escape option:
        elif rawinput in {'e','esc','escape','q','quit','b','back'}:
            break
        else:
            print('error: input not understood, retry ') 

    return label



def writesnapshot(nativedb):
    """ pickles twtids and labels every time labeling is run """

    snapshot = {t['twtid']: t.get('label') for t in nativedb}
    namestamp = time.strftime('%Y-%m-%d_%H-%m-%S')
    picklename = 'labelsnapshot_' + namestamp + '.p'
    pickle.dump(snapshot, open(picklename, 'w'))
    return None



def exhandle():
    return 'SportsCenter'



def exid():
    return '377305730291740672'




