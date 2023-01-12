<?php
//include_once '../vars.php';
	
$msg=$_POST["message"];

if ($msg=="pin40on"){
	set_gpio('40','1');
}

elseif ($msg=="pin40off"){
	set_gpio('40','0');
}

elseif ($msg=="pin38on"){
	set_gpio('38','1');
}

elseif ($msg=="pin38off"){
	set_gpio('38','0');
}

elseif ($msg=="allon"){
	set_gpio('40','1');
	set_gpio('38','1');
}

elseif ($msg=="alloff"){
	set_gpio('40','0');
	set_gpio('38','0');
}

function set_gpio($pin,$x){
	system("sudo gpio -1 mode $pin out"); // seta o pino físico 40 (gpio -1 ) como sada (out)
    system("sudo gpio -1 write $pin $x"); // Liga o pino físico 40
	echo "gpio $pin $x <br>";
	//switch($x){
	//	case '1': $z='dh';break;
	//	case '0': $z='dl';break;
	//	case 'output': $z='op';break;
	//}
	//$cmd="sudo raspi-gpio set $pin $z";
	//system($cmd);
	
	//echo"$x: $cmd <br>";
}

?>
