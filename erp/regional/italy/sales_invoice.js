erp.setup_e_invoice_button = (doctype) => {
	capkpi.ui.form.on(doctype, {
		refresh: (frm) => {
			if(frm.doc.docstatus == 1) {
				frm.add_custom_button('Generate E-Invoice', () => {
					frm.call({
						method: "erp.regional.italy.utils.generate_single_invoice",
						args: {
							docname: frm.doc.name
						},
						callback: function(r) {
							frm.reload_doc();
							if(r.message) {
								open_url_post(capkpi.request.url, {
									cmd: 'capkpi.core.doctype.file.file.download_file',
									file_url: r.message
								});
							}
						}
					});
				});
			}
		}
	});
};
