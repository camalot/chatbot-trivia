"use strict";
let animationEndClasses = "webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend";

if (!window.settings) {
	window.settings = {};
}
window.ANSWER_SELECTORS = ['a','b','c','d'];

window.settings = { ...window.DEFAULT_SETTINGS, ...window.settings };
let TimeoutPointer = null;

/*
	TriviaQuestion:
	
	{
		category: "Unknown",
		type: "none",
		difficulty: "none",
		question: "",
		correct_answer: "",
		correct_index: -1,
		incorrect_answers: [],
		answers: []
	}
*/

function initializeUI() {

	let vars = getUrlVars();
	if (parseInt(vars.debug) === 1) {
		$(".debug").removeClass("debug");
	}

	let topacity = (-(settings.TriviaTransparency || 0)+100) / 100;
	$(":root")
		.css("--trivia-container-width", `${settings.TriviaWidth || "80"}%`)

		.css("--trivia-correct-border-color", `${settings.TriviaCorrectBorderColor || "rgba(51, 51, 255, 1)"}`)
		.css("--trivia-correct-background-color", `${settings.TriviaCorrectBackgroundColor || "rgba(51, 255, 51, 1)"}`)
		.css("--trivia-correct-text-color", `${settings.TriviaCorrectTextColor || "rgba(51, 51, 51, 1)"}`)
		.css("--trivia-answer-border-color", `${settings.TriviaAnswerBorderColor || "rgba(255, 51, 51, 1)"}`)
		.css("--trivia-answer-background-color", `${settings.TriviaAnswerBackgroundColor || "rgba(51, 51, 51, 1)"}`)
		.css("--trivia-answer-text-color", `${settings.TriviaAnswerTextColor || "rgba(170, 170, 170, 1)"}`)
		.css("--trivia-question-background-color", `${settings.TriviaQuestionBackgroundColor || "rgba(51, 51, 51, 1)"}`)
		.css("--trivia-question-border-color", `${settings.TriviaQuestionBorderColor || "rgba(255, 51, 51, 1)"}`)
		.css("--trivia-question-text-color", `${settings.TriviaQuestionTextColor || "rgba(170, 170, 170, 1)"}`)
		.css("--trivia-question-category-color", `${settings.TriviaQuestionCategoryColor || "rgba(51, 255, 255, 1)"}`)
		.css("--trivia-difficulty-background-color", `${settings.TriviaDifficultyBackgroundColor || "rgba(51, 255, 255, 1)"}`)
		.css("--trivia-difficulty-text-color", `${settings.TriviaDifficultyTextColor || "rgba(255, 51, 51, 1)"}`)
		.css("--trivia-command-color", `${settings.TriviaCommandColor || "rgba(51, 51, 255, 1)"}`)

		.css("--trivia-margin-top", `${settings.TriviaMarginTop || "0"}px`)
		.css("--trivia-opacity", `${topacity || "1"}`)
		.css("--trivia-timeout", `${settings.TimeToAnswer || "60"}s`)
		
		;

	var fontName = settings.FontName;
	var customFontName = settings.CustomFontName;
	if (fontName && fontName === "custom" && customFontName && customFontName !== "") {
		loadFontsScript(customFontName);
	} else {
		$(":root")
			.css("--trivia-font-family", fontName);
	}

	$("#answer-command").html(settings.AnswerCommand);
	$("#start-command").html(settings.Command);
}

function startTrivia(trivia) {
	populateDifficulty(trivia.difficulty, trivia.points);
	// get the question
	populateQuestion(trivia.category, trivia.question);
	// get the answers
	populateAnswers(trivia.answers, trivia.correct_index);
	// $(".trivia").removeClass("hidden").removeClass("closed");
	$("#triva-host")
		.removeClass()
		.addClass(`${settings.InTransition} animated`)
		.one(animationEndClasses, function () {
			$(this)
				.off(animationEndClasses)
				.removeClass()
				.addClass(`${settings.InAttentionAnimation} animated`)
				.one(animationEndClasses, function () {
					$(this)
						.removeClass();
					console.log("end in attention animation");
				});
		})
		.dequeue();
}

function closeTrivia(who) {
	// show who won
	$(".trivia .result .who").html(who);
	$(".trivia").addClass("closed");
}

function shutdownTrivia() {
	$("#triva-host")
		.removeClass()
		.addClass(`${settings.OutAttentionAnimation} animated`)
		.one(animationEndClasses, function () {
			$(this)
				.off(animationEndClasses)
				.removeClass()
				.addClass(`${settings.OutTransition} animated`)
				.one(animationEndClasses, function () {
					$(this)
						.removeClass()
						.addClass("hidden");
					console.log("end in attention animation");
					$(".trivia").removeClass("closed");
					populateAnswers([], -1);
					populateQuestion("", "");
				});
		})
		.dequeue();
}

function populateDifficulty(difficulty, points) {
	$(".difficulty").html(difficulty);
	$(".points").html(points);
}

