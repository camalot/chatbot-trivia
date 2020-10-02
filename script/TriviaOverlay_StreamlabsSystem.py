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

SettingsFile = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "settings.json")
ScriptSettings = None
Initialized = False
CurrentQuestion = None
CurrentAnswers = list([])
CorrectIndex = -1
KnownBots = None
AnsweredCorrect = False


API_URL = "https://opentdb.com/api.php?amount=1&category={0}&difficulty={1}&type={2}"

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
                result = resp['results'][0]
                self.__dict__.update(result)
                numberOfAnswers = len(self.incorrect_answers)
                Parent.Log(ScriptName, "LEN: " + str(numberOfAnswers))
                self.answers = self.incorrect_answers[:]
                position = randrange(numberOfAnswers + 1)
                self.correct_index = position
                Parent.Log(ScriptName, "Correct: " + str(self.correct_index))
                Parent.Log(ScriptName, "Correct: " + str(self.correct_answer))
                Parent.Log(ScriptName, "answers: " + json.dumps(self.answers))
                self.answers.insert(position, self.correct_answer)
                self.points = GetPointsForDifficulty(self.difficulty)
                Parent.Log(ScriptName, "answers: " + json.dumps(self.answers))
            else:
                raise Exception("Unable to load trivia question.")
        except Exception as e:
            Parent.Log(ScriptName, str(e))


class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        try:
            self.Command = "!trivia"
            self.AnswerCommand = "!answer"
            self.Cooldown = 30
            self.QuestionCategory = "Any"
            self.QuestionDifficulty = "Any"
            self.QuestionType = "Any"
            self.PointsEasy = 100
            self.PointsMedium = 250
            self.PointsHard = 500
            self.TimeToAnswer = 60

            self.BackgroundColor = "rgba(0, 0, 0, 0)"
            self.CommandColor = "rgba(153, 74, 0, 1)"
            self.HelpColor = "rgba(200, 200, 200, 1)"
            self.UserColor = "rgba(255, 0, 0, 1)"
            self.AnswerColor = "rgba(255, 255, 255, 1)"
            self.QuestionColor = "rgba(255, 255, 255, 1)"

            self.TimeoutResponse = "No one got the correct answer. The correct answer was '$triviacorrect'."
            self.UnknownAnswerResponse = "@$username -> You should use $triviaanswercommand <number> to answer."
            self.IncorrectResponse = "@$username -> That is not the correct answer."
            self.AlreadyAnsweredResponse = "@$username -> You have already made an incorrect guess on the current question."
            self.ClearResponse = "@$username -> You have cleared the current trivia question. The correct answer was '$triviacorrect'."
            self.CorrectResponse = "@$username -> You got the correct answer: '$triviacorrect' and have been awarded $triviapoints $currencyname."
            self.QuestionResponse = "::TRIVIA QUESTION:: CATEGORY: $triviacategory :: DIFFICULTY: $triviadifficulty :: POINTS: $triviapoints\\n$triviaquestion :: $triviaanswers Use $triviaanswercommand <number> to answer"
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                fileSettings = json.load(f, encoding="utf-8")
                self.__dict__.update(fileSettings)

        except Exception as e:
            Parent.Log(ScriptName, str(e))

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        Parent.Log(ScriptName, "Reload Settings")
        fileLoadedSettings = json.loads(jsonData, encoding="utf-8")
        self.__dict__.update(fileLoadedSettings)


def Init():
    global Initialized
    global ScriptSettings
    global KnownBots
    if Initialized:
        Parent.Log(ScriptName, "Skip Initialization. Already Initialized.")
        return
    seed()
    Parent.Log(ScriptName, "Initialize")

    if KnownBots is None:
        try:
            botData = json.loads(json.loads(Parent.GetRequest(
                "https://api.twitchinsights.net/v1/bots/online", {}))['response'])['bots']
            KnownBots = [bot[0].lower() for bot in botData]
        except:
            Parent.Log(ScriptName, str(e))
            KnownBots = []
    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)

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
        if commandTrigger == ScriptSettings.Command:
            if data.GetParamCount() > 1:
                # SUB COMMANDS
                subCommand = data.GetParam(1).lower()
                if Parent.HasPermission(data.User, "Moderator", ""):
                    if subCommand == "clear":
                        Parent.SendTwitchMessage(
                            Parse(ScriptSettings.ClearResponse, data.User, data.UserName, "", data.Message))
                        ClearCurrentQuestion()
                else:
                    pass
            else:
                TriggerQuestionFromUser(data.User, data.UserName)
        elif CurrentQuestion is not None and commandTrigger == ScriptSettings.AnswerCommand:
            # check if they already answered
            if data.User in CurrentAnswers:
                # ignore since they already answered.
                Parent.SendTwitchMessage(Parse(
                    ScriptSettings.AlreadyAnsweredResponse, data.User, data.UserName, "", data.Message))
                return
            # Someone is answering a trivia question.
            if data.GetParamCount() > 1:
                answer = data.GetParam(1)
                selected_answer = None
                if answer.isnumeric():
                    answer_index = int(answer) - 1
                    if answer_index >= 0:
                        selected_answer = CurrentQuestion.answers[answer_index]
                        CurrentAnswers.append(data.User)
                        Parent.Log(ScriptName, json.dumps(CurrentAnswers))
                        if CurrentQuestion.correct_index == answer_index:
                            AnsweredCorrect = True
                            # Apply Points
                            Parent.AddPoints(data.User, data.UserName, CurrentQuestion.points)
                            # Tell Chat
                            Parent.SendTwitchMessage(Parse(ScriptSettings.CorrectResponse, data.User, data.UserName, "", data.Message))
                            SendQuestionAnsweredEvent(data.UserName)
                            ClearCurrentQuestion()
                            SendQuestionClearEvent()
                        else:
                            Parent.SendTwitchMessage(Parse(ScriptSettings.IncorrectResponse, data.User, data.UserName, "", data.Message))
                else:
                    Parent.SendTwitchMessage(Parse(ScriptSettings.UnknownAnswerResponse, data.User, data.UserName, "", data.Message))
                    return
            else:
                return

