function getFormData(jq) {
	let arrData = jq.serializeArray();
	let mapData = {};

	$.each(arrData, (_, el) => {
		mapData[el["name"]] = el["value"];
	})

	return mapData;
}

$(function () {
	let trainingName = $("#invite-form").data().training;
	let maxInvites = 10;

	$("form#invite-form").submit(function (event) {
		event.preventDefault();

		let formData = getFormData($(this));
		let invites = [];

		for (let i = 0; i < maxInvites; i++) {
			let email = formData[`invite${i}.email`];
			let firstName = formData[`invite${i}.first_name`];

			if (email && firstName) {
				invites.push({ "first_name": firstName, "email": email });
			}
		}

		let payload = {
			"training": trainingName,
			"invites": invites,
		};

		frappe.call({
			method: "engage.api.invite_participants",
			type: "POST",
			args: payload,
			btn: $("#submit-invite"),
			freeze: true,
		}).then(r => {
			if (!r.exc) {
				frappe.msgprint("Users added successfully");
			}
		});
	});
})
