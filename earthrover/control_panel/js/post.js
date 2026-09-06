// Replaces jQuery's $.post, which was the only thing jQuery was used for.
// The callback runs either way - with the response text on success, null on
// failure - so it covers both the plain posts and the two that used .always().
function post(url, data, done)
{
	fetch(url, {method: "POST", body: new URLSearchParams(data)})
		.then(function(r){ return r.text(); })
		.catch(function(e){ console.log("post " + url + " failed:", e); return null; })
		.then(function(text){ if (done) done(text); });
}
