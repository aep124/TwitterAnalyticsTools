# this module contains some tools for working with
# urls in tweets 

import urllib2
import urlparse
import re
import os
import os.path
import urlparse

# TO DO
#     - account for multiple links
#     - add nativecheck to fullsave method


def connectionOK():
    """ checks network connection by trying to open google """

    check = False
    try:
        testconn = urllib2.urlopen('http://www.google.com')
        if (str(testconn.getcode()) == '200'):
            print('network connection OK')
            check = True
        else:
            print('error: network connection could not be established')
    except:
        print('error: network connection could not be established')
    return check



def hasnimage(twt):
    """ returns True/False depending on whether an native image
        is linked to from the tweet   
        """

    check = False
    try:
        tdotco = gettco(twt)
        if (tdotco != None): 
            realurl = getreal(tdotco)
            if (realurl != None):
                if nativecheck(realurl):
                    check = True
    except:
        check = False
    return check
       

def gettco(text):
    """ returns the t.co-format url (in form "t.co ..." from the 
        tweet text or None if t.co does not appear in the text
        """
    
    tdotco = None
    tcosearch = re.search('t\.co', text)
    if (tcosearch != None):
        fromindex = tcosearch.start()
        findend = re.search(' ', text[fromindex:])
        if (findend != None):
            toindex = findend.start() + fromindex
            tdotco = text[fromindex:toindex]
        else:
            tdotco = text[fromindex:]
    return tdotco


def getshort(text):
    """ returns the shortened url (in form "http:// ...") from 
        the tweet text or None if no url appears in the text
        """
    short = None
    urlsearch = re.search('http', text)
    if (urlsearch != None):
        fromindex = urlsearch.start()
        findend = re.search(' ', text[fromindex:])
        if (findend != None):
            toindex = findend.start() + fromindex
            short = text[fromindex:toindex]
        else:
            short = text[fromindex:]
    return short


def getreal(tdotco):
    """ returns full url, assuming shortened url 
        is given as "t.co ... " 
        """

    fullurl = 'http://' + tdotco
    urlobj = urllib2.urlopen(fullurl)
    realurl = None
    if (urlobj.getcode() == 200):
        realurl = urlobj.geturl() 
    return realurl


def getfull(short, time=5):
    """ returns full url, assuming shortened url 
        is given as "http://... " 
        """
    try:
        urlobj = urllib2.urlopen(short, None, time)
        # urllib2 needed for timeout parameter 
        full = None
        if (urlobj.getcode() == 200):
            full = urlobj.geturl() 
    except:
        full = None
    return full


def has3pimg(full):
    """ returns true if expanded url points to 
        3rd-party image platform """
        
    # essentially redundant with getgenlimg()
    imgdoms = ['twitpic.com','twitter.yfrog.com']
    urlobj = urlparse.urlparse(full)
    domain = urlobj.netloc
    check = (domain in imgdoms)
    return check


def hasYouTubeVid(full):
    """ returns true if expanded url points to youtube video """
        
    urlobj = urlparse.urlparse(full)
    domain = urlobj.netloc
    check = ((domain=='youtube.com') | (domain=='www.youtube.com'))
    return check


def nativecheck(myurl):
    r = urlparse.urlparse(myurl)
    domcheck = r.netloc=='twitter.com'
    pathcheck = re.search('photo',r.path)!=None
    if domcheck & pathcheck:
        check = True
    else:
        check = False
    return check



def getnimg(fullurl):
    """ returns URL of image itself (i.e., ends in .jpg, .png, etc.)
        takes an expanded URL to a native image - i.e., of the form: 
        https://twitter.com/[username]/status/[tweet id]/photo/1
        """

    htmlsrc = urllib2.urlopen(fullurl).read()
    fromindex = re.search('img src=', htmlsrc).end() + 1
    toindex = re.search('\"', htmlsrc[fromindex:]).start() + fromindex
    imgurl = htmlsrc[fromindex:toindex]
    return imgurl


