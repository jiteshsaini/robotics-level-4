<?php
include_once '../vars.php';

$speed=$_POST["speed"];

$pwm_val=intval($speed);

//echo"pwm val: \" $pwm_val \"  <br>";
set_speed($pwm_val);

?>
