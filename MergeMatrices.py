#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import numpy
reload(sys)
sys.setdefaultencoding("utf-8")

iSim = open("itext_sim.txt", "r")
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
