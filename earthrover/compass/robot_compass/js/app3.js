
window.addEventListener("deviceorientation", onHeadingChange);
// the outer part of the compass that rotates
var rose = document.getElementById("rose");

var positionCurrent = null;

// called on device orientation change
function onHeadingChange(event) {
   var orientation = event.alpha;
  // var orientation = getBrowserOrientation();
  if (typeof orientation !== "undefined" && orientation !== null) { 
      positionCurrent = orientation;

      var phase = positionCurrent < 0 ? 360 + positionCurrent : positionCurrent;
      var heading = 360 - phase | 0;
     // positionHng.textContent = heading + "°";
			
      get_heading(heading);

      // apply rotation to compass rose
      if (typeof rose.style.transform !== "undefined") {
        rose.style.transform = "rotateZ(" + positionCurrent + "deg)";
      } else if (typeof rose.style.webkitTransform !== "undefined") {
        rose.style.webkitTransform = "rotateZ(" + positionCurrent + "deg)";
      }
  } 
  else {
      // device can't show heading
      //positionHng.textContent = "not";
      alert("No Orientation");
  }
}
	

	
		

 


