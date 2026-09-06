// Endpoints resolved from this script's own URL, not the page's: the
// same file is loaded from pages at different depths. The variable is
// named per file because several of these load into one page.
var RC = document.currentScript.src.replace(/js\/[^/]*$/, "");

// e.key rather than the deprecated e.keyCode.
//
// This file is loaded by the panel as well as by the remote pad it embeds, so
// the arrows work wherever the focus happens to be. Each page gets its own
// listener; they do not interfere.
document.addEventListener("keydown", function(e){
	// Leave the keys alone for a control that uses them itself - the speaker
	// text box, a dropdown, the speed slider. The test is on the type and not
	// on the tag because every button here is an <input type=submit>, and the
	// focus stays on one after it is clicked: a tag test swallowed every arrow
	// key from then on.
	var el = e.target, t = el.tagName;
	if (el.isContentEditable || t == "TEXTAREA" || t == "SELECT") return;
	if (t == "INPUT" && /^(text|password|search|email|number|url|tel|range)$/i.test(el.type)) return;

	var dir = {ArrowLeft: 'l', ArrowUp: 'f', ArrowRight: 'r',
	           ArrowDown: 'b', " ": 's'}[e.key];
	if (!dir) return;
	e.preventDefault();   // or the page scrolls away under you while driving
	button_direction(dir);
});

//---------DIRECTION---------------------------------
function button_direction(val)
{
	console.log("button val:" + val);
	post(RC + "ajax_direction.php", {direction: val});
}

//---------SPEED--------------------------------------
function speed_slider(val)
{
	console.log("slider val:" + val);
	post(RC + "ajax_speed.php", {speed: val});
}





