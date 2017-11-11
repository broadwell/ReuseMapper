#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#import unicodedata
#from jcconv import *
import operator
import requests
import json
from slugify import slugify
reload(sys)
sys.setdefaultencoding("utf-8")

# Max number of items on one side of the matrix -- parameter
#maxBins = 2000
maxBins = 100
useCachedFiles = True # parameter
getDocTexts = True

# Base URL (with port) of the Intertextualitet site -- parameter
itextBaseURL = 'http://ec2-34-224-27-91.compute-1.amazonaws.com:8080/'
itextAPI = itextBaseURL + 'api/'

itextMatches = {}

def queryPage(url):

  cacheFilename = slugify(url)
  if ((os.path.isfile('cache/' + cacheFilename)) and useCachedFiles):
    with open('cache/' + cacheFilename, 'r') as cacheFile:
      pageData = json.load(cacheFile)
  else:
    print("querying", url)
    r = requests.get(url)
    pageData = r.json()
    with open('cache/' + cacheFilename, 'w') as cacheFile:
      json.dump(pageData, cacheFile)
  return pageData

def apiHarvester(baseURL, query, key):
  firstMetaURL = itextAPI + query
  firstMetaPage = queryPage(firstMetaURL)
  totalDocs = firstMetaPage['total']

  # Should grab the metadata 1000 docs at a time to avoid
  # overloading the mongo DB
  print("Querying all", totalDocs, "documents in", query)
  offset = 0
  docsRead = 0
  maxLimit = 1000

  allDocs = []

  while (docsRead < totalDocs):
    limit = min(maxLimit, totalDocs - docsRead)
    metaURL = firstMetaURL + '?offset=' + str(docsRead) + '&limit=' + str(limit)
    thisContent = queryPage(metaURL)
    for item in thisContent[key]:
      allDocs.append(item)
    docsRead += limit

  return allDocs

print("Querying metadata")
allDocs = apiHarvester(itextBaseURL, "metadata", "docs")
print("Querying matches")
allMatches = apiHarvester(itextBaseURL, "clustered_matches", "docs")

print(len(allDocs), "metadata docs")
print(len(allMatches), "clustered_matches")

# XXX Sort keys also could be parameters (e.g., author first, then year)
print("sorting docs")
#allDocs.sort(key=lambda x: (int(x['metadata']['publication_year']), x['metadata']['title']))
allDocs.sort(key=lambda x: x['filename'])

bins = {}
binLabels = []
binLabelCounts = {}
docsToBins = {}

binsFile = open('bin_texts.txt', 'w')

def bankBinDocs(docsInBin):
  global binLabelCounts, binlabels, bins, docsToBins, binsFile, iTextMatches

  firstID = docsInBin[0]['filename'].replace('.txt', '')

  if (firstID in binLabelCounts):
    binLabelCounts[firstID] += 1
    binID = firstID + str(binLabelCounts[firstID])
  else:
    binID = firstID
    binLabelCounts[firstID] = 0
  binLabels.append(binID)

  binText = ""

  bins[binID] = []

  binMatches = {}

  binJSON = {'docs': {}, 'docsInBin': [], 'matches': {}, 'rawtext': '', 'label': binID}
  for doc in docsInBin:
    dID = doc['filename'].replace('.txt', '')
    bins[binID].append(dID)
    docsToBins[dID] = binID
    binJSON['docs'][dID] = doc
    binJSON['docsInBin'].append(dID)

    if (dID in itextMatches):
      for matchID in itextMatches[dID]:
        if (dID in binMatches):
          if (matchID in binMatches[dID]):
            for m in itextMatches[dID][matchID]:
              if (m not in binMatches[dID][matchID]):
                binMatches[dID][matchID].append(m)
          else:
            binMatches[dID][matchID] = itextMatches[dID][matchID]
        else:
          binMatches[dID] = {matchID: itextMatches[dID][matchID]}

    if (getDocTexts):
      fileID = doc['file_id']
      # Also grab the doc texts and put them in a folder?
      textInfo = queryPage(itextAPI + 'texts/' + str(fileID))
      docText = textInfo[0]['text']
      binText += docText + " "
      binJSON['docs'][dID]['text'] = docText

  if (getDocTexts):
    binsFile.write(binText + "\n")

  binJSON['rawtext'] = binText

  binJSON['matches'] = binMatches

  with open('binsJSON/' + binID + ".json", "w") as binFile:
    json.dump(binJSON, binFile)

