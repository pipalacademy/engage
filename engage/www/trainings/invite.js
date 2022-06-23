$(function() {
    let trainingName = $("#invite-form").data().training;

    $("form#invite-form").submit(function(event) {
	event.preventDefault();

	let arrayData = $(this).serializeArray();
	let data = {"training": trainingName}

	$.each(arrayData, (i, nameval) => {
	    data[nameval["name"]] = nameval["value"];
	});

	console.log("data", data);
	console.log("json-data", JSON.stringify(data));

	frappe.call({
	    method: "engage.api.invite_participants",
	    type: "POST",
	    args: data,
	    btn: $("#submit-invite"),
	    freeze: true,
	}).then(r => {
	    console.log(r.message);
	    console.log(JSON.stringify(r.message));

	    if (!r.exc) {
		frappe.msgprint("Users added successfully");
	    }
	});
    });
})
