<?php

$text = $_POST["str"];
$gender = $_POST["gen"];

// escapeshellarg() replaces the old filter_text() helper, which used
//     if (strpos($str, "'"))
// and therefore missed a leading apostrophe entirely - strpos returns 0 there,
// which is falsy. This text is interpolated into a command that runs as root,
// so correct quoting matters.
$text   = escapeshellarg($text);
$gender = escapeshellarg(preg_match('/^[mf]$/', $gender) ? $gender : 'm');

// system(), not os.system() - that was Python syntax in a PHP file. It worked
// on PHP 7 (undefined constant coerced to a string) but PHP 8 makes it fatal.
// Output is redirected so the backgrounded child does not hold the web
// server's stdout open and hang this request.
$APP = dirname(dirname(__DIR__));
// From /tmp: the GPIO library drops a working file in the launch directory.
$cmd = "cd /tmp && python3 " . $APP . "/speaker/speaker_tts.py " .
       $text . " " . $gender . " > " . $APP . "/logs/speaker.log 2>&1 &";

system($cmd);

echo "spoke";
?>
