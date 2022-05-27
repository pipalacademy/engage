// Copyright (c) 2022, Pipal Academy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Problem Repository', {
    refresh: function(frm) {
	frm.add_custom_button(__("Update Problems"), function() {
	    frappe.call(
		{
		    method: "engage.engage.doctype.problem_repository.problem_repository.update_problems",
		    type: "POST",
		    args: {
			"problem_repository_name": frm.doc.name,
		    },
		    freeze: true,
		}).then((data) => {
		    frappe.msgprint(`${data.count} problems added/updated!`);
		})
	});
    }
});