function populateQuestion(category, question) {
	let $q = $(".question .text");
	let $c = $(".question .category");
	$q.html(question);
	$c.html(category);
}

function populateAnswers(values, correctIndex) {
	// <span class="n">A</span>
	let list = $(".answers ol");
	list.empty();
	for(let x = 0; x < values.length; ++x) {
		let itemClass = x === correctIndex ? "correct" : "";
		list.append(`<li class="${itemClass}"><span class="n">${window.ANSWER_SELECTORS[x]}</span>${values[x]}</li>`)
	}
}

function loadFontsScript(font) {
	let fnt = font.toLowerCase().replace(" ", "-");
	var script = document.createElement('script');
	script.onload = function () {
		$(":root").css("--font-name", `${fnt}, Arial, sans-serif`);
	};
	script.src = `http://use.edgefonts.net/${fnt}.js`;

	document.head.appendChild(script);
}

function getUrlVars() {
	var vars = [], hash;
	var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	for (var i = 0; i < hashes.length; i++) {
		hash = hashes[i].split('=');
		vars.push(hash[0]);
		vars[hash[0]] = hash[1];
	}
	return vars;
}


function connectWebsocket() {
	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	let socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = function () {
		// AnkhBot Authentication Information
		let auth = {
			author: "DarthMinos",
			website: "darthminos.tv",
			api_key: API_Key,
			events: [
				"EVENT_TRIVIA_SETTINGS",
				"EVENT_TRIVIA_QUESTION",
				"EVENT_TRIVIA_TIMEOUT",
				"EVENT_TRIVIA_ANSWERED",
				"EVENT_TRIVIA_CLEAR"
			]
		};

		// Send authentication data to ChatBot ws server

		socket.send(JSON.stringify(auth));
	};

	//-------------------------------------------
	//  Websocket Event: OnMessage
	//-------------------------------------------
	socket.onmessage = function (message) {
		console.log(message);
		// Parse message
		let socketMessage = JSON.parse(message.data);
		let eventName = socketMessage.event;
		console.log(socketMessage);
		let eventData = typeof socketMessage.data === "string" ? JSON.parse(socketMessage.data || "{}") : socketMessage.data;
		switch (eventName) {
			case "EVENT_TRIVIA_QUESTION":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				if(eventData) {
					startTrivia(eventData);
				}
				break;
			case "EVENT_TRIVIA_TIMEOUT":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				closeTrivia("no one");
				TimeoutPointer = setTimeout(shutdownTrivia, 5 * 1000);
				break;
			case "EVENT_TRIVIA_ANSWERED":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				closeTrivia(eventData.user);
				TimeoutPointer = setTimeout(shutdownTrivia, 5 * 1000);
				break;
			case "EVENT_TRIVIA_CLEAR":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				shutdownTrivia();
				break;
			case "EVENT_TRIVIA_SETTINGS":
				window.settings = eventData;
				if (validateInit()) {
					initializeUI();
				}
				break;
			default:
				console.log(eventName);
				break;
		}
	};

	//-------------------------------------------
	//  Websocket Event: OnError
	//-------------------------------------------
	socket.onerror = function (error) {
		console.error(`Error: ${error}`);
	};

	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = function () {
		console.log("close");
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;
		// Try to reconnect every 5s
		setTimeout(function () { connectWebsocket(); }, 5000);
	};

}

function startTimer(seconds) {
	setTimeout(function() { 

	}, 1000, seconds * 1000);
}


function validateSettings() {
	let hasApiKey = typeof API_Key !== "undefined";
	let hasSettings = typeof settings !== "undefined";

	return {
		isValid: hasApiKey && hasSettings,
		hasSettings: hasSettings,
		hasApiKey: hasApiKey
	};
}

function validateInit() {
	// verify settings...
	let validatedSettings = validateSettings();

	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (!validatedSettings.isValid) {
		$("#config-messages").removeClass("hidden");
		$("#config-messages .settings").removeClass(validatedSettings.hasSettings ? "valid" : "hidden");
		$("#config-messages .api-key").removeClass(validatedSettings.hasApiKey ? "valid" : "hidden");
		return false;
	}
	return true;
}

jQuery(document).ready(function () {
	if (validateInit()) {
		initializeUI();
		connectWebsocket();
	} else {
		console.log("Invalid");
	}
	$("[data-button]").on("click", function() {
		let $this = $(this);
		let action = $this.data("action");
		switch(action) {
			case "newQuestion": 
				startTrivia({
					points: 100,
					difficulty: "easy",
					category: "Entertainment: Sports",
					question: "In Baseball, how many times does the ball have to be pitched outside of the strike zone before the batter is walked?",
					answers: [1, 2, 3, 4],
					correct_index: 3
				});
				break;	
			case "endQuestion":
				closeTrivia();
				break;
			case "clearQuestion":
				shutdownTrivia();
				break;
		}
	});
});