def Tick():
    pass

def ScriptToggled(state):
    Parent.Log(ScriptName, "State Changed: " + str(state))
    if state:
        Init()
    else:
        Unload()
    return


def ReloadSettings(jsondata):
    Parent.Log(ScriptName, "Reload Settings")
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
        "$triviacorrect", CurrentQuestion.correct_answer or "NONE")

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

def QuestionTimeoutThread(currentQuestion, seconds, timeoutResponse):
    global AnsweredCorrect
    # Parent.Log(ScriptName, "TIME OUT: THREAD START")
    counter = 0
    while counter < seconds and currentQuestion is not None and not AnsweredCorrect:
        time.sleep(1)
        counter += 1

    if currentQuestion and not AnsweredCorrect:
        SendQuestionTimeoutEvent()
        if timeoutResponse:
            Parent.SendTwitchMessage(timeoutResponse.replace("$triviacorrect", unescapeHtml(currentQuestion.correct_answer)))


    if not AnsweredCorrect:
        ClearCurrentQuestion()
        SendQuestionClearEvent()

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
        fmt += "{0}) {1} :: ".format(str(x+1), unescapeHtml(answers[x]))
    return fmt


def ClearCurrentQuestion():
    global CurrentQuestion
    global CurrentAnswers
    global ScriptName
    CurrentAnswers = None
    CurrentQuestion = None

def GetApiUrl():
    cat = GetItemIdFromName(CATEGORIES, ScriptSettings.QuestionCategory)
    dif = GetItemIdFromName(DIFFICULTIES, ScriptSettings.QuestionDifficulty)
    tpe = GetItemIdFromName(TYPES, ScriptSettings.QuestionType)

    url = API_URL.format(cat, dif, tpe)
    Parent.Log(ScriptName, url)
    return url

def GetNewQuestion():
    global CurrentQuestion
    global CurrentAnswers
    global AnsweredCorrect
    AnsweredCorrect = False
    resp = json.loads(Parent.GetRequest(GetApiUrl(), {}))['response']
    CurrentQuestion = TriviaQuestion(resp)
    CurrentAnswers = list([])
    
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
            "answer": CurrentQuestion.correct_answer
        }))


def SendQuestionClearEvent():
    Parent.BroadcastWsEvent("EVENT_TRIVIA_CLEAR", json.dumps(None))


def SendQuestionAnsweredEvent(user):
    global CurrentQuestion
    if CurrentQuestion is not None:
        Parent.BroadcastWsEvent("EVENT_TRIVIA_ANSWERED", json.dumps({
            "user": user,
            "answer": CurrentQuestion.correct_answer
        }))

def TriggerQuestionFromUser(userid, username):
    if not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command):
        if CurrentQuestion is None:
            GetNewQuestion()
        Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)
        SendQuestionEvent()
        if ScriptSettings.TimeToAnswer > 0:
            # Start a new thread to timeout the question
            threading.Thread(target=QuestionTimeoutThread, args=(
                CurrentQuestion, ScriptSettings.TimeToAnswer, ScriptSettings.TimeoutResponse)).start()
        Parent.SendTwitchMessage(Parse(ScriptSettings.QuestionResponse, userid, username, "", ""))


def TriggerQuestion():
    TriggerQuestionFromUser(Parent.GetChannelName().lower(), Parent.GetChannelName())

def ClearQuestion():
    Parent.SendTwitchMessage(Parse(ScriptSettings.ClearResponse, Parent.GetChannelName().lower(), Parent.GetChannelName(), "", ""))
    ClearCurrentQuestion()

def OpenScriptUpdater():
    currentDir = os.path.realpath(os.path.dirname(__file__))
    chatbotRoot = os.path.realpath(os.path.join(currentDir, "../../../"))
    libsDir = os.path.join(currentDir, "libs/updater")
    Parent.Log(ScriptName, libsDir)
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Parent.Log(ScriptName, tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Parent.Log(ScriptName, "Copy: " + full_file_name)
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
        Parent.Log(ScriptName, updater)
        configJson = json.dumps(updaterConfig)
        Parent.Log(ScriptName, configJson)
        with open(updaterConfigFile, "w+") as f:
            f.write(configJson)
        os.startfile(updater)
        return
    except OSError as exc:  # python >2.5
        raise
    return


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
