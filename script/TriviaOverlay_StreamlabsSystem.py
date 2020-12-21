# -*- coding: utf-8 -*-
# ---------------------------------------
#   Import Libraries
# ---------------------------------------
import sys
import clr
import json
import codecs
import os
import re
import random
from random import randrange
from random import seed
import datetime
import glob
import time
import threading
import shutil
import tempfile
from HTMLParser import HTMLParser
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")


# ---------------------------------------
#   [Required] Script Information
# ---------------------------------------
ScriptName = "Trivia Overlay"
Website = "http://darthminos.tv"
Description = "Trivia Overlay and Chat Interaction"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"
Repo = "camalot/chatbot-trivia"
ReadMeFile = "https://github.com/" + Repo + "/blob/develop/ReadMe.md"

UIConfigFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")
SettingsFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")
ScriptSettings = None
Initialized = False
CurrentQuestion = None
CurrentAnswers = list([])
CurrentQuestionEndTickTime = None
CorrectIndex = -1
KnownBots = None
AnsweredCorrect = False
CorrectlyAnswered = list([])
RunningThread = None
Logger = None
LastTickTime = None


API_URL = "https://opentdb.com/api.php?amount=1&category={0}&difficulty={1}&type={2}"
POSSIBLE_ANSWERS = [ "a", "b", "c", "d" ]
DIFFICULTIES = [
    {"id": "", "name": "Any"},
    {"id": "easy", "name": "Easy"},
    {"id": "medium", "name": "Medium"},
    {"id": "hard", "name": "Hard"}
]
TYPES = [
    {"id": "", "name": "Any"},
    {"id": "multiple", "name": "Multiple Choice"},
    {"id": "boolean", "name": "True / False"}
]
CATEGORIES = [
    {"id": "", "name": "Any"},
    {"id": "9", "name": "General Knowledge"},
    {"id": "10", "name": "Entertainment: Books"},
    {"id": "11", "name": "Entertainment: Film"},
    {"id": "12", "name": "Entertainment: Music"},
    {"id": "13", "name": "Entertainment: Musicals & Theatres"},
    {"id": "14", "name": "Entertainment: Television"},
    {"id": "15", "name": "Entertainment: Video Games"},
    {"id": "16", "name": "Entertainment: Board Games"},
    {"id": "17", "name": "Science & Nature"},
    {"id": "18", "name": "Science: Computers"},
    {"id": "19", "name": "Science: Mathematics"},
    {"id": "20", "name": "Mythology"},
    {"id": "21", "name": "Sports"},
    {"id": "22", "name": "Geography"},
    {"id": "23", "name": "History"},
    {"id": "24", "name": "Politics"},
    {"id": "25", "name": "Art"},
    {"id": "26", "name": "Celebrities"},
    {"id": "27", "name": "Animals"},
    {"id": "28", "name": "Vehicles"},
    {"id": "29", "name": "Entertainment: Comics"},
    {"id": "30", "name": "Science: Gadgets"},
    {"id": "31", "name": "Entertainment: Japanese Anime & Manga"},
    {"id": "32", "name": "Entertainment: Cartoon & Animations"}
]


class TriviaQuestion(object):
    def __init__(self, jsonData):
        try:
            self.category = "Unknown"
            self.type = "none"
            self.difficulty = "none"
            self.question = ""
            self.correct_answer = ""
            self.correct_index = -1
            self.incorrect_answers = list([])
            resp = json.loads(jsonData, encoding="utf-8")
            if resp['response_code'] == 0 and len(resp['results']) > 0:
                seed()
                result = resp['results'][0]
                self.__dict__.update(result)
                numberOfAnswers = len(self.incorrect_answers)
                Logger.debug("LEN: " + str(numberOfAnswers))
                self.answers = self.incorrect_answers[:]

                # Shouldn't shift if question type is boolean. it should be [true,false]
                if self.type == "boolean":
                    if self.correct_answer == "True":
                        position = 0
                    else:
                        position = 1
                else:
                    position = randrange(numberOfAnswers + 1)
                self.correct_index = position
                Logger.debug("Correct: " + str(self.correct_index))
                Logger.debug("Correct: " + str(self.correct_answer))
                Logger.debug("answers: " + json.dumps(self.answers))
                self.answers.insert(position, self.correct_answer)
                self.points = GetPointsForDifficulty(self.difficulty)
                Logger.debug("answers: " + json.dumps(self.answers))
            else:
                raise Exception("Unable to load trivia question.")
        except Exception as e:
            raise e
            Logger.error(str(e))


