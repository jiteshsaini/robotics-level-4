<?php

$myFile = "range.txt";

$fr=fopen($myFile, 'r') or die("can't open file");
$str=fread($fr, '20');
fclose($fr);

if($str!=""){
	$str1=round($str,1);
	echo"$str1";
}

?>
