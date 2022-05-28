// Copyright (c) 2022, Pipal Academy and contributors
// For license information, please see license.txt

const updateProblemsMethod = "engage.engage.doctype.problem_repository.problem_repository.update_problems";

frappe.ui.form.on('Problem Repository', {
    refresh: function(frm) {
	if (!frm.is_new()) {
	    frm.add_custom_button(__("Update Problems"), function() {
		frappe.call(
		    {
			method: updateProblemsMethod,
			type: "POST",
			args: {
			    problem_repository_name: frm.doc.name,
			},
			freeze: true,
		    }).then((data) => {
			frappe.msgprint(`${data.count} problems added/updated!`);
			frm.refresh();
		    })
	    });
	}
    },
    onload_post_render: function(frm) {
	if (!frm.is_new()) {
	    frm.call("is_update_available")
		.then(data => {
		    let latestCommit = data.message || "";
		    console.log(`latest commit: ${latestCommit}`);
		    if (latestCommit) {
			frappe.msgprint({
			    title: __("Update Available"),
			    indicator: "blue",
			    message: __(`An update to this Problem Repository is available. Use the "Update Problems" button if you wish to update to the latest version <span class="font-weight-light font-italic">(${latestCommit.slice(0, 7)})</span>.`),
			    // primary_action: {
			    //     label: 'Update',
			    //     server_action: updateProblemsMethod + "_as_action",
			    //     args: {
			    //         problem_repository_name: frm.doc.name,
			    //     },
			    //     type: "POST",
			    //     freeze: true,
			    // }
			});
		    }
		})
	}
    }
});
