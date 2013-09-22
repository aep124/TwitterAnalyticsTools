# this is a script to retrieve and process text-only data for classification

# This process includes four main tasks
#    1) getting raw tweets 
#    2) apply labels (this step can be conducted at any time)
#    2) filtering those tweets (e.g., according to CMU POS tagger)
#    3) deriving a set of features (a.k.a. word list)
#    4) write the feature vectors to an arff file 

import tools4pgs 
import tools4parsing 
import tools4fv 
import tools4labeling
# in case the handlemap (or anything else) needs to be pickled
import pickle

# dictionary entry names:
#    NAME         TYPE 
#    twtid ...... string (of digits)
#    raw ........ string
#    filtered ... string
#    userid ..... string (of digits)
#    handle ..... string
#    features ... list
#    labels ..... tuple of strings (actlabel, timelabel)

#################### (1) Get Tweets ####################
tools4pgs.writenativedb('data.p')
tools4pgs.writecheck4imgs('data.p')


#################### (2) Apply Labels ####################
labelmap = tools4labeling.getlabelmap('labelsystem')
tools4labeling.writelabels('data.p', labelmap)



#################### (3) Filter ####################
keepset = tools4parsing.getkeepset('POS2keep') 
tools4parsing.writefiltered('data.p', keepset) 
# TODO: add functionality for reply tweets (conversations) ????????


#################### (4) Derive Features ####################
wordmap = tools4fv.getwordmap('data.p')
wordlist = wordmap.keys()
# specify threshold directly :
# freq_threshold = 2
# could also specify threshold by number of words (e.g., 500):
# freq_threshold = sorted(wordmap.values())[-500]
# wordlist = [w for w in wordmap.keys() if wordmap[w] >= freq_threshold]
tools4fv.writefeatures('data.p', wordlist)


#################### (5) Make ARFF File ####################
tools4fv.writearff('data.p', wordlist) 



























