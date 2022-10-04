// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

capkpi.ui.form.on('Website Theme', {
	validate(frm) {
		let theme_scss = frm.doc.theme_scss;
		if (theme_scss && theme_scss.includes('capkpi/public/scss/website')
			&& !theme_scss.includes('erp/public/scss/website')
		) {
			frm.set_value('theme_scss',
				`${frm.doc.theme_scss}\n@import "erp/public/scss/website";`);
		}
	}
});
