// Global variable
var img = null,
	needle = null,
	ctx = null,
	degrees = 0;


function clearCanvas() {
	 // clear canvas
	ctx.clearRect(0, 0, 200, 200);
}

function draw() {
	
	//degrees=get_data();
	$.get("read_robot_heading.php", function(data, status){degrees = data;});
	
	console.log("degrees: " + degrees);
	
	clearCanvas();

	// Draw the compass onto the canvas
	ctx.drawImage(img, 0, 0);

	// Save the current drawing state
	ctx.save();

	// Now move across and down half the 
	ctx.translate(100, 100);

	// Rotate around this point
	ctx.rotate(degrees * (Math.PI / 180));

	// Draw the image back and up
	ctx.drawImage(needle, -100, -100);

	// Restore the previous drawing state
	ctx.restore();

	// Increment the angle of the needle by 5 degrees
	//degrees += 5;
	//degrees = 30;
}



function imgLoaded() {
	// Image loaded event complete.  Start the timer
	setInterval(draw, 1000);
}

function init() {
	// Grab the compass element
	var canvas = document.getElementById('followup_compass');

	// Canvas supported?
	if (canvas.getContext('2d')) {
		ctx = canvas.getContext('2d');

		// Load the needle image
		needle = new Image();
		needle.src = 'needle3.png';

		// Load the compass image
		img = new Image();
		img.src = 'scale3.png';
		img.onload = imgLoaded;
	} else {
		alert("Canvas not supported!");
	}
}
