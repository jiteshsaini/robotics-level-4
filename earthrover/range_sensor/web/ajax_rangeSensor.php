<?php
//include_once 'vars.php';

$state=$_POST["state"];

// The same single-owner rule the other way round: avoid_collision.py claims
// the motor pins, so it cannot start while an AI feature holds them.
require_once dirname(dirname(__DIR__)) . "/vars.php";
if ($state == "1") { er_pin_guard("collision avoidance"); }

//echo"range sensor status: $state <br>";

$app = dirname(dirname(__DIR__));
// From /tmp: the GPIO library drops a working file in the launch directory.
$xx=exec("cd /tmp && python3 " . $app . "/range_sensor/master.py $state");

?>
