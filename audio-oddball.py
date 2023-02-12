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
from pylsl import StreamInfo, StreamOutlet
import random
import datetime

from collections import namedtuple
from enum import Enum
import csv 

import psychopy.iohub as io
from psychopy.hardware import keyboard

SCREEN_NUMBER = 1
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
EXPERIMENT_NAME = 'audio-oddball'
START_TEXT = 'Здравствуйте!\n\
Выполняйте задание клавиатурного тренажёра.\n\
Не обращайте внимания на сигналы.\nНажмите "Enter", чтобы начать'
STANDARD_EXAMPLE_TEXT = 'Это стандартный сигнал'
ODD_EXAMPLE_TEXT = 'Это отклоняющийся сигнал'
CONTINUE_TEXT = 'Нажмите "Enter", чтобы начать'
COUNT_TEXT = 'Теперь вам нужно посчитать количество отклоняющихся сигналов\n\
Продолжайте выполнять задание клавиатурного тренажёра.\n\
Нажмите "Enter", чтобы начать'
ENTER_COUNT_TEXT = 'Введите количество отклоняющихся сигналов:'

# Main
SHOW_TEST_BLOCK = True # Replace with False to turn off
SHOW_MAIN_BLOCK = True
NUMBER_OF_EXAMPLES = 3
EXAMPLES_PAUSE = 1000

# Number of standard
STANDARD_MIN_NUMBER = 3
STANDARD_MAX_NUMBER = 7
ODD_NUMBER = 1
STIMULUS_SERIES_NUMBER = 10 #30
CYCLES_NUMBER = 3 #4

# Times
ODD_TIME = 400
STANDARD_TIME = 400
STANDARD_TIME_MIN = 700
STANDARD_TIME_MAX = 900
PAUSE_TIME_MIN = 1000 #6000
PAUSE_TIME_MAX = 2000 #30000 #ms
CYCLE_PAUSE = 3000 #30000 #ms

# Marks
STANDARD_MARK = "Standard"
ODD_MARK = "Odd"

# LSL
STANDARD_START_LSL = 111
STANDARD_END_LSL = 112
ODD_START_LSL = 123
ODD_END_LSL = 124

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
_lslOutlet = None

_startInstructionsSound = None
_oddSound = None
_standardSound = None
_countIntructionsSound = None
_enterCountIntrustions = None
_oddAnnouncementIntrustions = None
_standardAnnouncementIntrustions = None

_fixation = None
_fixationInfo = None
_instructionsSoundInfo = None
_examplesSoundInfo = None
_stimulusSoundInfo = None
_examplePauseInfo = None
_cyclePauseInfo = None
_resultTextBox = None
_resultText = None

_terminated = False
 
class StimulusType(Enum):
    STANDARD = 0
    ODD = 1
    NONE = 2,
    PAUSE = 3

class TrialState(Enum):
    OK = 0,
    TERMINATED = 1,
    ERROR = 2

# Declaring namedtuple()
Range = namedtuple('Range', ['Min', 'Max'])
StimulusInfo = namedtuple('StimulusInfo', ['Type', 'Duration', 'Name', 'LSLStart', 'LSLEnd', 'WriteLog'], defaults=(StimulusType.NONE, None, None, -1, -1, False))

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

    while i < stimulusNumber:
        # Add Standard
        standardNumber = random.randint(standardRange.Min, standardRange.Max)
        standardTimes = [standardTime] * (standardNumber - standardRange.Min)

        for j in range(standardRange.Min):
            standardTimes.append(random.randint(standardTimeRange.Min, standardTimeRange.Max))
        random.shuffle(standardTimes)

        for j in range(standardNumber):
            sequence.append(StimulusInfo(StimulusType.STANDARD, MS_TO_S * standardTimes[j], STANDARD_MARK, STANDARD_START_LSL, STANDARD_END_LSL, True))
            i += 1
        
        for j in range(oddNumber):
            sequence.append(StimulusInfo(StimulusType.ODD, MS_TO_S * oddTime, ODD_MARK, ODD_START_LSL, ODD_END_LSL, True))
            i += 1

    return sequence[:stimulusNumber]

