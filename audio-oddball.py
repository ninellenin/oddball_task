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

# Import packages
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

from collections import namedtuple
from enum import Enum

import psychopy.iohub as io
from psychopy.hardware import keyboard

SCREEN_NUMBER = 0
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
EXPERIMENT_NAME = 'audio-oddball'
START_TEXT = 'Здравствуйте!\
Выполняйте задание клавиатурного тренажёра.\
Не обращайте внимания на сигналы'

# Number of standard
STANDARD_MIN_NUMBER = 3
STANDARD_MAX_NUMBER = 7
ODD_NUMBER = 1
CYCLES_NUMBER = 3
STIMULUS_SERIES_NUMBER = 30

# Colors
BACKGROUND_COLOR = 'Black'
FIXATION_COLOR = 'White'

# Right bottom mark size for photosensor (set it to 0 to hide)
FIXATION_SIZE = 20
MARK_SIZE = 20

# Use default
WINDOW = None

_thisDirectory = ''


 
class StimulusType(Enum):
    STANDARD = 0
    ODD = 1

# Declaring namedtuple()
Range = namedtuple('Range', ['Min', 'Max'])
StimulusInfo = namedtuple('StimulusInfo', ['Type', 'Duration'])

#========================================================
# Low Level Functions
#========================================================
def CreateStandardSequence(standardNumber, oddNumber, cyclesNumber=1):
    sequence = []
    for i in range(cyclesNumber):
        for j in range(standardNumber):
            sequence.append(0)
        
        for f in range(oddNumber):
            sequence.append(1)
    random.seed(datetime.datetime.now().timestamp())
    random.shuffle(sequence) # shuffles in-place

    return sequence

def CreateSequence(standardRange, oddNumber, stimulusNumber=30, standardTime=400, standardTimeRange=Range(700, 900), oddTime=400):
    sequence = []
    
    random.seed(datetime.datetime.now().timestamp())
    i = 0

    print("hello")
    print(f"standardRange = {standardRange}, oddNumber = {oddNumber}, stimulusNumber = {stimulusNumber}, standardTime = {standardTime}, str = {standardTimeRange}, oddTime = {oddTime}")

    while i < stimulusNumber:
        # Add Standard
        print(f'i = {i}')
        standardNumber = random.randint(standardRange.Min, standardRange.Max)
        standardTimes = [standardTime] * (standardNumber - standardRange.Min)

        for j in range(standardRange.Min):
            print(f'j1 = {j}')
            standardTimes.append(random.randint(standardTimeRange.Min, standardTimeRange.Max))
        random.shuffle(standardTimes)

        for j in range(standardNumber):
            print(f'j2 = {j}')
            sequence.append(StimulusInfo(StimulusType.STANDARD, standardTimes[j]))
            i += 1
        
        for j in range(oddNumber):
            print(f'j3 = {j}')
            sequence.append(StimulusInfo(StimulusType.ODD, oddTime))
            i += 1

    for i in range(stimulusNumber):
        print(f'({sequence[i]})')

    return sequence


def GetThisDirectory():
    global _thisDirectory
    
    if not _thisDirectory:
        # Ensure that relative paths start from the same directory as this script
        _thisDirectory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(_thisDirectory)

    return _thisDirectory

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
    
def CreateTextStimulus(window, text):
    fixation = visual.TextStim(window, 
        text,
        color='White', 
        pos = (0, 0))
    
    return fixation

def CreateFixationStimulus(window):    
    return CreateTextStimulus(window, '+')
    
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

def RunTrial(window, thisExperiment, soundInfo, visuals, routineTimer, time = 10000):
    endExperimentNow = False  # flag for 'escape' or other condition => quit the exp
    continueRoutine = True
    routineForceEnded = False

    sound = soundInfo[0]
    # update component parameters for each repeat
    #sound_2.setSound('C:/Users/yulia.sazonova/Desktop/oddball/oddball_task/white-noise44.wav', hamming=True)
    #sound_2.setVolume(1.0, log=False)
    # keep track of which components have finished
    trialComponents = [sound]
    
    for visual in visuals:
        trialComponents.append(visual[0])
    
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

    # --- Run Routine "trial2" ---
    while continueRoutine and routineTimer.getTime() < time:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = window.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = window.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        # start/stop sound
        if sound.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sound.frameNStart = frameN  # exact frame index
            sound.tStart = t  # local t and not account for scr refresh
            sound.tStartRefresh = tThisFlipGlobal  # on global time
            # add timestamp to datafile
            if soundInfo[1]:
                thisExperiment.addData(soundInfo[2] + '.started', tThisFlipGlobal)
            sound.play(when=window)  # sync with win flip
            
        # *visuals* updates
        for visualInfo in visuals:
            visual = visualInfo[0]
            if visual.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                visual.frameNStart = frameN  # exact frame index
                visual.tStart = t  # local t and not account for scr refresh
                visual.tStartRefresh = tThisFlipGlobal  # on global time
                window.timeOnFlip(visual, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                if (visualInfo[1]):
                    thisExperiment.timestampOnFlip(window, visualInfo[2] + '.started')
            visual.setAutoDraw(True)
            
            if visual.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > visual.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    visual.tStop = t  # not accounting for scr refresh
                    visual.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    if (visualInfo[1]):
                        thisExperiment.timestampOnFlip(window, visualInfo[2] + '.stopped')
                    visual.setAutoDraw(False)
                # check for quit (typically the Esc key)
                
        if endExperimentNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
    
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
    
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            window.flip()

    # --- Ending Routine "trial2" ---
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    sound.stop()  # ensure sound has stopped at end of routine
    # the Routine "trial2" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

# Main Scenario
if __name__ == "__main__": 
    thisDirectory = GetThisDirectory()
    print(thisDirectory)
    
    CreateSequence(Range(STANDARD_MIN_NUMBER, STANDARD_MAX_NUMBER), ODD_NUMBER, STIMULUS_SERIES_NUMBER)
    print("hiiii!")

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
    
    fixation = CreateFixationStimulus(window)
    startText = CreateTextStimulus(window, START_TEXT)
    

    size = MARK_SIZE
    bg_color = [1, 1, 1]
    photosensor = CreatePhotosensor(window)
    
    startInstructionFile = thisDirectory + '\\Start.wav'
    startInstructionsSound = sound.Sound(startInstructionFile, secs=-1, stereo=True, hamming=True, name='startInstructionsSound')
    startInstructionsSound.setVolume(1.0)
    startInstructionsSound.setSound(startInstructionFile, secs=-1, hamming=False)
    startInstructionsSound.setVolume(1.0, log=False)

    oddAudioFile = thisDirectory + '\\pink-noise.wav'
    standartAudioFile = thisDirectory + '\\white-noise.wav'

    standardSound = sound.Sound(standartAudioFile, secs=8, stereo=True, hamming=True,
        name='standardSound')
    standardSound.setVolume(8.0)
    standardSound.setSound(standartAudioFile, secs=-1, hamming=False)
    standardSound.setVolume(8.0, log=False)

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
    
    startSoundInfo = (startInstructionsSound, True, 'startInstruction')
    visualsInfo = [(startText, False, '')]
    RunTrial(window, thisExperiment, startSoundInfo, visualsInfo, routineTimer)
    
    standardSoundInfo = (standardSound, True, 'startInstruction')
    visualsInfo = [(fixation, False, '')]
    RunTrial(window, thisExperiment, standardSoundInfo, visualsInfo, routineTimer, 8)
    '''
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
            standardSound.play()
            #standardSound.stop()

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

    '''
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
