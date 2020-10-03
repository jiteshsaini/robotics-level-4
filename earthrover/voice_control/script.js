try {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
  $('.no-browser-support').hide();
}
catch(e) {
  console.error(e);
  $('.no-browser-support').show();
}


var noteTextarea = $('#note-textarea');
var instructions = $('#recording-instructions');

var btn_start = $('#start-record-btn');
var btn_stop = $('#stop-record-btn');
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
    
    noteTextarea.html(transcript);
   
    action(transcript);
    
  }
  
 
};

function action(text){

	console.log("text:" + text);

	$.post("action.php",
    {
      txt: text
    },
    function(data,status){
    document.getElementById("response").innerHTML = data;
    });
}


recognition.onstart = function() { 
  instructions.text('Voice recognition activated');
 
}

recognition.onspeechend = function() {
  instructions.text('Voice recognition turned off');
  btn_start.css("background-color", "white");
}

recognition.onerror = function(event) {
  if(event.error == 'no-speech') {
    instructions.text('No speech was detected. Try again.');  
  };
}

/*-----------------------------
    buttons
------------------------------*/

$('#start-record-btn').on('click', function(e) {
	console.log("start recog");
 
  recognition.start();
  btn_start.css("background-color", "green");
});


$('#stop-record-btn').on('click', function(e) {
	console.log("stop recog");
  recognition.stop();
  instructions.text('Voice recognition stopped.');
  btn_start.css("background-color", "white");
   
});


