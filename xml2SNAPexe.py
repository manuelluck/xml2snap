# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 09:30:11 2022

@author: Manuel A. Luck
         luck@ifu.baug.ethz.ch , manuel.luck@gmail.com
         Ph.D. Candidate in Environmental Engineering, ETH Zurich 
"""

# %% Import:
# ----------------------------------------------------------------------
import os
from subprocess import PIPE, call, Popen



# %% Code Example:
xml     = 'J:\\_PhD\\_Processing\\_XML\\PhaseTest.xml'   
    
read2   = "J:\_PhD\_Data\ASF_Download\Kaikoura2016\S1B_IW_SLC__1SSV_20161128T071352_20161128T071422_003155_0055E7_EDF9.zip"
read1   = "J:\_PhD\_Data\ASF_Download\Kaikoura2016\S1B_IW_SLC__1SDV_20161116T071350_20161116T071418_002980_005109_2DC8.zip"

for IW in ['IW1']:#,'IW2','IW3'
    output  = 'D:\\Documents\\Processing\\Kaikora\\Test'+IW+'after.dim'
    cmd     = ['D:\\Programme\\Python\\python.exe',
               'J:\\_PhD\\_Python\\_up2dateVersions\\SNAP\\xml2SNAP.py',
               xml,
               'Read1','file',read1,
               'Read2','file',read2,
               'TOPSAR-Split','subswath',IW,
               'TOPSAR-Split','selectedPolarisations','VV',
               'Write1','file',output]
    print(Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()[0].decode('utf-8').strip())


