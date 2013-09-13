# this module contains some tools for 
# generating feature vectors (fv) for text strings (e.g., tweets)
#  \xe3\x80\x8b

# regular expressions module:
import re 
# module for getting time for arff header:
import time 

def runcheck(wordlist, twtfilename, featurefilename):
    twtfile = open(twtfilename, 'r')
    featurefile = open(featurefilename, 'r')
    cnt = 0
    for twt in twtfile:
        cnt = cnt + 1
        # make feature string into list of integers:
        features = re.split(',', featurefile.readline().strip())
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

def getcheckset(wordlist, features):
    # this function returns a set of words indicated by the features
    wfzipped = zip(wordlist, features)
    checkset = set([wf[0] for wf in wfzipped if wf[1] > 0])
    return checkset

def getwordlist(twtfilename):
    twtfile = open(twtfilename, 'r')
    wordset = set()
    for twt in twtfile:
        currentwordset = set(re.split(' ', twt.strip()))
        wordset = wordset | currentwordset  
    wordlist = list(wordset)
    twtfile.close()
    return wordlist

def getwordmap(twtfilename):
    twtfile = open(twtfilename, 'r')
    wordmap = {}
    for twt in twtfile:
        currentwordlist = twt.strip().split()
        for word in currentwordlist:
            word = word.lower()
            if word in wordmap.keys():
                wordmap[word] = wordmap[word] + 1
            else:
                wordmap.update({word: 1})
    twtfile.close()
    return wordmap

def writearff(wordlist, featurefilename, arffnamebase='twtfeatures_labeled'): 
    # deal with time stuff and construct output file name:
    writetime = time.time()
    ttime = time.asctime(time.gmtime(writetime))
    etime = re.split('\.', str(writetime))[0]
    arffname = arffnamebase + etime + '.arff'
    # open files
    features = open(featurefilename, 'r')
    arff = open(arffname, 'w')
    # write comments:
    timestamp = '% Written on: ' + ttime + '  (epoch time: ' + etime + ') \n\n'
    arff.write(timestamp)
    # write header:
    arff.write('@RELATION ' + 'wordfreq' + str(len(wordlist)) + ' \n\n')
    for word in wordlist: 
        attribute = '@ATTRIBUTE %-15s NUMERIC \n' % word
        arff.write(attribute)
    arff.write('@ATTRIBUTE %-15s {pos,neg} \n\n' % 'class')
    arff.write('@DATA \n')
    # write content:
    for line in features: 
        arff.write(line)
    features.close()
    arff.close()
    return None 

def writefeatures(wordlist, twtfilename, featurefilename='twtfeatures.txt'):
    # twtfilename is a file of tweets term frequencies:
    # wordlist is a list of terms for which to search:
    twtfile = open(twtfilename, 'r')
    featurefile = open(featurefilename,'w')
    for twt in twtfile:
        # could split tweet string into a list of word strings
        twtlist = twt.strip().split()
        features = [str(twtlist.count(w)) for w in wordlist]
        featurestring = ', '.join(features)
        # alternatively, could use regex
        # word = '\\b' + word + '\\b'
        # features = features + ', ' + str(len(re.findall(word,twt)))
        featurefile.write(featurestring + '\n')
    twtfile.close()
    featurefile.close()
    return None 