def getgenlimg(fullurl):
    """ returns URL of image itself (i.e., ends in .jpg, .png, etc.)
        takes an expanded URL to a native image - i.e., of the form: 
        https://twitter.com/[username]/status/[tweet id]/photo/1
        """
    
    # get the domain:
    parsed = urlparse.urlparse(fullurl)
    domain = parsed.netloc
    # get the actual html content of the page  
    htmlsrc = urllib2.urlopen(fullurl).read()
    imgurl = None

    # if the image is natively hosted, jump through the normal hoops 
    if domain=='twitter.com':
        try:
            codelocation = re.search('img src=', htmlsrc)
            fromindex = codelocation.end() + 1
            urllength = re.search('\"', htmlsrc[fromindex:]).start()
            toindex =  fromindex + urllength
            imgurl = htmlsrc[fromindex:toindex]
        except:
            imgurl = None

    # if 3rd-party app, look for something like these lines
    # <meta name="twitter:image" value="https://twitpic.com/show/large/3b499b.jpg" />
    # <meta name="twitter:image" value="http://a.yfrog.com/img220/7493/9ri.jpg" />
    elif ((domain=='twitpic.com') | (domain=='twitter.yfrog.com')):
        try:
            linestart = re.search('twitter:image', htmlsrc).end()
            dist2url = re.search('http', htmlsrc[linestart:]).start()
            fromindex = linestart + dist2url
            urllength = re.search('"', htmlsrc[fromindex:]).start()
            toindex =  fromindex + urllength
            imgurl = htmlsrc[fromindex:toindex]
        except:
            imgurl = None
    
    else:
        pass
        #msg = 'could not find image url in ' + fullurl
        #print msg

    return imgurl



def saveimg(imgurl, path='', namestem='autosavedimg'):
    """ saves image to disk, starting with 
        (1) a url directly to the image file (e.g., ending in .jpg)
        (2) a path in any form 
            (e.g., relative or absolute, existent or non)
        (3) a name to which an appropriate extension is added  
            approach used for binary file handling  demonstrated here:
            http://code.activestate.com/recipes/577385-image-downloader/
        """

    imgdata = urllib2.urlopen(imgurl).read() 
    # get the appropriate file extension and add it to name:
    spliturl = re.split("\.", imgurl)
    ext = spliturl[len(spliturl)-1]
    filename = namestem + '.' + ext
    # expand and/or create path as necessary:
    if (len(path) > 0): # path was specified 
        # remove trailing "/" 
        if (path[len(path)-1]=='/'):
            path = path[:len(path)-1]
        if path[0]=='~':
            fullpath = os.path.expanduser(path)
        elif (path[0]!='/'):
            fullpath = os.getcwd() + '/' + path
        # create path if non-existent 
        if not os.path.exists(fullpath): 
            os.makedirs(fullpath)
    else: # if path isn't specified, just use current directory 
        fullpath = os.getcwd()
    # open a new file object and write data:  
    fullname = fullpath + '/' + filename
    imgfile = open(fullname,'w') 
    imgfile.write(imgdata)
    imgfile.close()
    return fullname



def fullsave(text, path='', stem='autosavedimg'):
    """ wrapper for saveimg() that starts with tweet text """

    tdotco = gettco(text)
    # if the name is unspecified, use the t.co extension 
    if stem=='':
        stem = re.split('/',tdotco)[1]
    if hasnimage(text):
        fullname = saveimg(getnimg(getreal(tdotco)), path, stem)
    return fullname


    
def ex_url():
    """  this returns an example url; tweet id: 372445983231066112 """
    return 't.co/uGCvOJZxw1'

def ex_plain():
    """ returns example tweet with no URLs
        tweet id: 372515457158230016 
         """
    return 'My favorite tea @TeasofTexas is now for sale at @WholeFoods in Tulsa and Oklahoma City. Love my Texas Tea!'   

def ex_noimg():
    """ returns an example tweet text with non-image URL
        tweet id: 372625505544986624 
        """
    return 'so apparently twitter needs spaces or beginning/end of tweet surrounding url: make it so http://t.co/I5zYJdFyBC' 

def ex_n():
    """ returns an example tweet with single URL to native image
        tweet id: 372591759974359040  
        """
    return 'photo duel. @IMGAVI http://t.co/pbAPBRVoKN'

def ex_wfaces():
    """ returns example tweet with native image that has good 
        example of faces - tweet id 440322224407314432 
        """
    return "If only Bradley's arm was longer. Best photo ever. #oscars http://t.co/C9U5NOtGap"
 

def ex_3p():
    """ returns an example tweet with single URL to image from 3rd part app
        tweet id: 370637357147361281 
        """
    return 'Try, try, try, let it ride. I did it - my longest drive yet! 110.15 meters closer to Mount Sharp. http://t.co/btiavKAJ0I'  


