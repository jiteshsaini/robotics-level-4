// Endpoints resolved from this script's own URL, not the page's: the
// same file is loaded from pages at different depths. The variable is
// named per file because several of these load into one page.
var RNG = document.currentScript.src.replace(/[^/]*$/, "");

var interval;

function toggle_rangeSensor(id)
	{
		console.log("toggle_rangeSensor button clicked");
		button_caption=document.getElementById(id).value;

		if(button_caption=="OFF"){
			rangeSensor(1);
			show_range_on(id);
		}
		if(button_caption=="ON"){
			rangeSensor(0);
			document.getElementById(id).value="OFF";
			document.getElementById(id).classList.remove("is-on");

			clearInterval(interval);
			document.getElementById("range").innerHTML="";
		}
	}

// The button on and the readout polling, without sending the start command:
// used when the sensor is already running and this page has just arrived.
function show_range_on(id)
	{
		document.getElementById(id).value="ON";
		document.getElementById(id).classList.add("is-on");
		clearInterval(interval);
		interval=window.setInterval(get_range, 500);
	}

function resume_rangeSensor()
	{
		show_range_on("range_button");
	}

function rangeSensor(state)
{
	console.log("state: ", state);
	post(RNG + "ajax_rangeSensor.php", {state: state});
}

function get_range()
	{
		post(RNG + "ajax_getRange.php", {}, function(data){
			// How close it is, as a class. Set here as an inline style it beat
			// the stylesheet, and plain blue was hard to read on the readout.
			var el = document.getElementById("range");
			el.classList.remove("near", "mid");
			if (data <= 30)                   el.classList.add("near");
			else if (data > 30 && data <= 60) el.classList.add("mid");

			// 400 cm is past what the sensor can measure, not a distance
			el.innerHTML = (data > 400) ? "-" : data;
		});
	}