class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        defaults = self.DefaultSettings(UIConfigFile)
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                settings = json.load(f, encoding="utf-8")
            self.__dict__ = Merge(defaults, settings)
        except Exception as ex:
            if Logger:
                Logger.error(str(ex))
            else:
                Parent.Log(ScriptName, str(ex))
            self.__dict__ = defaults

    def DefaultSettings(self, settingsfile=None):
        defaults = dict()
        with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
        for key in ui:
            if 'value' in ui[key]:
                try:
                    defaults[key] = ui[key]['value']
                except:
                    if key != "output_file":
                        if Logger:
                            Logger.warn("DefaultSettings(): Could not find key {0} in settings".format(key))
                        else:
                            Parent.Log(ScriptName, "DefaultSettings(): Could not find key {0} in settings".format(key))
        return defaults
    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        if Logger:
            Logger.debug("Reload Settings")
        else:
            Parent.Log(ScriptName, "Reload Settings")
        self.__dict__ = Merge(self.DefaultSettings(UIConfigFile), json.loads(jsonData, encoding="utf-8"))


class StreamlabsLogHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            message = self.format(record)
            Parent.Log(ScriptName, message)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def GetLogger():
    log = logging.getLogger(ScriptName)
    log.setLevel(logging.DEBUG)

    sl = StreamlabsLogHandler()
    sl.setFormatter(logging.Formatter("%(funcName)s(): %(message)s"))
    sl.setLevel(logging.INFO)
    log.addHandler(sl)

    fl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(
        __file__), "info"), when="w0", backupCount=8, encoding="utf-8")
    fl.suffix = "%Y%m%d"
    fl.setFormatter(logging.Formatter(
        "%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
    fl.setLevel(logging.INFO)
    log.addHandler(fl)

    if ScriptSettings.DebugMode:
        dfl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(
            __file__), "debug"), when="h", backupCount=24, encoding="utf-8")
        dfl.suffix = "%Y%m%d%H%M%S"
        dfl.setFormatter(logging.Formatter(
            "%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
        dfl.setLevel(logging.DEBUG)
        log.addHandler(dfl)

    log.debug("Logger initialized")
    return log

def Init():
    global Initialized
    global ScriptSettings
    global KnownBots
    global Logger
    global LastTickTime

    if Initialized:
        Parent.Log(ScriptName, "Skip Initialization. Already Initialized.")
        return

    LastTickTime = time.time()
    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    Logger = GetLogger()    

    if KnownBots is None:
        try:
            botData = json.loads(json.loads(Parent.GetRequest(
                "https://api.twitchinsights.net/v1/bots/online", {}))['response'])['bots']
            KnownBots = [bot[0].lower() for bot in botData]
        except:
            Logger.error(str(e))
            KnownBots = []

    SendQuestionEvent()
    SendSettingsEvent()

    Initialized = True
    return


def Unload():
    global Initialized
    Initialized = False
    return


def Execute(data):
    global AnsweredCorrect
    # if ScriptSettings.OnlyWhenLive and not Parent.IsLive():
    #     return
    if data.IsChatMessage():
        commandTrigger = data.GetParam(0).lower()

        # handle letter commands
        commands = [ "!a", "!b", "!c", "!d" ]
        if CurrentQuestion and commandTrigger.lower() in commands:
            commandParam = commandTrigger[1:].lower()
            commandTrigger = ScriptSettings.AnswerCommand
            Logger.debug("commandTrigger: {0}".format(commandTrigger))
            Logger.debug("commandParam: {0}".format(commandParam))

        if CurrentQuestion and commandTrigger.lower() in POSSIBLE_ANSWERS:
            commandParam = commandTrigger.lower()
            commandTrigger = ScriptSettings.AnswerCommand
            Logger.debug("commandTrigger: {0}".format(commandTrigger))
            Logger.debug("commandParam: {0}".format(commandParam))

        if commandTrigger == ScriptSettings.Command:
            if data.GetParamCount() > 1:
                # SUB COMMANDS
                subCommand = data.GetParam(1).lower()
                if Parent.HasPermission(data.User, "Moderator", ""):
                    if subCommand == "clear":
                        Parent.SendTwitchMessage(Parse(ScriptSettings.ClearResponse, data.User, data.UserName, "", data.Message))
                        ClearCurrentQuestion()
                    if subCommand == "close":
                        Parent.SendTwitchMessage(Parse(ScriptSettings.ClearResponse, data.User, data.UserName, "", data.Message))
                        CloseQuestion()
                else:
                    return
            else:
                if Parent.HasPermission(data.User, ScriptSettings.TriviaPermission, ""):
                    TriggerQuestionFromUser(data.User, data.UserName)
        elif CurrentQuestion is not None and commandTrigger == ScriptSettings.AnswerCommand:
            # check if user has permission to answer
            if not Parent.HasPermission(data.User, ScriptSettings.AnswerPermission, ""):
                return
            # check if they already answered
            if data.User in CurrentAnswers:
                # ignore since they already answered.
                Parent.SendTwitchMessage(Parse(ScriptSettings.AlreadyAnsweredResponse, data.User, data.UserName, "", data.Message))
                return
            # Someone is answering a trivia question.
            if commandParam or data.GetParamCount() > 1:
                answer = commandParam or data.GetParam(1).lower()
                Logger.debug("{0} guessed {1}".format(data.User, answer))
                selected_answer = None
                if answer in POSSIBLE_ANSWERS:
                    answer_index = POSSIBLE_ANSWERS.index(answer)
                    if answer_index >= 0:
                        selected_answer = CurrentQuestion.answers[answer_index]
                        CurrentAnswers.append(data.User)
                        Logger.debug(json.dumps(CurrentAnswers))
                        if CurrentQuestion.correct_index == answer_index:
                            AnsweredCorrect = True
                            # Apply Points
                            Parent.AddPoints(data.User, data.UserName, CurrentQuestion.points)
                            # Tell Chat
                            Parent.SendTwitchMessage(Parse(ScriptSettings.CorrectResponse, data.User, data.UserName, "", data.Message))
                            CorrectlyAnswered.append(data.UserName)
                            SendQuestionAnsweredEvent(data.UserName)
                            ClearCurrentQuestion()
                            # SendQuestionClearEvent()
                        else:
                            Parent.SendTwitchMessage(Parse(ScriptSettings.IncorrectResponse, data.User, data.UserName, "", data.Message))
                else:
                    Parent.SendTwitchMessage(Parse(ScriptSettings.UnknownAnswerResponse, data.User, data.UserName, "", data.Message))
                    return
            else:
                return

def Tick():
    global LastTickTime
    global CurrentQuestionEndTickTime
    if ScriptSettings.EnableAutoTrivia:
        if LastTickTime is None:
            # if last tick time was not ever set, lets make sure it was set.
            LastTickTime = time.time()
        intervalSeconds = ScriptSettings.AutoTriviaInterval * 60
        if time.time() - LastTickTime >= intervalSeconds:
            Logger.debug("Start Auto Question")
            TriggerQuestion()
            LastTickTime = time.time()
    if CurrentQuestionEndTickTime and time.time() >= CurrentQuestionEndTickTime:
        #threading.Thread(target=QuestionTimeoutThread, args=(ScriptSettings.TimeToAnswer, ScriptSettings.TimeoutResponse)).start()
        QuestionTimeout()

def ScriptToggled(state):
    Logger.debug("State Changed: " + str(state))
    if state:
        Init()
    else:
        Unload()
    return


def ReloadSettings(jsondata):
    Logger.debug("Reload Settings")
    # Reload saved settings and validate values
    Unload()
    Init()
    return


def Parse(parseString, userid, username, target, message):
    resultString = parseString
    resultString = resultString.replace("$username", username)
    resultString = resultString.replace("$userid", userid)
    resultString = resultString.replace(
        "$currencyname", Parent.GetCurrencyName())
    resultString = resultString.replace(
        "$points", str(int(Parent.GetPoints(target))))

    resultString = resultString.replace("$triviapoints", str(
        GetPointsForDifficulty(CurrentQuestion.difficulty)))

    resultString = resultString.replace(
        "$triviaanswercommand", ScriptSettings.AnswerCommand)
    resultString = resultString.replace(
        "$triviacommand", ScriptSettings.Command)

    resultString = resultString.replace(
        "$triviacategory", CurrentQuestion.category or "NONE")
    resultString = resultString.replace(
        "$triviaquestion", unescapeHtml(CurrentQuestion.question) or "NONE")
    resultString = resultString.replace(
        "$triviadifficulty", CurrentQuestion.difficulty or "NONE")
    resultString = resultString.replace(
        "$triviaanswers", GetChatFormattedAnswers(CurrentQuestion.answers) or "NONE")

    resultString = resultString.replace(
        "$triviacorrectindex", str(CurrentQuestion.correct_index or "NONE"))
    resultString = resultString.replace(
        "$triviacorrect", unescapeHtml(CurrentQuestion.correct_answer or "NONE"))

    resultString = resultString.replace('\\n', '\n')

    return resultString


def IsTwitchBot(user):
    return user.lower() in KnownBots


def str2bool(v):
    if not v:
        return False
    return stripQuotes(v).strip().lower() in ("yes", "true", "1", "t", "y")


def stripQuotes(v):
    r = re.compile(r"^[\"\'](.*)[\"\']$", re.U)
    m = r.search(v)
    if m:
        return m.group(1)
    return v

def unescapeHtml(s):
    h = HTMLParser()
    return h.unescape(s.strip())

def QuestionTimeout():
    global AnsweredCorrect
    global CurrentQuestion
    global CurrentQuestionEndTickTime
    if CurrentQuestion and not AnsweredCorrect:
        Logger.debug("Sending Timeout")
        SendQuestionTimeoutEvent()
        if ScriptSettings.TimeoutResponse:
            Parent.SendTwitchMessage(ScriptSettings.TimeoutResponse.replace("$triviacorrect", unescapeHtml(CurrentQuestion.correct_answer)))
        Logger.debug("Clear Current Question")
        ClearCurrentQuestion()
        CurrentQuestionEndTickTime = None
    return

def GetItemIdFromName(lst, name):
    iid = [item['id'] for item in lst if item['name'] == name]
    return iid[0] if not None else "any"

def GetPointsForDifficulty(difficulty):
    if difficulty == "hard":
        return ScriptSettings.PointsHard
    elif difficulty == "medium":
        return ScriptSettings.PointsMedium
    elif difficulty == "easy":
        return ScriptSettings.PointsEasy
    else:
        return 0

def GetChatFormattedAnswers(answers):
    fmt = ""
    for x in range(0, len(answers)):
        fmt += "{0}) {1} :: ".format(str(POSSIBLE_ANSWERS[x]), unescapeHtml(answers[x]))
    return fmt


def ClearCurrentQuestion():
    global CurrentQuestion
    global CurrentAnswers
    global LastTickTime
    global CorrectlyAnswered
    global AnsweredCorrect
    AnsweredCorrect = False
    CorrectlyAnswered = list([])
    CurrentAnswers = None
    CurrentQuestion = None
    LastTickTime = time.time()

def GetApiUrl():
    cat = GetItemIdFromName(CATEGORIES, ScriptSettings.QuestionCategory)
    dif = GetItemIdFromName(DIFFICULTIES, ScriptSettings.QuestionDifficulty)
    tpe = GetItemIdFromName(TYPES, ScriptSettings.QuestionType)

    url = API_URL.format(cat, dif, tpe)
    Logger.debug(url)
    return url

def GetNewQuestion():
    global CurrentQuestion
    global CurrentAnswers
    global AnsweredCorrect
    global LastTickTime
    global CorrectlyAnswered
    try:
        CorrectlyAnswered = list([])
        AnsweredCorrect = False
        resp = json.loads(Parent.GetRequest(GetApiUrl(), {}))['response']
        CurrentQuestion = TriviaQuestion(resp)
        CurrentAnswers = list([])
        LastTickTime = time.time()
    except Exception as e:
        CurrentQuestion = None
        CurrentAnswers = list([])
        AnsweredCorrect = False
        CorrectlyAnswered = list([])
        Logger.error(str(e))

def SendSettingsEvent():
    Parent.BroadcastWsEvent("EVENT_TRIVIA_SETTINGS", json.dumps(ScriptSettings.__dict__))


def SendQuestionEvent():
    global CurrentQuestion
    if CurrentQuestion is not None:
        Parent.BroadcastWsEvent("EVENT_TRIVIA_QUESTION", json.dumps(CurrentQuestion.__dict__))
    else:
        Parent.BroadcastWsEvent("EVENT_TRIVIA_QUESTION", json.dumps(None))

def SendQuestionTimeoutEvent():
    global CurrentQuestion
    if CurrentQuestion is not None:
        Parent.BroadcastWsEvent("EVENT_TRIVIA_TIMEOUT", json.dumps({
            "answer": CurrentQuestion.correct_answer,
            "answer_index": CurrentQuestion.correct_index
        }))

def SendQuestionClearEvent():
    Parent.BroadcastWsEvent("EVENT_TRIVIA_CLEAR", json.dumps(None))


def SendQuestionAnsweredEvent(user):
    if CurrentQuestion is not None:
        Parent.BroadcastWsEvent("EVENT_TRIVIA_ANSWERED", json.dumps({
            "user": user,
            "users": CorrectlyAnswered,
            "answer": CurrentQuestion.correct_answer,
            "answer_index": CurrentQuestion.correct_index
        }))

def TriggerQuestionFromUser(userid, username):
    global CurrentQuestionEndTickTime
    if not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command):
        if CurrentQuestion is None:
            GetNewQuestion()
            # Should I send this if there is an Active Question?
            SendQuestionEvent()
            Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)
            if ScriptSettings.TimeToAnswer > 0:
                CurrentQuestionEndTickTime = time.time() + ScriptSettings.TimeToAnswer
        Parent.SendTwitchMessage(Parse(ScriptSettings.QuestionResponse, userid, username, "", ""))


