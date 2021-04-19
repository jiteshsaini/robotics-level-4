var xx,yy,zz;

if (window.DeviceMotionEvent != undefined) {
	window.ondevicemotion = function(e) {
	sleep(250);
		xx=e.accelerationIncludingGravity.x.toFixed(2);
		yy=e.accelerationIncludingGravity.y.toFixed(2);
		zz=e.accelerationIncludingGravity.z.toFixed(2);
		
		document.getElementById("accelerationX").innerHTML = xx;
		document.getElementById("accelerationY").innerHTML = yy;
		document.getElementById("accelerationZ").innerHTML = zz;
	
		if(document.getElementById('acc').value == 'ON')
			send_acc_data(xx,yy,zz);
	}
} 

function acc_toggle()
{
	var id='acc';
	//alert('acc toggle');
	button_caption=document.getElementById(id).value;
		
	if(button_caption=="OFF"){
		document.getElementById(id).value="ON";
		document.getElementById(id).style.backgroundColor="#66ff66";

	}
	if(button_caption=="ON"){
		document.getElementById(id).value="OFF";
		document.getElementById(id).style.backgroundColor="gray";
	}		
}

function sleep(milliseconds) {
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds){
			break;
		}
	}
}

function send_acc_data(xx,yy,zz)
{
	
		$.post("ajax_acc.php",
		{
		acc_x: xx,
		acc_y: yy,
		acc_z:zz
		}
		);
}
