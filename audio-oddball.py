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
START_TEXT = 'Здравствуйте!\n\
Выполняйте задание клавиатурного тренажёра.\
Не обращайте внимания на сигналы. Нажмите "Enter", чтобы начать'

# Number of standard
STANDARD_MIN_NUMBER = 3
STANDARD_MAX_NUMBER = 7
ODD_NUMBER = 1
CYCLES_NUMBER = 3
STIMULUS_SERIES_NUMBER = 10 #30

# Times
ODD_TIME = 400
STANDARD_TIME = 400
STANDARD_TIME_MIN = 700
STANDARD_TIME_MAX = 900
PAUSE_TIME_MIN = 1000 #6000 ms
PAUSE_TIME_MAX = 3000 #30000 ms

# Marks
STANDARD_MARK = "Standard"
ODD_MARK = "Odd"

# LSL
STANDARD_LSL = 111
ODD_LSL = 123

# Colors
BACKGROUND_COLOR = 'Black'
FIXATION_COLOR = 'White'

# Right bottom mark size for photosensor (set it to 0 to hide)
FIXATION_SIZE = 20
MARK_SIZE = 20

# Use default
WINDOW = None

MS_TO_S = 0.001

# Globals
_thisDirectory = ''
_globalClock = None
_defaultKeyboard = None
_routineTimer = None
_ioSession = None
_ioServer = None
_eyetracker = None
_ioConfig = None

_startInstructionSound = None
_oddSound = None
_standardSound = None
 
class StimulusType(Enum):
    STANDARD = 0
    ODD = 1
    NONE = 2,
    PAUSE = 3

# Declaring namedtuple()
Range = namedtuple('Range', ['Min', 'Max'])
StimulusInfo = namedtuple('StimulusInfo', ['Type', 'Duration', 'Name', 'LSL', 'WriteLog'], defaults=(None,) * 5)

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
            standardTimes.append(random.randint(standardTimeRange.Min, standardTimeRange.Max))
        random.shuffle(standardTimes)

        for j in range(standardNumber):
            sequence.append(StimulusInfo(StimulusType.STANDARD, MS_TO_S * standardTimes[j], STANDARD_MARK, STANDARD_LSL, True))
            i += 1
        
        for j in range(oddNumber):
            sequence.append(StimulusInfo(StimulusType.ODD, MS_TO_S * oddTime, ODD_MARK, ODD_LSL, True))
            i += 1

    for i in range(stimulusNumber):
        print(f'({sequence[i]})')

    return sequence[:stimulusNumber]

def CreatePauseSequence(stimulusNumber=30, timeRange=Range(700, 900)):
    sequence = []

    for i in range(stimulusNumber):
        sequence.append(StimulusInfo(StimulusType.PAUSE, MS_TO_S * random.randint(timeRange.Min, timeRange.Max), 'Pause', -1, True))

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
        text = text,
        font='Open Sans', 
        height=0.05, 
        color='White',
        languageStyle='LTR',
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

def RunCustomTrial(text, textStimulusInfo, sound, soundStimulusInfo, waitForInput=False):
    global _routineTimer

    continueRoutine = True
    routineForceEnded = False
    hasText = text != None and textStimulusInfo != None
    hasSound = sound != None and soundStimulusInfo != None

    # keep track of which components have finished
    components = []
    time = 0
    if hasText:
        components.append(text)
        time = textStimulusInfo.Duration
    if hasSound:
        components.append(sound)
        time = soundStimulusInfo.Duration

    print(f'hasSound = {hasSound}, hasText = {hasText}, time = {time}')
    for thisComponent in components:
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
    
    # --- Run Routine ---
    while continueRoutine and _routineTimer.getTime() < time:
        # get current time
        t = _routineTimer.getTime()
        tThisFlip = window.getFutureFlipTime(clock=_routineTimer)
        tThisFlipGlobal = window.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text* updates
        if hasText:
            if text.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
                # keep track of start time/frame for later
                text.frameNStart = frameN  # exact frame index
                text.tStart = t  # local t and not account for scr refresh
                text.tStartRefresh = tThisFlipGlobal  # on global time
                window.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                if textStimulusInfo.WriteLog:
                    thisExperiment.timestampOnFlip(window, textStimulusInfo.Name + '.started')
                text.setAutoDraw(True)
            if text.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text.tStartRefresh + time - frameTolerance:
                    # keep track of stop time/frame for later
                    text.tStop = t  # not accounting for scr refresh
                    text.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    if textStimulusInfo.WriteLog:
                        thisExperiment.timestampOnFlip(window, textStimulusInfo.Name + '.stopped')
                    text.setAutoDraw(False)
        
        if hasSound:
            # start/stop sound
            if sound.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                sound.frameNStart = frameN  # exact frame index
                sound.tStart = t  # local t and not account for scr refresh
                sound.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                if soundStimulusInfo.WriteLog:
                    thisExperiment.addData(soundStimulusInfo.Name +'.started', tThisFlipGlobal)
                sound.play(when=window)  # sync with win flip
            if sound.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > sound.tStartRefresh + time - frameTolerance:
                    # keep track of stop time/frame for later
                    sound.tStop = t  # not accounting for scr refresh
                    sound.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    if soundStimulusInfo.WriteLog:
                        thisExperiment.timestampOnFlip(window, soundStimulusInfo.Name +'.stopped')
                    sound.stop()
        
        # check for quit (typically the Esc key)
        keys = _defaultKeyboard.getKeys(keyList=["escape", "return"])
        if "escape" in keys:
            core.quit()
        if waitForInput and "return" in keys:
            time = 0
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            window.flip()
    
    # --- Ending Routine "StandardStimulus" ---
    for thisComponent in components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    if hasSound:
        sound.stop()  # ensure sound has stopped at end of routine

    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        _routineTimer.reset()
    else:
        _routineTimer.addTime(-time)
   
