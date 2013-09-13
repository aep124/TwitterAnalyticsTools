
# this package contains some tools for dealing with tweets in conjunction with CMU POS tagger 


import re 

def getkeepset(filename):
    # this function reads file with a line for each POS tag we want to keep
    # each line of the file must begin with a POS tag
    # it returns a set containing these tags
    keepfile = open(filename, 'r')
    keepset = set()
    for line in keepfile:
        keepset.add(line[0])
    return keepset

def writefiltered(keepset, tagsfilename, wordsfilename='filteredtwts'):
    # this function takes the CMU POS tagger output (text file) 
    # and generates another text file with only particular parts of speech
    tagfile = open(tagsfilename,'r')
    wordsfile = open(wordsfilename,'w')
    for line in tagfile:
        splitstr = re.split('\t', line)
        w = re.split(' ', splitstr[0])
        t = re.split(' ', splitstr[1])
        words = [w[ii] for ii in range(len(w)) if t[ii] in keepset]
        wordscat = ' '.join(words)
        wordsfile.write(wordscat + '\n')
    wordsfile.close()
    return None 
    
def extagged():
   return 'I predict I won\'t win a single game I bet on . Got Cliff Lee today , so if he loses its on me RT @e_one : Texas ( cont ) http://tl.gd/6meogh	O V O V V D A N O V P , V ^ ^ N , P P O V L P O ~ @ ~ ^ , ~ , U	0.9983 0.9996 0.9981 0.9981 0.9993 0.9987 0.9758 0.9988 0.9922 0.9995 0.7823 0.9919 0.9884 0.9926 0.9998 0.9899 0.9988 0.6624 0.9970 0.9979 0.9996 0.9865 0.9871 0.9986 0.9650 0.9987 0.9672 0.9989 0.9681 0.9239 0.9280 0.9973	I predict I won\'t win a single game I bet on. Got Cliff Lee today, so if he loses its on me RT @e_one: Texas (cont) http://tl.gd/6meogh'
   

