// Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Twitter Settings', {
	onload: function(frm) {
		if (frm.doc.session_status == 'Expired' && frm.doc.consumer_key && frm.doc.consumer_secret){
			capkpi.confirm(
				__('Session not valid, Do you want to login?'),
				function(){
					frm.trigger("login");
				},
				function(){
					window.close();
				}
			);
		}
		frm.dashboard.set_headline(__("For more information, {0}.", [`<a target='_blank' href='https://docs.capkpi.com/docs/user/manual/en/CRM/twitter-settings'>${__('Click here')}</a>`]));
	},
	refresh: function(frm) {
		let msg, color, flag=false;
		if (frm.doc.session_status == "Active") {
			msg = __("Session Active");
			color = 'green';
			flag = true;
		}
		else if(frm.doc.consumer_key && frm.doc.consumer_secret) {
			msg = __("Session Not Active. Save doc to login.");
			color = 'red';
			flag = true;
		}

		if (flag) {
			frm.dashboard.set_headline_alert(
				`<div class="row">
					<div class="col-xs-12">
						<span class="indicator whitespace-nowrap ${color}"><span class="hidden-xs">${msg}</span></span>
					</div>
				</div>`
			);
		}
	},
	login: function(frm) {
		if (frm.doc.consumer_key && frm.doc.consumer_secret){
			capkpi.dom.freeze();
			capkpi.call({
				doc: frm.doc,
				method: "get_authorize_url",
				callback : function(r) {
					window.location.href = r.message;
				}
			}).fail(function() {
				capkpi.dom.unfreeze();
			});
		}
	},
	after_save: function(frm) {
		frm.trigger("login");
	}
});
