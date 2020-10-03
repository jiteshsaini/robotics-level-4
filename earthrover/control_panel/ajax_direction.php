<?php
include_once '../vars.php';

$dir=$_POST["direction"];

move($dir);

echo"Dir: \" $dir \"  <br>";

?>
