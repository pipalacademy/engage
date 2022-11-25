// Copyright (c) 2022, Pipal Academy and contributors
// For license information, please see license.txt

const jhubCreateUser = "engage.engage.doctype.training.training.create_jupyterhub_user";

let someForm;

frappe.ui.form.on('Training', {
  refresh: function(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Create JupyterHub User"), function() {
        let d = new frappe.ui.Dialog({
          title: 'Enter details',
          fields: [
            {
              label: 'JupyterHub Username',
              fieldname: 'jh_username',
              fieldtype: 'Data'
            },
            {
              label: 'JupyterHub Password',
              fieldname: 'jh_password',
              fieldtype: 'Data'
            },
            {
              label: 'Select Participant',
              fieldname: 'participant_name',
              fieldtype: 'Select',
              options: frm.doc.participants.map(p => {return {value: p.name, label: p.user}})
            },
          ],
          primary_action_label: 'Submit',
          primary_action(values) {
            frappe.call(
              {
                method: jhubCreateUser,
                type: "POST",
                args: {
                  training_name: frm.doc.name,
                  participant_name: values.participant_name,
                  jh_username: values.jh_username,
                  jh_password: values.jh_password,
                },
                freeze: true,
              }).then((data) => {
                if (data.ok) {
                  frappe.msgprint("User added to JupyterHub.");
                  frm.refresh();
                } else {
                  frappe.msgprint({title: "Something went wrong", indicator: "red", message: data.message})
                }
              });
            d.hide();
          }
        });

        d.show();
      });
    }
  },
});
