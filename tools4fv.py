# this module contains some tools for 
# generating feature vectors (fv) for text strings (e.g., tweets)

import time 
import pickle
import copy

import numpy as np
import pandas as pd 

# tweet info data frame columns:
#    NAME          DATATYPE 
#    twtid ....... string (of digits)
#    raw ......... string
#    filtered .... string
#    userid ...... string (of digits)
#    handle ...... string
#    label ....... string

# tweet features data frame columns 
#    twtid ....... string (of digits)
#    feature 1 ... TF score for word 1
#    feature 2 ... TF score for word 2
#       :
#    feature n ... TF score for word n
#    label ....... string


def getwordmap(infofilename):
    """ returns dictionary (a.k.a. map) in which keys are words
        and values are corpus frequencies
        """

    pandasDF = pickle.load(open(infofilename, 'r'))
    wordmap = {}
    # filtered word set is just space-delimited string
    allfiltered = pandasDF.filtered 
    # loop through word sets:
    for thiswordstring in allfiltered:
        thiswordlist = thiswordstring.split()
        # loop through the words in the word set 
        for word in thiswordlist:
            # process the word:
            word = cleanword(word)
            if word != '':
                if word in wordmap.keys():
                    wordmap[word] = wordmap[word] + 1
                else:
                    wordmap.update({word: 1})
    return wordmap


def cleanword(wordstring):

    # convert all letters to lower case 
    word = wordstring.lower()
    # remove '\x ...' strings (i think they're emojis):
    # codecs.decode('\xf0\x9f\x98\xb7')
    if (r'\x' in word):
        word = ''
    return word 


def writetf(infofilename, featfilename, wordlist):
    """ writes term frequencies to the feature dataframe 
        corresponding to the elements of the wordlist
        """ 
    # read the tweet info data frame from file 
    infoDF = pickle.load(open(infofilename,'r'))
    twtidcol = copy.copy(infoDF[['twtid']])

    # initialize the feature data frame
    ntwts = len(infoDF)
    nwords = len(wordlist)
    allzeros = np.zeros((ntwts,nwords), dtype=int)
    # add "tf_" each word to name the feature
    featnamelist = ['tf_' + word for word in wordlist]
    justfeatures = pd.DataFrame(allzeros, columns = featnamelist)

    print 'processing tweets ...'
    # loop through both data frames and assign features
    for index in infoDF.index:  
        # get list of filtered words from info data frame
        thiswordlist = infoDF.loc[index,'filtered'].strip().split()
        # turn that into list of counts (as integers)
        featurelist = [thiswordlist.count(w) for w in wordlist]
        # assign that list to row of feature data frame 
        justfeatures.loc[index] = featurelist

    print 'handling pandas data frame ...'
    # make feature data frame with tweet IDs and zeroed features 
    featDF = pd.concat([twtidcol, justfeatures], axis=1)
    # pickle the features
    pickle.dump(featDF, open(featfilename, 'w'))
    return None 


def synclabels(fromfilename, tofilename):
    """ sychronizes labels between data frames, assuming 'from' 
        is correct 
        """
    # unpickle both data frames
    fromDF = pickle.load(open(fromfilename, 'r'))
    toDF = pickle.load(open(tofilename, 'r'))
    
    # check whether or not toDF already has a label     
    toDF['label'] = copy.copy(fromDF['label'])
    pickle.dump(toDF, open(tofilename, 'w'))
    return None



def writearff(featfilename): 
    """ writes features and classes in the feature data frame to an
        arff file (does NOT write TO the data frame pickle file)
        """

    # as always, unpickle the database:
    featDF = pickle.load(open(featfilename, 'r'))

    # deal with time stuff and construct output file name:
    writetime = time.gmtime()
    namestamp = time.strftime('%Y-%m-%d_%H:%m:%S', writetime)
    arffname = 'twtfeatures' + '_' + namestamp + '.arff'
    arff = open(arffname, 'w')

    # write comments:
    timestring = time.asctime(writetime) 
    timeheader = '% Written on: ' + timestring
    arff.write(timeheader)
    
    # write header: 
    # first, description of overall relation:
    featlist = list(featDF.columns)
    featlist.remove('twtid')
    featlist.remove('label')
    nfeats = len(featlist)
    reldesc = '@RELATION ' + 'tweetfeatures' + str(nfeats) + '\n\n'
    arff.write(reldesc)
    # next, write actual attribute descriptions  
    for name in featlist: 
        attrdesc = '@ATTRIBUTE %-15s NUMERIC \n' % name
        arff.write(attrdesc)
    # next, write class/label description 
    labelset = set([str(level) for level in featDF['label']])
    labelstring = '{' + ','.join(labelset) + '}'
    arff.write('@ATTRIBUTE %-15s ' % 'class' + labelstring + ' \n')
    arff.write('@DATA \n')

    # write content:
    for index in featDF.index: 
        # get current feature vector 
        thisfvlist = [str(feat) for feat in featDF.loc[index]]
        thisfvlist.remove('twtid')        
        thisfvstring = ','.join(thisfvlist) + '\n'
        arff.write(thisfvstring)
    arff.close()

    return None 