def CreatePauseSequence(stimulusNumber=30, timeRange=Range(700, 900)):
    sequence = []

    for i in range(stimulusNumber):
        sequence.append(StimulusInfo(StimulusType.PAUSE, MS_TO_S * random.randint(timeRange.Min, timeRange.Max), 'Pause', -1, True))

    return sequence

def GetThisDirectory():
    global _thisDirectory
    
    if not _thisDirectory:
        # Ensure that relative paths start from the same directory as this script
        _thisDirectory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(_thisDirectory)

    return _thisDirectory

def InitLslStream():
    global _lslOutlet

    lslInfo = StreamInfo(name='stream_name', type='Markers', channel_count=1,
                  channel_format='int32', source_id='uniqueid12345')
    # Initialize the stream.
    _lslOutlet = StreamOutlet(lslInfo)


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

def ShowCountDialog():
    text = 'Количество'
    dictionary = {
        text: ""
    }

    dialog = gui.DlgFromDict(dictionary=dictionary, sortKeys=False, title=ENTER_COUNT_TEXT, screen=-1)

    return dictionary[text]

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

def CreateInputTextbox(window):
    textbox = visual.TextBox2(
        window, 
        text='',
        font='Open Sans',
        pos=(0, 0),
        letterHeight=0.05,
        size=(None, None),
        borderWidth=2.0,
        color='white',
        colorSpace='rgb',
        opacity=None,
        bold=False,
        italic=False,
        lineSpacing=1.0,
        padding=0.0, 
        alignment='center', 
        anchor='center',
        fillColor=None,
        borderColor=None,
        flipHoriz=False, 
        flipVert=False, 
        languageStyle='LTR',
        editable=True,
        name='textbox',
        autoLog=True)
    
    return textbox
    
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

def RunTrial(texts, textStimulusInfo, sound, soundStimulusInfo, waitForInput=False):
    global _routineTimer
    global _terminated

    if (_terminated):
        return TrialState.TERMINATED
    continueRoutine = True
    routineForceEnded = False
    hasText = texts != None and textStimulusInfo != None
    hasSound = sound != None and soundStimulusInfo != None

    # keep track of which components have finished
    components = []
    time = 0

    if hasText:
        if type(texts) is not list:
            texts = [texts]

        time = textStimulusInfo.Duration
        
        for text in texts:
            components.append(text)
    if hasSound:
        components.append(sound)
        time = soundStimulusInfo.Duration

    for thisComponent in components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = _window.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine ---
    while continueRoutine and (time == -1 or _routineTimer.getTime() < time):
        # get current time
        t = _routineTimer.getTime()
        tThisFlip = _window.getFutureFlipTime(clock=_routineTimer)
        tThisFlipGlobal = _window.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text* updates
        if hasText:
            for text in texts:
                if text.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
                    # keep track of start time/frame for later
                    text.frameNStart = frameN  # exact frame index
                    text.tStart = t  # local t and not account for scr refresh
                    text.tStartRefresh = tThisFlipGlobal  # on global time
                    _window.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    if textStimulusInfo.WriteLog:
                        thisExperiment.timestampOnFlip(_window, textStimulusInfo.Name + '.started')
                    text.setAutoDraw(True)
                if text.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text.tStartRefresh + time - frameTolerance:
                        # keep track of stop time/frame for later
                        text.tStop = t  # not accounting for scr refresh
                        text.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        if textStimulusInfo.WriteLog:
                            thisExperiment.timestampOnFlip(_window, textStimulusInfo.Name + '.stopped')
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
                if soundStimulusInfo.LSLStart != -1:
                    _lslOutlet.push_sample(x=[soundStimulusInfo.LSLStart])
                sound.play(when=_window)  # sync with win flip
            if sound.status == STARTED and time != -1:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > sound.tStartRefresh + time - frameTolerance:
                    # keep track of stop time/frame for later
                    sound.tStop = t  # not accounting for scr refresh
                    sound.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    if soundStimulusInfo.WriteLog:
                        thisExperiment.timestampOnFlip(_window, soundStimulusInfo.Name +'.stopped')
                    if soundStimulusInfo.LSLEnd != -1:
                        _lslOutlet.push_sample(x=[soundStimulusInfo.LSLEnd])
                    sound.stop()
        
        # check for quit (typically the Esc key)
        keys = _defaultKeyboard.getKeys(keyList=["escape", "return"])
        if "escape" in keys:
            _terminated = True
            return TrialState.TERMINATED
            #core.quit()
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
            _window.flip()
    
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

    return TrialState.OK
   
