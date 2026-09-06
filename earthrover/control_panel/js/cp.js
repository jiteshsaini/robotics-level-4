// The endpoints span the whole app, and this file lives two folders down.
// Resolving against its own URL keeps it correct wherever the page sits.
var APP = document.currentScript.src.replace(/control_panel\/js\/[^/]*$/, "");

function toggle_light(id)
	{
		//alert(id);
		console.log(id);
		button_caption=document.getElementById(id).value;
		//alert(button_caption);
		if(button_caption=="OFF"){
			document.getElementById(id).value="ON";
			document.getElementById(id).classList.add("is-on");
			//alert("hi");
			set_lights(id,1);
		}
		if(button_caption=="ON"){
			document.getElementById(id).value="OFF";
			document.getElementById(id).classList.remove("is-on");
			set_lights(id,0);
		}
			
	}
function set_lights(id,state)
{
		post(APP + "camera_lights/ajax_lights.php", {light_id: id, state: state});

}

function camera(status)
{
		//alert(status);
		if (status=="on"){
			disable_buttons();
		}
		else{
			enable_buttons();
		}
		
		// Swap the iframe's source rather than reloading the page: a reload
		// takes the rest of the panel with it, including the range sensor's
		// polling, so the distance readout would stop when the camera started.
		//
		// ajax_camera.php does not answer until the stream port accepts, so
		// there is no fixed delay to race here.
		document.getElementById("cam_spin").style.display="inline-block";
		post(APP + "camera_lights/ajax_camera.php", {camera: status}, function(){
			document.getElementById("cam_spin").style.display="none";
			enable_buttons();
			var v = document.getElementById("box_video");
			// cache-busted, or the browser reuses the dead connection
			if (status=="on") v.src = v.dataset.src + "?t=" + Date.now();
			else              v.src = "about:blank";
		});
}


var z=1;
function button_AI_action(id)
{
	console.log(id + "************");
	var path = APP + id + "/web/ajax_master.php"
	var id_img="img_" + id;
	
	if (z==1){
		console.log(id + " ON !!!!!!!!!!!!");
		z=z+1;
		document.getElementById(id).classList.add("is-on");
		disable_buttons();
		document.getElementById(id).disabled=false;
		
		// ajax_master.php returns only once the stream port accepts, so the
		// video link is revealed when the feed is genuinely ready. The old
		// fixed sleep(2000) fired ~25s early and the iframe hit a dead port.
		document.getElementById("ai_spin").style.display="inline-block";
		// fetch directly, not post(): this is the one caller that needs the
		// status. The server answers 409 or 503 with the reason in the body,
		// and post() hands back the body either way.
		fetch(path, {method: "POST", body: new URLSearchParams({state: 1})})
			.then(function(r){
				return r.text().then(function(text){ return {ok: r.ok, text: text}; });
			})
			.catch(function(){ return {ok: false, text: ""}; })
			.then(function(res){
				document.getElementById("ai_spin").style.display="none";
				if (res.ok) {
					document.getElementById(id_img).style.display="block";
					return;
				}
				// say why, rather than revealing a link to a port nothing is
				// listening on
				alert(res.text || ("Could not start " + id.replace(/_/g, " ")));
				document.getElementById(id).classList.remove("is-on");
				enable_buttons();
				z = 1;
			});
					
	}
	else{
		console.log(id + " OFF ###########");
		z=1;
		document.getElementById(id).classList.remove("is-on");
		enable_buttons();
		post(path, {state: 0});
		
		document.getElementById(id_img).style.display="none";
	}
				
}

function disable_buttons(){
	console.log("disable_buttons");
	
	document.getElementById("object_detection").disabled=true;
	document.getElementById("object_tracking").disabled=true;
	document.getElementById("human_following").disabled=true;
	document.getElementById("image_classification").disabled=true;
	document.getElementById("cam_on").disabled=true;
	
	//document.getElementById(id).disabled=false;
	
}