def GetSound(localPath, name):
    fullPath = thisDirectory + localPath#'\\Start.wav''startInstructionsSound'
    soundStimulus = sound.Sound(fullPath, secs=-1, stereo=True, hamming=True, name=name)
    soundStimulus.setVolume(1.0)
    soundStimulus.setSound(fullPath, secs=-1, hamming=False)
    soundStimulus.setVolume(1.0, log=False)

    return soundStimulus

def InitializeSounds():
    global _startInstructionsSound
    global _oddSound 
    global _standardSound

    _startInstructionsSound = GetSound('\\Start.wav', 'startInstructionsSound')
    _oddSound = GetSound('\\pink-noise.wav', ODD_MARK)
    _standardSound = GetSound('\\white-noise.wav', STANDARD_MARK)

def StoreCurrentExperimentInfo(experimentInfo):
    global _ioConfig
    global _ioServer
    global _ioSession
    global _routineTimer
    global _defaultKeyboard

   # store frame rate of monitor if we can measure it
    experimentInfo['frameRate'] = window.getActualFrameRate()
    if experimentInfo['frameRate'] != None:
        frameDur = 1.0 / round(experimentInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    # --- Setup input devices ---
    _ioConfig = {}

    # Setup iohub keyboard
    _ioConfig['Keyboard'] = dict(use_keymap='psychopy')

    _ioSession = '1'
    if 'session' in experimentInfo:
        _ioSession = str(experimentInfo['session'])
    _ioServer = io.launchHubServer(window=window, **_ioConfig)
    _eyetracker = None

    # create a default keyboard (e.g. to check for escape)
    _defaultKeyboard = keyboard.Keyboard(backend='iohub')

    # --- Initialize components for Routine "trial" ---

    # Create some handy timers
    _globalClock = core.Clock()  # to track the time since experiment started
    _routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine 
    

# Main Scenario
if __name__ == "__main__": 
    thisDirectory = GetThisDirectory()
    print(thisDirectory)
    
    stimuliInfo = CreateSequence(Range(STANDARD_MIN_NUMBER, STANDARD_MAX_NUMBER), ODD_NUMBER, STIMULUS_SERIES_NUMBER)
    pauseInfo = CreatePauseSequence(STIMULUS_SERIES_NUMBER, Range(PAUSE_TIME_MIN, PAUSE_TIME_MAX))

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
    startInstructionsSoundInfo = StimulusInfo(StimulusType.NONE, WriteLog=True, Name='startInstruction', Duration=1000000)
    photosensor = CreatePhotosensor(window)
    
    InitializeSounds()
    StoreCurrentExperimentInfo(experimentInfo)
    RunCustomTrial(startText, StimulusInfo(StimulusType.NONE, WriteLog=False), _startInstructionsSound, startInstructionsSoundInfo, True)

    fixationInfo = StimulusInfo(
        Type = StimulusType.NONE, 
        Duration = -1,
        WriteLog = False)

    for i in range(STIMULUS_SERIES_NUMBER):
        stimulusInfo = stimuliInfo[i]
        sound = _standardSound if stimulusInfo.Type == StimulusType.STANDARD else _oddSound
        RunCustomTrial(fixation, fixationInfo, sound, stimuliInfo[i])
        RunCustomTrial(fixation, pauseInfo[i], None, None)

    # these shouldn't be strictly necessary (should auto-save)
    thisExperiment.saveAsWideText(dataFilename+'.csv', delim='auto')
    thisExperiment.saveAsPickle(dataFilename)
    logging.flush()
    # make sure everything is closed down
    if _eyetracker:
        _eyetracker.setConnectionState(False)
    thisExperiment.abort()  # or data files will save again on exit
    window.close()
    core.quit()
