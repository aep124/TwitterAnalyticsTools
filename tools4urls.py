# this module contains some tools for working with
# urls in tweets 

import urllib
import urlparse
import re
import os
import os.path

# TO DO
#     - account for multiple links
#     - add nativecheck to fullsave method

def gettco(text):
    # extracts the t.co-format url from the tweet text
    fromindex = re.search('t\.co', text).start()
    findend = re.search(' ', text[fromindex:])
    if findend!=None:
        toindex = findend.start() + fromindex
        tdotco = text[fromindex:toindex]
    else:
        tdotco = text[fromindex:]
    return tdotco

def getreal(tdotco):
    fullurl = 'http://' + tdotco
    realurl = urllib.urlopen(fullurl).geturl()
    return realurl

def nativecheck(myurl):
    r = urlparse.urlparse(myurl)
    domcheck = r.netloc=='twitter.com'
    pathcheck = re.search('photo',r.path)!=None
    if domcheck & pathcheck:
        check = True
    else:
        check = False
    return check

def getnimg(realurl):
    # takes an expanded URL to a native image - i.e., of the form: 
    # https://twitter.com/[username]/status/[tweet it]/photo/1
    # returns URL of the image itself (i.e., ends in .jpg, .png, etc.)
    content = urllib.urlopen(realurl).read()
    fromindex = re.search('img src=', content).end() + 1
    toindex = re.search('\"', content[fromindex:]).start() + fromindex
    imgurl = content[fromindex:toindex]
    return imgurl

def saveimg(imgurl, path, namestem):
    # starts with 
    #    (1) a url directly to the image file 
    #    (2) a path in any form 
    #        (e.g., relative or absoluote, existent or non)
    #    (3) a name to which an appropriate extension is added  
    # the approach used for binary file handling is demonstrated here:
    # http://code.activestate.com/recipes/577385-image-downloader/
    imgdata = urllib.urlopen(imgurl).read() 
    # get the appropriate file extension and add it to name:
    spliturl = re.split("\.", imgurl)
    ext = spliturl[len(spliturl)-1]
    filename = namestem + '.' + ext
    # expand and/or create path as necessary:
    if path[0]=='~':
        fullpath = os.path.expanduser(path)
    elif path[0]!='/':
        fullpath = os.getcwd() + '/' + path
    if not os.path.exists(fullpath): 
        os.makedirs(fullpath)
    # open a new file object and write data:  
    imgfile = open(fullpath + '/' + filename,'w') 
    imgfile.write(imgdata)
    imgfile.close()
    return fullpath

def fullsave(text, path, name=''):
    # this method conveniently strings together several others
    # executes a full save starting with the tweet text 
    stem = name
    tdotco = gettco(text)
    if name=='':
        stem = re.split('/',tdotco)[1]
    fullpath = saveimg(getnimg(getreal(tdotco)), path, stem)
    return fullpath
    
def ex_url():
    # this returns an example url
    # tweet id: 372445983231066112 
    return 't.co/uGCvOJZxw1'

def ex_plain():
    # returns example tweet with no URLs 
    # tweet id: 372515457158230016 
    return 'My favorite tea @TeasofTexas is now for sale at @WholeFoods in Tulsa and Oklahoma City. Love my Texas Tea!'   

def ex_noimg():
    # returns an example tweet text with non-image URL
    # tweet id: 372625505544986624 
    return 'so apparently twitter needs spaces or beginning/end of tweet surrounding url: make it so http://t.co/I5zYJdFyBC' 

def ex_n():
    # returns an example tweet with single URL to native image
    # tweet id: 372591759974359040  
    return 'photo duel. @IMGAVI http://t.co/pbAPBRVoKN'

def ex_3p():
    # returns an example tweet with single URL to image from 3rd part app
    # tweet id: 370637357147361281 
    return 'Try, try, try, let it ride. I did it - my longest drive yet! 110.15 meters closer to Mount Sharp. http://t.co/btiavKAJ0I'  


