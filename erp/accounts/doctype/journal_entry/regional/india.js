capkpi.ui.form.on("Journal Entry", {
	refresh: function(frm) {
		frm.set_query('company_address', function(doc) {
			if(!doc.company) {
				capkpi.throw(__('Please set Company'));
			}

			return {
				query: 'capkpi.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Company',
					link_name: doc.company
				}
			};
		});
	}
});
