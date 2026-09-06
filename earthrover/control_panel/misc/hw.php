<?php

// The two values below arrive by POST and used to be interpolated straight
// into a shell command, which made this endpoint an unauthenticated command
// injection: anyone on the network could run arbitrary commands as www-data by
// putting a ';' in "entry_by". They are now matched against a strict pattern
// and passed as escaped arguments.
//
// This also no longer runs under sudo. Reading the local IP and making an
// HTTPS request needs no privileges, and running it as root put it on the
// path to a full system compromise.

$entry_by = $_POST["entry_by"] ?? "";
$page     = $_POST["page"] ?? "";

// Plain names only: letters, digits, dot, dash, underscore. 
$safe = "/^[A-Za-z0-9._-]{1,64}$/";
if (!preg_match($safe, $entry_by) || !preg_match($safe, $page)) {
    http_response_code(400);
    echo "bad parameters";
    exit;
}

// Detached so a slow or unreachable endpoint never delays the page.
$cmd = "python3 " . escapeshellarg(__DIR__ . "/hw.py")
     . " " . escapeshellarg($entry_by)
     . " " . escapeshellarg($page)
     . " > /dev/null 2>&1 &";
exec($cmd);

echo "ok";
?>
