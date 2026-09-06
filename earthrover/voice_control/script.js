var noBrowserSupport = document.querySelector('.no-browser-support');

try {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
  if (noBrowserSupport) noBrowserSupport.style.display = 'none';
}
catch(e) {
  console.error(e);
  if (noBrowserSupport) noBrowserSupport.style.display = '';
}


var noteTextarea = document.getElementById('note-textarea');
var instructions = document.getElementById('recording-instructions');

var btn_start = document.getElementById('start-record-btn');
var btn_stop  = document.getElementById('stop-record-btn');
var noteContent = '';


/*-----------------------------
      Voice Recognition 
------------------------------*/

// If false, the recording will stop after a few seconds of silence.
// When true, the silence period is longer (about 15 seconds),
recognition.continuous = true;

// This block is called every time the Speech APi captures a line. 
recognition.onresult = function(event) {

  // event is a SpeechRecognitionEvent object.
  // It holds all the lines we have captured so far. 
  // We only need the current one.
  var current = event.resultIndex;

  // Get a transcript of what was said.
  var transcript = event.results[current][0].transcript;

  // There is a weird bug on mobile, where everything is repeated twice.
  // There is no official solution so far so we have to handle an edge case.
  var mobileRepeatBug = (current == 1 && transcript == event.results[0][0].transcript);
  console.log("mobile bug: " + mobileRepeatBug);

  if(!mobileRepeatBug) {

    noteTextarea.innerHTML = transcript;

    action(transcript);

  }

};

function action(text){

	console.log("text:" + text);

	post("action.php", {txt: text}, function(data){
		document.getElementById("response").innerHTML = data;
	});
}


recognition.onstart = function() { 
  instructions.textContent = 'Voice recognition activated';
}

recognition.onspeechend = function() {
  instructions.textContent = 'Voice recognition turned off';
  btn_start.style.backgroundColor = "white";
}

recognition.onerror = function(event) {
  if(event.error == 'no-speech') {
    instructions.textContent = 'No speech was detected. Try again.';
  };
}

/*-----------------------------
    buttons
------------------------------*/

btn_start.addEventListener('click', function(e) {
	console.log("start recog");
  recognition.start();
  btn_start.style.backgroundColor = "green";
});


btn_stop.addEventListener('click', function(e) {
	console.log("stop recog");
  recognition.stop();
  instructions.textContent = 'Voice recognition stopped.';
  btn_start.style.backgroundColor = "white";
});