def GetSound(localPath, name):
    fullPath = thisDirectory + localPath#'\\Start.wav''startInstructionsSound'
    soundStimulus = sound.Sound(fullPath, secs=-1, stereo=True, hamming=True, name=name)
    soundStimulus.setVolume(1.0)
    soundStimulus.setSound(fullPath, secs=-1, hamming=False)
    soundStimulus.setVolume(1.0, log=False)

    return soundStimulus

def InitializeSounds():
    global _startInstructionsSound
    global _countIntructionsSound
    global _enterCountIntrustions
    global _oddSound 
    global _standardSound
    global _oddAnnouncementIntrustions
    global _standardAnnouncementIntrustions

    _startInstructionsSound = GetSound('\\start-instructions.wav', 'startInstructionsSound')
    _countIntructionsSound = GetSound('\\continue-instructions.wav', 'continueInstructionsSound')
    _enterCountIntrustions = GetSound('\\enter-count-instructions.wav', 'enterCountInstructionsSound')
    _oddAnnouncementIntrustions = GetSound('\\odd-announcement.wav', 'oddAnnouncementSound')
    _standardAnnouncementIntrustions = GetSound('\\standard-announcement.wav', 'standardAnnouncementSound')
    _oddSound = GetSound('\\white-noise.wav', ODD_MARK)
    _standardSound = GetSound('\\pink-noise.wav', STANDARD_MARK)

def StoreCurrentExperimentInfo(experimentInfo):
    global _ioConfig
    global _ioServer
    global _ioSession
    global _routineTimer
    global _defaultKeyboard

   # store frame rate of monitor if we can measure it
    experimentInfo['frameRate'] = _window.getActualFrameRate()
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
    _ioServer = io.launchHubServer(window=_window, **_ioConfig)
    _eyetracker = None

    # create a default keyboard (e.g. to check for escape)
    _defaultKeyboard = keyboard.Keyboard(backend='iohub')

    # --- Initialize components for Routine "trial" ---

    # Create some handy timers
    _globalClock = core.Clock()  # to track the time since experiment started
    _routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine 
    
def GetSequences(cyclesNumber):
    stimuliSequence = []
    pauseSequence = []
    
    for i in range(cyclesNumber):
        stimuliSequence.append(CreateSequence(Range(STANDARD_MIN_NUMBER, STANDARD_MAX_NUMBER), ODD_NUMBER, STIMULUS_SERIES_NUMBER))
        pauseSequence.append(CreatePauseSequence(STIMULUS_SERIES_NUMBER, Range(PAUSE_TIME_MIN, PAUSE_TIME_MAX)))

    return stimuliSequence, pauseSequence

