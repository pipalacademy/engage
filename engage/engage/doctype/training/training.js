// Copyright (c) 2022, Pipal Academy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training', {
  // refresh: function(frm) {
    // below code adds current user as a trainer and participant by default
    // 
    // if (frm.is_new()) {
    //   let default_participant = frm.add_child('participants', {
    //     user: frappe.session.user
    //   });

    //   let default_trainer = frm.add_child('trainers', {
    //     user: frappe.session.user
    //   });

    //   frm.refresh_field('participants');
    //   frm.refresh_field('trainers');
    // }
  // }
});

// frappe.ui.form.on('Training Trainer', {
//   trainers_add: function(frm, cdt, cdn) {
//     // when a trainer is added, make an entry for the trainer in the participants table too
//     // cdt is child doctype, cdn is child docname
// 
//     frappe.db.get_doc(cdt, cdn)
//       .then(trainer => {
// 	frm.add_child('participants', {
// 	  user: trainer.user,
// 	})
// 
// 	frm.refresh_field('participants');
//       });
//   }
// });
