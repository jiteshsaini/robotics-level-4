// Endpoints resolved from this script's own URL, not the page's: the
// same file is loaded from pages at different depths. The variable is
// named per file because several of these load into one page.
var RNG = document.currentScript.src.replace(/[^/]*$/, "");

var interval;
function toggle_rangeSensor(id)
	{
		
		//alert(id);
		console.log("toggle_rangeSensor button clicked");
		button_caption=document.getElementById(id).value;
		//alert(button_caption);
		if(button_caption=="OFF"){
			rangeSensor(1);
			
			document.getElementById(id).value="ON";
			document.getElementById(id).style.backgroundColor="#66ff66";
			//alert("hi");
			interval=window.setInterval(get_range, 500); //timer for initiating ajax request 

			
			
		}
		if(button_caption=="ON"){
			rangeSensor(0);
			document.getElementById(id).value="OFF";
			document.getElementById(id).style.backgroundColor="white";
			
			clearInterval(interval);
			document.getElementById("range").innerHTML="";
			
			
		}
			
	}
function rangeSensor(state)
{	console.log("state: ", state);
	
	$.post(RNG + "ajax_rangeSensor.php",
	{
		state: state
	}
	);

}
function get_range()
	{
		$.post(RNG + "ajax_getRange.php",
		{
		//direction: dir
		//speed:sp
		},
		function(data){
			//document.getElementById("range").innerHTML = data;
			
			if (data<=30)
				document.getElementById("range").style.color="red";
			else if(data > 30 && data <= 60) 
				document.getElementById("range").style.color="orange";
			else
				document.getElementById("range").style.color="blue";
			
			if (data>400)
				document.getElementById("range").innerHTML = "-";
			else
				document.getElementById("range").innerHTML = data;
				
		});
	}
