<?php
//include_once 'vars.php';

$state=$_POST["state"];
//echo"range sensor status: $state <br>";

$app = dirname(dirname(__DIR__));
$xx=exec("python3 " . $app . "/range_sensor/master.py $state");

?>
