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
import pickle
import copy
import numpy as np
import pandas as pd

# dividing into two dataframe because tweet info is fixed, but features are flexible
# tweet info data frame columns:
#    NAME          DATATYPE 
#    twtid ....... string (of digits)
#    raw ......... string
#    filtered .... string
#    userid ...... string (of digits)
#    handle ...... string
#    label ....... string
#    imgurl ...... string 

# tweet features data frame columns 
#    twtid ....... string (of digits)
#    feature 1 ... TF score for word 1
#    feature 2 ... TF score for word 2
#       :
#    feature n ... TF score for word n
#    label ....... string



############### (1) Get Tweets ################ 
# TODO: modify query handling to accomodate the column names that databases use, as well as subsets query variables 
# (this is written for robbery database) 
query = 'SELECT id,text,user_id FROM tweets'
condition = "WHERE text like '%bears%'"
tools4pgs.writetwtinfo(query, condition, 'twtinfo.p')


############### (2) Apply Labels ###############
labelmap = tools4labeling.getlabelmap('labelsystem')
tools4labeling.writelabels('twtinfo.p', labelmap)


################# (3) Filter ################
keepset = tools4parsing.getkeepset('POS2keep') 
tools4parsing.writefiltered('twtinfo.p', keepset) 
# TODO: add functionality for reply tweets (conversations) ????????


############## (4) Derive Features ##############
wordmap = tools4fv.getwordmap('twtinfo.p')
wordlist = wordmap.keys()
# specify threshold directly :
# freq_threshold = 2
# could also specify threshold by number of words (e.g., 500):
# freq_threshold = sorted(wordmap.values())[-500]
# wordlist = [w for w in wordmap.keys() if wordmap[w] >= freq_threshold]


tools4fv.writetf('twtinfo.p','twtfeatures.p', wordlist)
tools4fv.synclabels('twtinfo.p','twtfeatures.p')


############### (5) Make ARFF File ###############
#tools4fv.writearff('twtfeatures.p') 




















