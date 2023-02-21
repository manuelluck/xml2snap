# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 09:30:11 2022

@author: Manuel A. Luck
         luck@ifu.baug.ethz.ch , manuel.luck@gmail.com
         Ph.D. Candidate in Environmental Engineering, ETH Zurich 
"""

# %% Import:
import sys

from snappy import GPF
from snappy import ProductIO
from snappy import HashMap

#%% function
def xml2tasks(file,printTasks=False):
    """
    

    Parameters
    ----------
    file : string
        Path of .xml file.
    printTasks : boolean, optional
        Printing all tasks. The default is False.

    Returns
    -------
    tasks : dict()
        Dictionary with tasks as individual dictionaries.

    """
    with open(file) as f:
        lines = f.readlines()
    
    f.close()
    
    # Trouble shoot lines which are too long
    linesCorr = list()        
    for i in range(len(lines)):
        while lines[i][0] == ' ':
            lines[i] = lines[i][1:]
        if lines[i][0] == '<':
            linesCorr.append(lines[i])
        else:
            linesCorr[-1] = linesCorr[-1]+lines[i]  
            
    tasks   = dict()
    par     = False
    sor     = False   
    # creating tasks     
    for line in linesCorr:
        if '<node ' in line:                                                   # node marks new task
            # get name and nr 
            seg     = line.split('"')[1]
            if '(' in seg:
                nr  = seg.split('(')[1]
                nr  = nr.replace(')','')
                seg = seg.split('(')[0]
            else:
                nr = '1'
                
            # setting up dict()
            tasks[seg+nr]               = dict()
            tasks[seg+nr]['name']       = seg
            tasks[seg+nr]['nr']         = nr
            tasks[seg+nr]['operator']   = ''
            tasks[seg+nr]['parameters'] = dict()
            tasks[seg+nr]['sources']    = dict()
            tasks[seg+nr]['nextTask']   = dict()
            
        elif '<operator>' in line:                                             # operator marks SNAP - function
            op                          = line.split('>')[1]
            op                          = op.split('<')[0]
            tasks[seg+nr]['operator']   = op
            
        elif '<parameters ' in line:                                           # following lines should be parameters
            par     = True
            
        elif '</parameters>' in line:                                          # following lines should NOT be parameters
            par     = False
            
        elif par == True:                                                      # saving parameter in task['parameters'] dict()
            l       = line.split('</')[0]
            l       = l.replace('<','')
            n,v     = l.split('>')[0:2]
            if n[-1] != '/' and '&quot' not in v:
                tasks[seg+nr]['parameters'][n]  = v
    
        elif '<sources>' in line:                                              # following lines should be sources
            sor     = True
        elif '</sources>' in line:                                             # following lines should not be sources
            sor     = False
        elif sor == True:                                                      # get source name and nr
            if 'sourceProduct' in line:
                segS     = line.split('"')[1]
                if '(' in segS:
                    nrS  = segS.split('(')[1]
                    nrS  = nrS.replace(')','')
                    segS = segS.split('(')[0]
                else:
                    nrS = '1'
        
                tasks[seg+nr]['sources'][segS+nrS] = {'name':segS,'nr':nrS}

        elif 'Presentation' in line:                                           # following lines are SNAP internal visualization parameters
            break

    for t in tasks.keys():                                                     # get nextTask name and nr by sources of other tasks 
        for s in tasks[t]['sources'].keys():
            tasks[tasks[t]['sources'][s]['name']+tasks[t]['sources'][s]['nr']]['nextTask'][t] = {'name':tasks[t]['name'],'nr':tasks[t]['nr']}
            
    
    if printTasks == True:                                                     # printing all tasks 
        for t in tasks.keys():
            print(' ')
            print(' ----- ')
            print(' ')
            print('Task:')
            print(tasks[t]['name']+' - '+tasks[t]['nr'])
            print(' ')
            print('Parameters:')
            for p in tasks[t]['parameters'].keys():
                print(p+': '+tasks[t]['parameters'][p])
            print(' ')
            print('Sources:')    
            for s in tasks[t]['sources'].keys():
                print(s+': '+tasks[t]['sources'][s]['name']+' - '+tasks[t]['sources'][s]['nr'])
            print(' ')
            print('Next Task:')
            for n in tasks[t]['nextTask'].keys():
                print(n+': '+tasks[t]['nextTask'][n]['name']+' - '+tasks[t]['nextTask'][n]['nr'])
    
    return tasks

class SNAPtask:
    def __init__(self,name,nr,operator,parameters):
        """
        

        Parameters
        ----------
        name : string
            Task name.
        nr : string
            Task nr.
        operator : string
            Task SNAP-function.
        parameters : dict()
            Task parameters as dict

        Returns
        -------
        None.

        """
        self.name       = name
        self.nr         = nr
        self.parameters = parameters
        self.operator   = operator
        
        self.hashMap    = ''
        self.status     = 'pending'
        self.image      = ''
        
        self.nextTask   = list()
        self.sources    = list()
        
    def __createHashmap(self):
        """
        creates SNAP hashMap from self.parameters

        Returns
        -------
        None.

        """
        self.hashMap = HashMap()

        for key in self.parameters.keys():
            self.hashMap.put(key,self.parameters[key])
  
        
    def runTask(self):
        """
        Runs task using one of 3 functions (write,read, or create Product) with 
        setting saved in self.
        Recursivly runs pervious tasks if connected.
        self.image are the individual results

        Returns
        -------
        None.

        """
        self.__createHashmap()
        bands = ''

        print('     Checking: '+self.name+' - '+self.nr)
        while any([s.status == 'pending' for s in self.sources]):
            for s in self.sources:
                if s.status == 'pending':
                    s.runTask()
                    
        if 'sourceBands' in self.parameters.keys() and self.operator == 'Terrain-Correction':
            Names   = list(self.sources[0].image.getBandNames())
            bands   = []
            bands   += filter(lambda x: x.startswith('Amp'), Names)
            bands   += filter(lambda x: x.startswith('Phase'), Names)
            bands   += filter(lambda x: x.startswith('coh'), Names)
            bands   += filter(lambda x: x.startswith('Int'), Names)
            #bands   += filter(lambda x: x.startswith('i'), Names)
            #bands   += filter(lambda x: x.startswith('q'), Names)        
            bands   += filter(lambda x: x.endswith('VV'), Names)
            bands   += filter(lambda x: x.endswith('VH'), Names)
            bands   += filter(lambda x: x.endswith('HH'), Names)
            bands   += filter(lambda x: x.endswith('DEM'), Names)
            bands   += filter(lambda x: x.endswith('elevation'), Names)
            bands   += filter(lambda x: x.startswith('lay'), Names)
            
            string  = ''
            for idx in range(len(bands)):
                if idx == len(bands)-1:
                    string  += str(bands[idx])
                else:
                    string  += str(bands[idx]) + ','
            print('SourceBands: ' + string)
            self.hashMap.put('sourceBands',string)   

                
        if self.name != 'Read' and self.name != 'Write':
            print('Running: '+self.name+' - '+self.nr)
            self.image  = GPF.createProduct(self.operator,self.hashMap,[s.image for s in self.sources])
        elif self.name == 'Read':
            print('Reading: '+self.parameters['file'])
            self.image  = ProductIO.readProduct(self.parameters['file'])
        elif self.name == 'Write':
            print('Writing '+self.parameters['formatName']+' File: '+self.parameters['file'])
            ProductIO.writeProduct(self.sources[0].image, self.parameters['file'],self.parameters['formatName'])
        self.status     = 'finished'
        
        
def createTasksDict(tasks):
    """
    Creates Task Dictionary with individual task classes.

    Parameters
    ----------
    tasks : dict()
        Dictionary with individual dictionary for each task.

    Returns
    -------
    tDict : dict()
        Dictionary with individual SNAPtasks for each task.

    """
    tDict = dict()
    for task in tasks.keys():
        tDict[task] = SNAPtask(tasks[task]['name'],tasks[task]['nr'],tasks[task]['operator'],tasks[task]['parameters'])
    for t in tasks.keys():
        try:
            tDict[t].sources = [tDict[s] for s in tasks[t]['sources'].keys()]
        except:
            pass
        try:
            tDict[t].nextTask = [tDict[n] for n in tasks[t]['nextTask'].keys()]
        except:
            pass
            
    return tDict
        
def changeTasks(cmdIn,tasks):
    """
    

    Parameters
    ----------
    cmdIn : list of strings.
        List of stings (3 strings for each change) to change task (string 1), parameter (string 2) to value (string 3).
    tasks : dict()
        Dictionary with individual dictionary for each task.

    Returns
    -------
    tasks : dict()
        Dictionary with individual dictionary for each task.

    """
    cmdIn = cmdIn[1:]        
    if len(cmdIn) > 1:
        if (len(cmdIn[1:])%3)==0:
            for i in range(int(len(cmdIn[1:])/3)):
                print(cmdIn[i*3+1])
                if cmdIn[i*3+1][-1] in [str(i) for i in range(10)]:
                    try:
                        print(cmdIn[i*3+1]+' - '+cmdIn[i*3+2]+':\n'+ tasks[cmdIn[i*3+1]]['parameters'][cmdIn[i*3+2]])
                        print('Changed to:\n'+ cmdIn[i*3+3])
                        tasks[cmdIn[i*3+1]]['parameters'][cmdIn[i*3+2]] = cmdIn[i*3+3]
                    except:
                        print('Task - Parameter - Value not found.')
                else:
                    for key in tasks.keys():
                        if cmdIn[i*3+1] in key:
                            try:
                                print(key+' - '+cmdIn[i*3+2]+':\n'+ tasks[key]['parameters'][cmdIn[i*3+2]])
                                print('Changed to:\n'+ cmdIn[i*3+3])
                                tasks[key]['parameters'][cmdIn[i*3+2]] = cmdIn[i*3+3]
                            except:
                                print('Task - Parameter - Value not found.')
                                
    return tasks
            
        
        
# %% running all tasks ( works if last task is 'Write1')        
cmdIn = sys.argv

tasks = xml2tasks(cmdIn[1],printTasks=True)
tasks = changeTasks(cmdIn,tasks)


tDict = createTasksDict(tasks)

tDict['Write1'].runTask()

exit
