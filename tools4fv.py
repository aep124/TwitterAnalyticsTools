# this module contains some tools for 
# generating feature vectors (fv) for text strings (e.g., tweets)

import time 
import pickle



def getwordmap(dbfilename):
    """ returns dictionary (a.k.a. map) in which keys are words
        and values are corpus frequencies
        """

    nativedb = pickle.load(open(dbfilename, 'r'))
    wordmap = {}
    allfiltered = [inst['filtered'] for inst in nativedb]
    for thiswordlist in allfiltered:
        for word in thiswordlist:
            word = word.lower()
            if word in wordmap.keys():
                wordmap[word] = wordmap[word] + 1
            else:
                wordmap.update({word: 1})
    return wordmap



def writefeatures(filename, wordlist):
    """ writes the features to the nativedb corresponding to the
        elements of the wordlist
        """
    nativedb = pickle.load(open(filename,'r'))
    for inst in nativedb:
        twtlist = inst['filtered'].strip().split()
        featurelist = [str(twtlist.count(w)) for w in wordlist]
        inst.update({'features': featurelist})
        # alternatively, could use regex
        # word = '\\b' + word + '\\b'
        # features = features + ', ' + str(len(re.findall(word,twt)))
    pickle.dump(nativdb, open(filename, 'w'))
    return None 



def writearff(dbfilename, wordlist): 
    """ writes the features and classesin the database to an arff file 
        (reads, but does not write to, the database pickle file)
        """

    # as always, unpickle the database:
    nativedb = pickle.load(open(dbfilename, 'r'))

    # deal with time stuff and construct output file name:
    writetime = time.gmtime()
    namestamp = time.strftime('%Y-%m-%d_%H:%m:%S', writetime)
    arffname = 'twtfeatures' + '_' + namestamp + '.arff'
    arff = open(arffname, 'w')

    # write comments:
    timeheader = '% Written on: ' + time.asctime(writetime) 
    arff.write(timeheader)

    # write header:
    arff.write('@RELATION ' + 'wordfreq' + str(len(wordlist)) + '\n\n')
    for word in wordlist: 
        attribute = '@ATTRIBUTE %-15s NUMERIC \n' % word
        arff.write(attribute)
    actclasses = '{pos,neg}'
    arff.write('@ATTRIBUTE %-15s ' + actclasses + ' \n' % 'actclass')
    timeclasses = '{past,pres,future,ambiguous}'
    arff.write('@ATTRIBUTE %-15s ' + timeclasses + ' \n\n' % 'timeclass')
    arff.write('@DATA \n')

    # write content:
    for inst in nativedb: 
        featurestring = ','.join(inst['features'])
        labelstring = inst['actclass'] + ',' + inst['timeclass']
        line = featurestring + ',' + labelstring + '\n'
        arff.write(line)
    arff.close()
    return None 


def getcheckset(wordlist, features):
    # this function returns a set of words indicated by the features
    wfzipped = zip(wordlist, features)
    checkset = set([wf[0] for wf in wfzipped if wf[1] > 0])
    return checkset



def runcheck(wordlist, twtfilename, featurefilename):
    twtfile = open(twtfilename, 'r')
    featurefile = open(featurefilename, 'r')
    cnt = 0
    for twt in twtfile:
        cnt = cnt + 1
        # make feature string into list of integers:
        features = featurefile.readline().strip().split(',')
        features = [int(f) for f in features]
        # get set of words from the tweet string
        fromtwt = set(twt.split())
        # get set of words from the features:
        fromfeatures = getcheckset(wordlist, features)
        # test whether or not the two sets are the same:
        xorset = fromtwt ^ fromfeatures
        if len(xorset) == 0:
            print('Line ' + str(cnt) + ' is OK')
        else:
            print('Line ' + str(cnt) + ' is NOT OK')
            print('    (begins with "' + twt[:20] + ' ...")')
            xorwords = ''
            for el in xorset:
                xorwords = xorwords + ' ' + el
            print('    (inconsistency with following words: ' + xorwords + ' )')
    twtfile.close()
    featurefile.close()
    return None 