print("Building intertext matrix")

textMatches = {}

for pair in allMatches:
  sourceDoc = pair['source_filename'].replace('.txt','')
  targetDoc = pair['target_filename'].replace('.txt','')
  #similarity = pair['similarity']
  matchText = pair['target_match']

  if (matchText in textMatches):
    textMatches[matchText] += 1
  else:
    textMatches[matchText] = 1

  if (sourceDoc not in itextMatches):
    itextMatches[sourceDoc] = {targetDoc: [pair]}
  else:
    if (targetDoc in itextMatches[sourceDoc]):
      itextMatches[sourceDoc][targetDoc].append(pair)
    else:
      itextMatches[sourceDoc][targetDoc] = [pair]
  # This makes the relations symmetrical (not sure they should be)
  if (targetDoc not in itextMatches):
    itextMatches[targetDoc] = {sourceDoc: [pair]}
  else:
    if (sourceDoc in itextMatches[targetDoc]):
      itextMatches[targetDoc][sourceDoc].append(pair)
    else:
      itextMatches[targetDoc][sourceDoc] = [pair]

sortedMatches = sorted(textMatches.iteritems(), key=operator.itemgetter(1))
sortedMatches.reverse()

with open('itext_phrases.txt', 'w') as phrasesFile:
  for match in sortedMatches:
    if (match[1] > 1):
      #print(match[0] + ": " + str(match[1]))
      phrasesFile.write(match[0] + "\t" + str(match[1]) + "\n")

print("Populating doc bins")

docsPerBin = 1

if (len(allDocs) > maxBins):
  docsPerBin = len(allDocs) / maxBins

print(docsPerBin, "docs per bin")

spaceInBin = docsPerBin
docsInBin = []

for doc in allDocs:
  docID = doc['filename'].replace('.txt', '')
  docsInBin.append(doc)

  spaceInBin -= 1
  if (spaceInBin < 1):
    bankBinDocs(docsInBin)
    spaceInBin += docsPerBin
    docsInBin = []

if (len(docsInBin) > 0):
  bankBinDocs(docsInBin)

print("Writing labels file")
with open("bin_labels.txt", "w") as labelsFile:
  for label in binLabels:
    labelsFile.write(label + "\n")

print ("Building intertextualitet similarity matrix for bins")
with open("itext_sim.txt", 'w') as itextFile:
  for binLabel1 in binLabels:
    binRow = []
    bl1docs = []
    for docID in bins[binLabel1]:
      bl1docs.append(docID)
    for binLabel2 in binLabels:
      if (binLabel1 == binLabel2):
        binRow.append("1")
        continue
      bl2docs = []
      for docID in bins[binLabel2]:
        bl2docs.append(docID)
      colMatches = []
      for docID1 in bl1docs:
        if (docID1 in itextMatches):
          for docID2 in bl2docs:
            if (docID2 in itextMatches[docID1]):
              for match in itextMatches[docID1][docID2]:
                colMatches.append(match['similarity'])
      for docID2 in bl2docs:
        if (docID2 in itextMatches):
          for docID1 in bl1docs:
            if (docID1 in itextMatches[docID2]):
              for match in itextMatches[docID2][docID1]:
                # Dumb way to avoid double-counting matches
                #if (match not in colMatches):
                colMatches.append(match['similarity'])
      if (len(colMatches) > 0):
        # XXX Use maximum match for the bin? Mean? Median?
        #binRow.append(str(numpy.mean(colMatches)))
        binRow.append(str(max(colMatches)))
      else:
        binRow.append("0")
    itextFile.write("\t".join(binRow) + "\n")
