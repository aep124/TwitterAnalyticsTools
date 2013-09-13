# this package contains some tools for applying labels

import webbrowser 
import sys
import random
import re

def labelmanually(infilename, pgsfilename, checksfilename, handlemap):
    # open files:
    # infeatures is the file from which to get unlabeled feature vectors:
    infeatures = open(infilename, 'r')
    # outfeatures is the file to which to write the labeled feature vectors:
    outfilename = re.split('\.', infilename)[0] + '_labeled.txt'
    outfeatures = open(outfilename, 'w')
    # pgs is the file of id #s and tweets directly output from PostGreSQL:
    pgs = open(pgsfilename, 'r')
    # checks is the filtered tweet file from which features were generated:
    checks = open(checksfilename, 'r')
    # labelfile is the file into which only labels are place
    # this file can later be used as the input for labelfromfile() 
    labelsonly = open('labelsonly', 'w')

    # loop through the input file
    for line in infeatures:
        # get lines from other files:
        idandtwt = pgs.readline().strip()
        twtid = idandtwt[0:18]
        twttext = idandtwt[18:]
        user = handlemap[twtid]
        checkline = checks.readline()
        # check whether this line has been labeled:
        lastel = line.split()[-1]
        if lastel.strip() in {'pos', 'neg'}:
            # if labeled simply transfer the line to the output file
            outfeatures.write(line)
            # write label to file for reference:
            label = lastel.strip()
            labelsonly.write(label + '\n')
        elif lastel.strip() in {'skipped','quit'}:
            # if skipped, apply manual labeling:
            label = getlabel(user, twtid, twttext)
            # write labeled features to outfile:
            featurevals = ' '.join(line.split()[:-1])
            outfeatures.write(featurevals + ', ' + label + '\n')
            # write label to file for reference:
            labelsonly.write(label + '\n')
            # conduct random check:
            runcheck(checkline)
        else:
            # if unlabeled, apply manual labeling:
            label = getlabel(user, twtid, twttext)
            # write labeled features to outfile:
            outfeatures.write(line.strip() + ', ' + label + '\n')
            # conduct random check:
            runcheck(checkline)
            # write label to file for reference:
            labelsonly.write(label + '\n')
        if label == 'quit':
            infeatures.close()
            outfeatures.close()
            pgs.close()
            checks.close()
            labelsonly.close()            
            break
    return None 

def labelfromfile(infilename, labelfilename):
    # open files:
    # infeatures is the file from which to get unlabeled feature vectors:
    infeatures = open(infilename, 'r')
    # outfeatures is the file to which to write the labeled feature vectors:
    outfilename = re.split('\.', infilename)[0] + '_labeled.txt'
    outfeatures = open(outfilename, 'w')
    # labelfile is the file from which to get the labels
    labelfile = open(labelfilename, 'r')

    # loop through the input file
    for line in infeatures:
        # get label from label file:
        label = labelfile.readline().strip()
        # check whether this line has been labeled:
        lastel = line.split()[-1]
        if lastel.strip() in {'pos', 'neg'}:
            # if labeled simply transfer the line to the output file
            outfeatures.write(line)
        elif lastel.strip() in {'skipped','quit'}:
            # if skipped, remove skipped label and add new label
            featurevals = ' '.join(line.split()[:-1])
            outfeatures.write(featurevals + ', ' + label + '\n')
        else:
            # if unlabeled, add new label
            outfeatures.write(line.strip() + ', ' + label + '\n')
    return None 


def getlabel(userhandle='', twtid='', twttext=''):
    # open tweet in browser:
    if (userhandle != '') & (twtid != ''):
        twturl = 'https://twitter.com/' + userhandle + '/status/' + twtid
        webbrowser.open(twturl) 
    # prepare prompt for user:
    initialtext = '"' + twttext[:20] + '..."'
    if twttext == '':
        prompt = 'Is this a positive instance? [y/n/skip] '
    else:
        prompt = 'Is ' + initialtext  + ' a positive instance? [y/n/skip/quit] '
    # assign label:
    label = ''
    while label == '':
        print(prompt)
        rawlabel = sys.stdin.readline()
        if rawlabel.strip() in {'y', 'yes', 'yeah', 'pos', 'positive'}:
            label = 'pos'
        elif rawlabel.strip() in {'n', 'no', 'neg', 'negative'}:
            label = 'neg'
        elif rawlabel.strip() in {'s','skip', 'skipped'}:
            label = 'skipped'
        elif rawlabel.strip() in {'q','quit'}:
            label = 'quit'
        else:
            print('Error: Input not understood, retry ') 
    return label

def exhandle():
    return 'SportsCenter'

def exid():
    return '377305730291740672'

def runcheck(twtcheckline):
    if random.random() > 0.9:
        checklist = twtcheckline.strip().split()
        nwords = min(5, len(checklist))
        checkwords = checklist[0:nwords]
        checkstring = ', '.join(checklist)
        checkmsg = '(this tweet should include: "' + checkstring + ' ..."'
        print(checkmsg)
    return None





