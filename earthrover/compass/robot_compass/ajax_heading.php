<?php

//this file receives the heading information from client (mobile with control web app) and writes it on txt file
$h=$_POST["heading"];

$myFile = "heading.txt";
$fh = fopen($myFile, 'w') or die("can't open file");
fwrite($fh,$h);

fclose($fh);


?>
