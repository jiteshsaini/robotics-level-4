// Endpoints resolved from this script's own URL, not the page's: the
// same file is loaded from pages at different depths. The variable is
// named per file because several of these load into one page.
var RC = document.currentScript.src.replace(/js\/[^/]*$/, "");

// e.key rather than the deprecated e.keyCode
document.addEventListener("keydown", function(e){
	if (e.key == "ArrowLeft")  button_direction('l');
	if (e.key == "ArrowUp")    button_direction('f');
	if (e.key == "ArrowRight") button_direction('r');
	if (e.key == "ArrowDown")  button_direction('b');
	if (e.key == " ")          button_direction('s');
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