def InitialzeStimuli(window):
    global _fixation
    global _fixationInfo
    global _cyclePauseInfo
    global _resultTextBox
    global _resultText
    global _instructionsSoundInfo
    global _examplesSoundInfo
    global _stimulusSoundInfo
    global _examplePauseInfo

    _fixation = CreateFixationStimulus(window)
    _fixationInfo = StimulusInfo(
        Type = StimulusType.NONE, 
        Duration = -1,
        WriteLog = False)
    _examplePauseInfo = StimulusInfo(
        Type = StimulusType.NONE, 
        Duration = MS_TO_S * EXAMPLES_PAUSE,
        WriteLog = False)
    _fixation = CreateFixationStimulus(window)
    _instructionsSoundInfo = StimulusInfo(StimulusType.NONE, WriteLog=True, Name='startInstruction', Duration=1000000)
    _examplesSoundInfo = StimulusInfo(StimulusType.NONE, WriteLog=False, Name='examplesInstruction', Duration=-1)
    _stimulusSoundInfo = StimulusInfo(StimulusType.NONE, WriteLog=False, Name='stimulusExample', Duration=MS_TO_S * STANDARD_TIME)
    _cyclePauseInfo = StimulusInfo(
        Type = StimulusType.NONE, 
        Duration = MS_TO_S * CYCLE_PAUSE,
        Name = "Cycle pause",
        WriteLog = True)
    _resultTextBox = CreateInputTextbox(window)
    _resultText = CreateTextStimulus(window, ENTER_COUNT_TEXT)
    _resultText.pos = (0, 0.2)

def CheckState(trialState):
    return trialState != TrialState.TERMINATED and trialState != TrialState.ERROR

def MinimizeWindow():
    global _terminated
    
    if _terminated:
        return

    _window.winHandle.minimize() # minimise the PsychoPy window
    _window.flip() # redraw the (minimised) window

def MaximizeWindow():
    global _terminated
    
    if _terminated:
        return
    _window.winHandle.maximize()
    #_window.winHandle.set_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    _window.winHandle.activate()
    _window.flip()

def RunOddball(stimuli, pauses, test=True):
    global _resultTextBox
    global _resultText
    global _fixationInfo
    global _instructionsSoundInfo
    global _terminated

    results = []
    oddCount = 0
    type = "TEST" if test else "RUN"

    MinimizeWindow()

    for i in range(CYCLES_NUMBER):
        oddCount = 0

        # Cycle
        for j in range(STIMULUS_SERIES_NUMBER):
            stimulusInfo = stimuli[i][j]
            if not _terminated:
                print(f'{type}, Cycle #{i}, Trial #{j}, Type = {stimulusInfo.Type}, D1 = {stimulusInfo.Duration}, Pause Duration = {pauses[i][j].Duration}')
            if stimulusInfo.Type == StimulusType.STANDARD:
                sound = _standardSound
            else:
                sound = _oddSound
                oddCount += 1
            RunTrial(_fixation, pauses[i][j], None, None)
            RunTrial(_fixation, _fixationInfo, sound, stimulusInfo)

        # Pause between cycles
        if not test:
            MaximizeWindow()
            state = RunTrial([_resultTextBox, _resultText], _fixationInfo, _enterCountIntrustions, _instructionsSoundInfo, True)
            userInput = _resultTextBox.text.strip() if CheckState(state) else '-'
            results.append((oddCount, userInput))
            _resultTextBox.text = ''
            MinimizeWindow()
        
        RunTrial(_fixation, _cyclePauseInfo, None, None)
    
    MaximizeWindow()

    return results

def PrintResultsToCsv(results, filename):
    file = open(filename+ '.csv','w')
    writer = csv.writer(file, delimiter=';')
    writer.writerows([c[0], ','.join(c[1:])] for c in results)
    file.close()

def RunExamples(mainText, mainTextInfo):
    global _examplesSoundInfo
    global _examplePauseInfo
    global _standardAnnouncementIntrustions
    global _oddAnnouncementIntrustions
    global _fixationInfo
    global _standardSound
    global _oddSound
    global _stimulusSoundInfo
    global continueText

    # Standard and odd examples
    soundInfo = _examplesSoundInfo._replace(Duration = _standardAnnouncementIntrustions.getDuration())
    RunTrial(_fixation, instructionsTextInfo, _standardAnnouncementIntrustions, soundInfo, True)
    for i in range(NUMBER_OF_EXAMPLES):
        RunTrial(standardExampleText, _examplePauseInfo, None, None)
        RunTrial(standardExampleText, _fixationInfo, _standardSound, _stimulusSoundInfo)

    soundInfo = _examplesSoundInfo._replace(Duration = _oddAnnouncementIntrustions.getDuration())
    RunTrial(_fixation, instructionsTextInfo, _oddAnnouncementIntrustions, soundInfo)
    for i in range(NUMBER_OF_EXAMPLES):
        RunTrial(oddExampleText, _examplePauseInfo, None, None)
        RunTrial(oddExampleText, _fixationInfo, _oddSound, _stimulusSoundInfo)


