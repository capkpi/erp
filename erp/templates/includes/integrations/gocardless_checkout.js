$(document).ready(function() {
	var data = {{ capkpi.form_dict | json }};
	var doctype = "{{ reference_doctype }}"
	var docname = "{{ reference_docname }}"

	capkpi.call({
		method: "erp.templates.pages.integrations.gocardless_checkout.check_mandate",
		freeze: true,
		headers: {
			"X-Requested-With": "XMLHttpRequest"
		},
		args: {
			"data": JSON.stringify(data),
			"reference_doctype": doctype,
			"reference_docname": docname
		},
		callback: function(r) {
			if (r.message) {
				window.location.href = r.message.redirect_to
			}
		}
	})

})
