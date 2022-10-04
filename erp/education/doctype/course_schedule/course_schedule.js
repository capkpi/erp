capkpi.provide("education");

cur_frm.add_fetch("student_group", "course", "course")
capkpi.ui.form.on("Course Schedule", {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Mark Attendance"), function() {
				capkpi.route_options = {
					based_on: "Course Schedule",
					course_schedule: frm.doc.name
				}
				capkpi.set_route("Form", "Student Attendance Tool");
			}).addClass("btn-primary");
		}
	}
});
