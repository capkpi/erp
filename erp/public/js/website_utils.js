// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

if(!window.erp) window.erp = {};

// Add / update a new Lead / Communication
// subject, sender, description
capkpi.send_message = function(opts, btn) {
	return capkpi.call({
		type: "POST",
		method: "erp.templates.utils.send_message",
		btn: btn,
		args: opts,
		callback: opts.callback
	});
};

erp.subscribe_to_newsletter = function(opts, btn) {
	return capkpi.call({
		type: "POST",
		method: "capkpi.email.doctype.newsletter.newsletter.subscribe",
		btn: btn,
		args: {"email": opts.email},
		callback: opts.callback
	});
}

// for backward compatibility
erp.send_message = capkpi.send_message;
