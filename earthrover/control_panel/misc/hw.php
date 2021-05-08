<?php
//include_once 'vars.php';

$entry_by=$_POST["entry_by"];
$page=$_POST["page"];

$xx=exec("sudo python /var/www/html/earthrover/control_panel/misc/hw.py $entry_by $page &");

?>
