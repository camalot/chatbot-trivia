"use strict";
let animationEndClasses = "webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend";

if (!window.settings) {
	window.settings = {};
}

window.settings = { ...window.DEFAULT_SETTINGS, ...window.settings };
var TimeoutPointer = null;

function initializeUI() {
	console.log(`color: ${settings.AnswerColor}`);
	$(":root")
		.css("--question-color", `${settings.QuestionColor || "rgba(255, 255, 255, 1)"}`)
		.css("--answers-color", `${settings.AnswerColor || "rgba(255, 255, 255, 1)"}`)
		.css("--user-color", `${settings.UserColor || "rgba(255, 0, 0, 1)"}`)
		.css("--help-color", `${settings.HelpColor || "rgba(200, 200, 200, 1)"}`)
		.css("--background-color", `${settings.BackgroundColor || "rgba(0, 0, 0, 0)"}`)
		.css("--command-color", `${settings.CommandColor || "rgba(153, 74, 0, 1)"}`);
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
				console.log(eventData);
				showQuestion(eventData);
				break; 
			case "EVENT_TRIVIA_TIMEOUT":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				questionTimeout(eventData);
				break;
			case "EVENT_TRIVIA_ANSWERED":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}
				questionAnswered(eventData);
				break;
				case "EVENT_TRIVIA_CLEAR":
				if (TimeoutPointer !== null) {
					clearTimeout(TimeoutPointer);
				}

				TimeoutPointer = setTimeout(hideAll, 10 * 1000);
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

function hideAll() {
	var correct = $("#trivia-correct");
	var expired = $("#trivia-expired");
	var trivia = $("#trivia");

	correct.addClass("hidden");
	expired.addClass("hidden");
	trivia.addClass("hidden");
}

function questionTimeout(d) {
	showQuestion(null);
	var expired = $("#trivia-expired");
	$(".who", expired).html(d.user);
	$(".answer", expired).html(d.answer);
	expired.removeClass("hidden");
}

function questionAnswered(d) {
	showQuestion(null);
	var correct = $("#trivia-correct");
	$(".who", correct).html(d.user);
	$(".answer", correct).html(d.answer);
	correct.removeClass("hidden");
}

function showQuestion(q) {
	var trivia = $("#trivia");
	$("#trivia-correct").addClass("hidden");
	$("#trivia-expired").addClass("hidden");
	if (q) {
		$(".category", trivia).html(q.category);
		$(".question", trivia).html(q.question);
		$(".answers", trivia).empty();
		for(var x = 0; x < q.answers.length; ++x) {
			$(".answers").append(`<li>${q.answers[x]}</li>`)
		}
		$("#answer-command").html(settings.AnswerCommand);

		trivia.removeClass("hidden");
	} else {
		$(".category", trivia).empty();
		$(".question", trivia).html();
		$(".answers", trivia).empty();
		$("#answer-command").empty();
		trivia.addClass("hidden");
	}
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
});
