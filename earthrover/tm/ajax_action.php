<?php
include_once '../vars.php';
	
$msg=$_POST["message"];

if ($msg=="left"){
	left();
}
elseif ($msg=="right"){
	right();
}
elseif ($msg=="forward"){
	forward();
}
elseif ($msg=="backward"){
	back();
}
elseif ($msg=="light_on"){
	system("gpio -g write $cameralight 1");
			
}
elseif ($msg=="speak"){
	//speak();
	$text="i love machine learning";
	$gender="f";
	$cmd="sudo python /var/www/html/earthrover/speaker/speaker_tts.py '".$text."' '".$gender."' &";
	os.system($cmd);
}
else{
	stop();
	system("gpio -g write $cameralight 0");
}

/*
$myFile = "testFile.txt";
$fh = fopen($myFile, 'w') or die("can't open file");
fwrite($fh, $msg);
fclose($fh);
*/
?>
