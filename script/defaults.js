var DEFAULT_SETTINGS = {
  "Command": "!trivia",
  "Cooldown": 30,
  "AnswerCommand": "!answer",
  "TimeToAnswer": 60,
  "EnableAutoTrivia": false,
  "AutoTriviaInterval": 60,
  "QuestionResponse": "::TRIVIA QUESTION:: CATEGORY: $triviacategory :: DIFFICULTY: $triviadifficulty :: POINTS: $triviapoints\\n$triviaquestion :: $triviaanswers Use $triviaanswercommand \u03b1 to answer.",
  "CorrectResponse": "@$username -> You got the correct answer: '$triviacorrect' and have been awarded $triviapoints $currencyname.",
  "ClearResponse": "@$username -> You have cleared the current trivia question. The correct answer was '$triviacorrect'.",
  "AlreadyAnsweredResponse": "@$username -> You have already made an incorrect guess on the current question.",
  "IncorrectResponse": "@$username -> That is not the correct answer.",
  "TimeoutResponse": "No one got the correct answer. The correct answer was '$triviacorrect'.",
  "UnknownAnswerResponse": "@$username -> You should use $triviaanswercommand <number> to answer.",
  "DebugMode": false,
  "QuestionCategory": "Any",
  "QuestionDifficulty": "Any",
  "QuestionType": "Any",
  "PointsEasy": 100,
  "PointsMedium": 250,
  "PointsHard": 500,
  "TriviaCorrectBorderColor": "rgba(51, 51, 255, 1)",
  "TriviaCorrectBackgroundColor": "rgba(51, 255, 51, 1)",
  "TriviaCorrectTextColor": "rgba(51, 51, 51, 1)",
  "TriviaAnswerBorderColor": "rgba(255, 51, 51, 1)",
  "TriviaAnswerBackgroundColor": "rgba(51, 51, 51, 1)",
  "TriviaAnswerTextColor": "rgba(170, 170, 170, 1)",
  "TriviaQuestionBorderColor": "rgba(255, 51, 51, 1)",
  "TriviaQuestionBackgroundColor": "rgba(51, 51, 51, 1)",
  "TriviaQuestionTextColor": "rgba(170, 170, 170, 1)",
  "TriviaQuestionCategoryColor": "rgba(51, 255, 255, 1)",
  "TriviaDifficultyTextColor": "rgba(51, 51, 51, 1)",
  "TriviaDifficultyBackgroundColor": "rgba(255, 51, 51, 1)",
  "TriviaWidth": 100,
  "TriviaMarginTop": 0,
  "TriviaTransparency": 0,
  "FontName": "days-one",
  "CustomFontName": "",
  "InTransition": "slideInRight",
  "InAttentionAnimation": "pulse",
  "OutTransition": "slideOutRight",
  "OutAttentionAnimation": "pulse"
};