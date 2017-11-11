#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
Helper script to merge two tab-delimited matrices of the same dimensions.
Assumption is that they are both symmetrical across their main diagonal,
so merging them along this diagonal will produce a single matrix with
the combined similarity data of both. Output matrix file = imerged_sim.txt
"""

# IMPORTANT: Both matrices must be of the same dimensions, and tab-delimited

# The matrix produced by the ReuseMapper tool
iSim = open("itext_sim.txt", "r")
# Another similarity matrix, e.g. one produced by TextHeatmapper
tSim = open("dist_sim.txt", "r")

i = 0

mergedSim = []

for iLine in iSim:
  iRow = iLine.strip().split("\t")
  maxDim = len(iRow)
  tLine = tSim.readline()
  tRow = tLine.strip().split("\t")
  mergedRow = []

  for j in range(0,maxDim):
    if (j <= i):
      mergedRow.append(iRow[j])
    else:
      mergedRow.append(tRow[j])

  mergedSim.append(mergedRow)
  i += 1

with open("imerged_sim.txt", 'w') as tabFile:
  for row in mergedSim:
    rowData = [];
    for col in row:
      if ((col < .01) or (col == 0)):
        colStr = "0";
      else:
        colStr = str(col)
      rowData.append(colStr)
    rowStr = "\t".join(rowData)
    tabFile.write(rowStr + "\n");
