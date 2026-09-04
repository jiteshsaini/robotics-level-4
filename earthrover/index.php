<?php
	if (!empty($_SERVER['HTTPS']) && ('on' == $_SERVER['HTTPS'])) {
		$uri = 'https://';
	} else {
		$uri = 'http://';
	}
	// relative on purpose: an absolute /earthrover/... sends the browser to
	// whatever is installed at that path instead of this copy
	header('Location: control_panel/');
	exit;
?>