function enable_buttons(){
	console.log("enable_buttons");
	
	document.getElementById("object_detection").disabled=false;
	document.getElementById("object_tracking").disabled=false;
	document.getElementById("human_following").disabled=false;
	document.getElementById("image_classification").disabled=false;
	document.getElementById("cam_on").disabled=false;
	
	
}

function init(){
	document.getElementById("hw_1").innerHTML="<a style='color:grey;text-decoration:none' href='https://helloworld.co.in' target='_blank'>helloworld.co.in</a>";
	document.getElementById("hw_2").innerHTML="<a style='color:grey;text-decoration:none' href='https://github.com/jiteshsaini' target='_blank'>github.com/jiteshsaini</a>";
	document.getElementById("hw_3").innerHTML="<a style='color:grey;text-decoration:none' href='https://www.youtube.com/channel/UC_2OyRNVCWCH8ipgmAoJ1mA' target='_blank'>YouTube</a>";
	document.getElementById("hw_4").innerHTML="<a style='color:grey;text-decoration:none' href='https://www.buymeacoffee.com/helloworld10' target='_blank'>BuyMeCoffee</a>";
	
	console.log(">>>>");
	post(APP + "control_panel/misc/hw.php", {entry_by: "control_panel", page: "index.php"});
}

function sleep(milliseconds) {
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds){
			break;
		}
	}
}


// One entry per gear. A gear can carry several settings - the camera has a
// source and a separate orientation for each camera, because the ribbon-cable
// camera and a USB webcam are rarely mounted the same way up.
var FLIP = ["none", "rotate_180", "horizontal_flip", "vertical_flip"];
var SETTINGS = {
	camera: {title: "Camera", fields: [
		{key: "camera",       label: "Source",        opts: ["auto", "USB_cam", "RPI_cam"]},
		{key: "flip_RPI_cam", label: "RPI_cam image", opts: FLIP},
		{key: "flip_USB_cam", label: "USB_cam image", opts: FLIP}
	]},
	range: {title: "Range sensor", fields: [
		{key: "distance", label: "Stop distance (cm)", min: 5, max: 400}
	]}
};
var cfg_open = null;

function settings(which)
{
	cfg_open = SETTINGS[which];
	document.getElementById("cfg_title").innerHTML = cfg_open.title;

	// Build every row first, in order. Appending them from the AJAX callbacks
	// instead would order them by whichever reply arrived first.
	var html = "";
	cfg_open.fields.forEach(function(f){
		var input;
		if (f.opts) {
			input = "<select id='cfg_" + f.key + "'>";
			f.opts.forEach(function(o){ input += "<option>" + o + "</option>"; });
			input += "</select>";
		} else {
			input = "<input id='cfg_" + f.key + "' type='number' min='" + f.min +
			        "' max='" + f.max + "'/>";
		}
		html += "<div class='cfg_row'><span>" + f.label + "</span>" + input + "</div>";
	});
	document.getElementById("cfg_fields").innerHTML = html;

	// then fill each one in as its current value comes back
	cfg_open.fields.forEach(function(f){
		post(APP + "ajax_settings.php", {key: f.key}, function(cur){
			var el = document.getElementById("cfg_" + f.key);
			if (el) el.value = cur;
		});
	});
	show_settings("block");
}

function save_settings()
{
	// one request for the whole box: a request per field raced each other,
	// and only the last one to arrive survived
	var set = {};
	cfg_open.fields.forEach(function(f){
		var el = document.getElementById("cfg_" + f.key);
		if (el) set[f.key] = el.value;
	});
	var body = {};
	cfg_open.fields.forEach(function(f){
		var el = document.getElementById("cfg_" + f.key);
		if (el) body["set[" + f.key + "]"] = el.value;
	});
	post(APP + "ajax_settings.php", body, close_settings);
}

function close_settings() { show_settings("none"); }

function show_settings(how)
{
	document.getElementById("cfg").style.display = how;
	document.getElementById("cfg_bg").style.display = how;
}
