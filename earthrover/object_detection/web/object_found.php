<?php
$myfile = fopen("object_found.txt", "r") or die("Unable to open file!");
$str= fread($myfile,5);
fclose($myfile);

$str=intval($str);

echo"$str";
/*
if($str>0){
	//echo"<br>writing 0";
	$myfile = fopen("object_found.txt", "w") or die("Unable to open file!");
	fwrite($myfile,"0");
	fclose($myfile);
	
}
*/
?>
