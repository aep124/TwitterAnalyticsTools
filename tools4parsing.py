# this package contains some tools for dealing with tweets in conjunction with CMU POS tagger 

import pickle

def getkeepset(filename):
    """ returns a set of tags from the file
        each line of the file must begin with a CMU POS tag
        (rest of the line is irrelevant)
        """

    keepfile = open(filename, 'r')
    keepset = set()
    for line in keepfile:
        keepset.add(line[0])
    return keepset


def writefiltered(dbfilename, keepset):
    """ runs the CMU POS tagger and populates the 'filtered' 
        field of the database as a list of words
        """
    # unpickle database:
    nativedb = pickle.load(open(dbfilename, 'r'))
    
    # write raw tweets from db to file
    writefile = open('rawtwts','w')
    for entry in nativedb:
        writefile.write(entry['raw'] + '\n')
    writefile.close()

    # run tagger:
    infile = open('rawtwts','r')
    outfile = open('taggedtwts','w')
    subprocess.call('./runTagger', stdin = infile, stdout = outfile)
    infile.close()
    outfile.close()

    # retrieve filtered tweets from file and write to db:
    taggedfile = open('taggedtwts', 'r') 
    cnt = 0
    for line in taggedfile:
        words = line.split('\t')[0]
        tags = line.split('\t')[1]
        tuples = zip(words.split(), tags.split())
        words = [wt[0] for wt in tuples if wt[1] in keepset]
        nativedb[cnt].update({'filtered': words})
        cnt = cnt + 1
    taggedfile.close()

    # re-pickle the database and exit
    pickle.dump(nativedb, open(dbfilename, 'w'))
    return None 

    
def extagged():
   return 'I predict I won\'t win a single game I bet on . Got Cliff Lee today , so if he loses its on me RT @e_one : Texas ( cont ) http://tl.gd/6meogh	O V O V V D A N O V P , V ^ ^ N , P P O V L P O ~ @ ~ ^ , ~ , U	0.9983 0.9996 0.9981 0.9981 0.9993 0.9987 0.9758 0.9988 0.9922 0.9995 0.7823 0.9919 0.9884 0.9926 0.9998 0.9899 0.9988 0.6624 0.9970 0.9979 0.9996 0.9865 0.9871 0.9986 0.9650 0.9987 0.9672 0.9989 0.9681 0.9239 0.9280 0.9973	I predict I won\'t win a single game I bet on. Got Cliff Lee today, so if he loses its on me RT @e_one: Texas (cont) http://tl.gd/6meogh'
   

