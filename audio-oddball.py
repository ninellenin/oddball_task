#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2022.2.4),
    on Ноябрь 27, 2022, at 23:33
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding
import pylsl
import random
import datetime

import psychopy.iohub as io
from psychopy.hardware import keyboard

SCREEN_NUMBER = 0
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
EXPERIMENT_NAME = 'audio-oddball'

# Number of standard
STANDARD_NUMBER = 7
ODD_NUMBER = 3
CYCLES_NUMBER = 3

#Colors
BACKGROUND_COLOR = 'Black'
FIXATION_COLOR = 'White'

# Right bottom mark size for photosensor (set it to 0 to hide)
FIXATION_SIZE = 20
MARK_SIZE = 20

WINDOW = None


#========================================================
# Low Level Functions
#========================================================
def CreateSequence(standardNumber, oddNumber, cyclesNumber=1):
    sequence = []
    
    for i in range(cyclesNumber):
        for j in range(standardNumber):
            sequence.append(0)
        
        for f in range(oddNumber):
            sequence.append(1)
        
    #sequence.append([0 for x in range(standardNumber)])
    #sequence.append([1 for x in range(oddNumber)])
    #sequence = listFlatten(sequence)
    random.seed(datetime.datetime.now().timestamp())
    random.shuffle(sequence) # shuffles in-place

    for element in sequence:
        print(element)

    return sequence

def InitSessionInfo(experimentName):
    # Store info about the experiment session
    experimentInfo = {
        'Participant': f"{randint(0, 999999):06.0f}",
        'Session': '001',
    }

    return experimentInfo

def ShowStartDialog(experimentInfo, experimentName, psychopyVersion):
    # --- Show participant info dialog --
    dialog = gui.DlgFromDict(dictionary=experimentInfo, sortKeys=False, title=experimentName)
    if dialog.OK == False:
        core.quit()  # user pressed cancel
    
    experimentInfo['date'] = data.getDateStr()  # add a simple timestamp
    experimentInfo['experimentName'] = experimentName
    experimentInfo['psychopyVersion'] = psychopyVersion
    
    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    dataFilename = thisDirectory + os.sep + u'data/%s_%s_%s' % (experimentInfo['Participant'], experimentName, experimentInfo['date'])

    return dataFilename

def GetExperimentHandler(experimentInfo, experimentName, dataFilename):
    # An ExperimentHandler isn't essential but helps with data saving
    thisExperiment = data.ExperimentHandler(name=experimentName, version='',
        extraInfo=experimentInfo, runtimeInfo=None,
        originPath=thisDirectory + '\\audio-oddball.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataFilename)
    # save a log file for detail verbose info
    logFile = logging.LogFile(dataFilename+'.log', level=logging.EXP)
    logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

    return thisExperiment

def CreateFixationStimulus(window):
    fixation = visual.TextStim(window, 
        '+',
        color='White', 
        #colorSpace='rgb',  
        pos = (0, 0))
    
    return fixation
    
def CreatePhotosensor(window, size=15):
    photosensor = visual.Rect(
            win=window,
            units="pix",
            width=size,
            height=size,
            fillColor=(1, 1, 1),
            lineColor=(1, 1, 1),
            lineWidth = 1,
            name = 'off', # Used to determine state
            pos = ((WINDOW_WIDTH / 2) - size, -((WINDOW_HEIGHT / 2) - size))
        )
    
    return photosensor

# Main Scenario
if __name__ == "__main__": 
    # Ensure that relative paths start from the same directory as this script
    thisDirectory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(thisDirectory)

    experimentName = EXPERIMENT_NAME
    psychopyVersion = '2022.2.4'
    experimentInfo = InitSessionInfo(experimentName)

    dataFilename = ShowStartDialog(experimentInfo, experimentName, psychopyVersion)

    # An ExperimentHandler isn't essential but helps with data saving
    thisExperiment = GetExperimentHandler(experimentInfo, experimentName, dataFilename)

    frameTolerance = 0.001  # how close to onset before 'same' frame

    # Start Code - component code to be run after the window creation

    # --- Setup the Window ---
    window = visual.Window(
        size=SCREEN_SIZE, 
        fullscr=False, 
        screen=SCREEN_NUMBER, 
        winType='pyglet',
        allowStencil=False,
        monitor='testMonitor',
        color=BACKGROUND_COLOR,
        blendMode='avg', 
        useFBO=True, 
        units='height')
    window.mouseVisible = False
    
    stim = CreateFixationStimulus(window)
    
    CreateSequence(STANDARD_NUMBER, ODD_NUMBER)

    size = MARK_SIZE
    bg_color = [1, 1, 1]
    photosensor = CreatePhotosensor(window)
    # store frame rate of monitor if we can measure it
    experimentInfo['frameRate'] = window.getActualFrameRate()
    if experimentInfo['frameRate'] != None:
        frameDur = 1.0 / round(experimentInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    # --- Setup input devices ---
    ioConfig = {}

    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')

    ioSession = '1'
    if 'session' in experimentInfo:
        ioSession = str(experimentInfo['session'])
    ioServer = io.launchHubServer(window=window, **ioConfig)
    eyetracker = None

    # create a default keyboard (e.g. to check for escape)
    defaultKeyboard = keyboard.Keyboard(backend='iohub')

    # --- Initialize components for Routine "trial" ---

    # Create some handy timers
    globalClock = core.Clock()  # to track the time since experiment started
    routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine 

    # --- Prepare to start Routine "trial" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    # keep track of which components have finished
    trialComponents = []
    for thisComponent in trialComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = window.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine "trial" ---
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = window.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = window.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
            
        # check for quit (typically the Esc key)
        keys = defaultKeyboard.getKeys(keyList=["escape"])
        if keys:
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        #continueRoutine = False  # will revert to True if at least one component still running
        
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        continueRoutine = True
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            stim.draw()
            photosensor.draw()
            window.flip()

    # --- Ending Routine "trial" ---
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "trial" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # --- End experiment ---
    # Flip one final time so any remaining win.callOnFlip() 
    # and win.timeOnFlip() tasks get executed before quitting
    window.flip()

    # these shouldn't be strictly necessary (should auto-save)
    thisExperiment.saveAsWideText(dataFilename+'.csv', delim='auto')
    thisExperiment.saveAsPickle(dataFilename)
    logging.flush()
    # make sure everything is closed down
    if eyetracker:
        eyetracker.setConnectionState(False)
    thisExperiment.abort()  # or data files will save again on exit
    window.close()
    core.quit()