def TriggerQuestion():
    TriggerQuestionFromUser(Parent.GetChannelName().lower(), Parent.GetChannelName())

def ClearQuestion():
    Parent.SendTwitchMessage(Parse(ScriptSettings.ClearResponse, Parent.GetChannelName().lower(), Parent.GetChannelName(), "", ""))
    ClearCurrentQuestion()
    SendQuestionClearEvent()
    
def CloseQuestion():
    SendQuestionTimeoutEvent()
    ClearCurrentQuestion()
    if ScriptSettings.TimeoutResponse:
        Parent.SendTwitchMessage(ScriptSettings.TimeoutResponse.replace("$triviacorrect", unescapeHtml(CurrentQuestion.correct_answer)))

def OpenScriptUpdater():
    currentDir = os.path.realpath(os.path.dirname(__file__))
    chatbotRoot = os.path.realpath(os.path.join(currentDir, "../../../"))
    libsDir = os.path.join(currentDir, "libs/updater")
    Logger.debug(libsDir)
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Logger.debug(tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Logger.debug("Copy: " + full_file_name)
                shutil.copy(full_file_name, tempdir)
        updater = os.path.join(tempdir, "ApplicationUpdater.exe")
        updaterConfigFile = os.path.join(tempdir, "update.manifest")
        repoVals = Repo.split('/')
        updaterConfig = {
            "path": os.path.realpath(os.path.join(currentDir, "../")),
            "version": Version,
            "name": ScriptName,
            "requiresRestart": True,
            "kill": [],
            "execute": {
                "before": [{
                    "command": "cmd",
                    "arguments": [ "/c", "del /q /f /s *" ],
                    "workingDirectory": "${PATH}\\${FOLDERNAME}\\Libs\\updater\\",
                    "ignoreExitCode": True,
                    "validExitCodes": [ 0 ]
                }],
                "after": []
            },
            "application": os.path.join(chatbotRoot, "Streamlabs Chatbot.exe"),
            "folderName": os.path.basename(os.path.dirname(os.path.realpath(__file__))),
            "processName": "Streamlabs Chatbot",
            "website": Website,
            "repository": {
                "owner": repoVals[0],
                "name": repoVals[1]
            }
        }
        Logger.debug(updater)
        configJson = json.dumps(updaterConfig)
        Logger.debug(configJson)
        with open(updaterConfigFile, "w+") as f:
            f.write(configJson)
        os.startfile(updater)
        return
    except OSError as exc:  # python >2.5
        raise
    return


def Merge(source, destination):
    """
    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            Merge(value, node)
        elif isinstance(value, list):
            destination.setdefault(key, value)
        else:
            if key in destination:
                pass
            else:
                destination.setdefault(key, value)

    return destination

def OpenFollowOnTwitchLink():
    os.startfile("https://twitch.tv/DarthMinos")
    return


def OpenReadMeLink():
    os.startfile(ReadMeFile)
    return


def OpenPaypalDonateLink():
    os.startfile("https://paypal.me/camalotdesigns/10")
    return
def OpenGithubDonateLink():
    os.startfile("https://github.com/sponsors/camalot")
    return
def OpenTwitchDonateLink():
    os.startfile("http://twitch.tv/darthminos/subscribe")
    return

def OpenOverlayInBrowser():
    os.startfile(os.path.realpath(os.path.join(
        os.path.dirname(__file__), "overlay.html")))
    return
def OpenDiscordLink():
    os.startfile("https://discord.com/invite/vzdpjYk")
    return