# Main Scenario
if __name__ == "__main__": 
    thisDirectory = GetThisDirectory()
    print(thisDirectory)
    
    testStimuliSequences, testPauseSequence = GetSequences(CYCLES_NUMBER)

    # genarate permutation
    trainStimuliSequences = testStimuliSequences.copy()
    random.shuffle(trainStimuliSequences)
    trainPauseSequence = testPauseSequence.copy()
    random.shuffle(trainPauseSequence)

    experimentName = EXPERIMENT_NAME
    psychopyVersion = '2022.2.4'
    experimentInfo = InitSessionInfo(experimentName)
    InitLslStream()

    dataFilename = ShowStartDialog(experimentInfo, experimentName, psychopyVersion)

    # An ExperimentHandler isn't essential but helps with data saving
    thisExperiment = GetExperimentHandler(experimentInfo, experimentName, dataFilename)
    frameTolerance = 0.001  # how close to onset before 'same' frame

    # Start Code - component code to be run after the window creation

    # --- Setup the Window ---
    _window = visual.Window(
        size=SCREEN_SIZE, 
        fullscr=True, 
        screen=SCREEN_NUMBER, 
        winType='pyglet',
        allowStencil=False,
        monitor='testMonitor',
        color=BACKGROUND_COLOR,
        blendMode='avg', 
        useFBO=True, 
        units='height')
    _window.mouseVisible = False
    StoreCurrentExperimentInfo(experimentInfo)
    
    startText = CreateTextStimulus(_window, START_TEXT)
    countText = CreateTextStimulus(_window, COUNT_TEXT)
    standardExampleText = CreateTextStimulus(_window, STANDARD_EXAMPLE_TEXT)
    oddExampleText = CreateTextStimulus(_window, ODD_EXAMPLE_TEXT)
    continueText = CreateTextStimulus(_window, CONTINUE_TEXT)
    instructionsTextInfo = StimulusInfo(StimulusType.NONE, 100000, WriteLog=False)
    photosensor = CreatePhotosensor(_window)
    InitialzeStimuli(_window)
    InitializeSounds()

    if (SHOW_TEST_BLOCK and not _terminated):
        # Show start instuctions
        RunTrial(startText, instructionsTextInfo, _startInstructionsSound, _instructionsSoundInfo, True)

        # Run Test
        RunOddball(testStimuliSequences, testPauseSequence)

    if (SHOW_MAIN_BLOCK and not _terminated):
        #RunTrial(continueText, instructionsTextInfo, None, None, True)
        RunExamples(countText, instructionsTextInfo)
        # Show count instuctions
        RunTrial(countText, instructionsTextInfo, _countIntructionsSound, _instructionsSoundInfo, True)

        # Run Train
        results = RunOddball(trainStimuliSequences, trainPauseSequence, False)
        results.insert(0, ("odd_count", "user_input"))

    print(results)

    resultsFilename = _thisDirectory + os.sep + u'data/results_%s_%s_%s' % (experimentInfo['Participant'], experimentName, experimentInfo['date'])
    PrintResultsToCsv(results, resultsFilename)

    # these shouldn't be strictly necessary (should auto-save)
    thisExperiment.saveAsWideText(dataFilename+'.csv', delim='auto')
    thisExperiment.saveAsPickle(dataFilename)
    logging.flush()
    # make sure everything is closed down
    if _eyetracker:
        _eyetracker.setConnectionState(False)
    thisExperiment.abort()  # or data files will save again on exit
    _window.close()
    core.quit()
