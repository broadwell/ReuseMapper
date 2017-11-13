#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import operator
import requests
import json
import argparse
from slugify import slugify
reload(sys)
sys.setdefaultencoding("utf-8")

# Max number of items on one side of the matrix -- parameter
maxBins = 1000
useCachedFiles = True # parameter
getDocTexts = False

# Base URL (with port) of the Intertextualitet site -- parameter
#itextBaseURL = 'http://ec2-34-224-27-91.compute-1.amazonaws.com:8080/'
itextBaseURL = 'http://localhost:8080/'
itextAPI = itextBaseURL + 'api/'

itextMatches = {}

bins = {}
binLabels = []
binLabelCounts = {}
docsToBins = {}

binsFile = open('bin_texts.txt', 'w')

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
  firstMetaURL = baseURL + query
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

def processArgs(args):

  global useCachedFiles, getDocTexts, maxBins, itextBaseURL, itextAPI

  print("processing command line args")

  if (not args.no_cache):
    useCachedFiles = False
  if args.get_texts:
    getDocTexts = True
  if ('bins' in args):
    maxBins = args.bins
    print("Set maxBins to ", maxBins)
  if ('url' in args):
    print("setting URL to " + args.url)
    itextBaseURL = args.url
    if (itextBaseURL[-1] != '/'):
      itextBaseURL += '/'
    itextAPI = itextBaseURL + 'api/'


if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Generate an interactive heatmap matrix of text reuse')
  parser.add_argument('--version', action='version', version='1.0.0')
  parser.add_argument('--bins', type=int, help='The number of "bins" on each dimension of the matrix. Affects the resolution of the heatmap. Default=1000.', default=1000)
  parser.add_argument('--url', help='The URL (with port number) of the running Intertextualitet service. Default=http://localhost:8080/', default='http://localhost:8080/')
  parser.add_argument('--no_cache', action='store_true', help='Do not use the previous results from the API that are stored locally. Will re-download all data. Default behavior is to use the cache.')
  parser.add_argument('--get_texts', action='store_true', help='Use to download the full text of each document. Can take a long time. Default behavior is not to download the texts.')
  parser.set_defaults(func=processArgs)

  args = parser.parse_args()
  args.func(args)

  print("base URL is now", itextBaseURL)

  print("Querying metadata")
  allDocs = apiHarvester(itextAPI, "metadata", "docs")
  print("Querying matches")
  allMatches = apiHarvester(itextAPI, "clustered_matches", "docs")

  print(len(allDocs), "metadata docs")
  print(len(allMatches), "clustered_matches")

  # XXX Sort keys also could be parameters (e.g., author first, then year)
  print("sorting docs")
  #allDocs.sort(key=lambda x: (int(x['metadata']['publication_year']), x['metadata']['title']))
  allDocs.sort(key=lambda x: x['filename'])

  print("Building intertext matrix")

  textMatches = {}

  for pair in allMatches:
    sourceDoc = pair['source_filename'].replace('.txt','')
    targetDoc = pair['target_filename'].replace('.txt','')
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
    # This makes the relations symmetrical (do they really need to be?)
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
                  colMatches.append(match['similarity'])
        if (len(colMatches) > 0):
          # XXX Use maximum match for the bin? Mean? Median?
          #binRow.append(str(numpy.mean(colMatches)))
          binRow.append(str(max(colMatches)))
        else:
          binRow.append("0")
      itextFile.write("\t".join(binRow) + "\n")
