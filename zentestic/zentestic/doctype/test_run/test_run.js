// Copyright (c) 2026, Fafadia Tech and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Test Run", {
// 	refresh(frm) {

// 	},
// });

// Trigger when child Test Result status changes
frappe.ui.form.on('Test Result', {
    status(frm, cdt, cdn) {
        frm.trigger('calculate_progress');
    }
});

frappe.ui.form.on('Test Run', {

    refresh(frm) {
        frm.trigger('calculate_progress');
         if (frm.doc.status === "Completed" && !frm.is_new()) {

        frm.add_custom_button("Schedule Retest", function () {

            frappe.call({
                method: "zentestic.zentestic.doctype.test_run.test_run.schedule_retest",
                args: {
                    test_run_name: frm.doc.name
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.set_route("Form", "Test Run", r.message);
                    }
                }
            });

        });
    }
    },


    calculate_progress(frm) {

        let total = frm.doc.test_results ? frm.doc.test_results.length : 0;
        let completed = 0;

        (frm.doc.test_results || []).forEach(row => {
            if (["Pass", "Fail", "Blocked"].includes(row.status)) {
                completed++;
            }
        });

        let percentage = total ? (completed / total) * 100 : 0;

        frm.set_value("progress", percentage.toFixed(2));

        // Proper status handling
        if (total === 0) {
            frm.set_value("status", "Draft");
        }
        else if (completed === total) {
            frm.set_value("status", "Completed");
        }
        else if (completed > 0) {
            frm.set_value("status", "In Progress");
        }
        else {
            frm.set_value("status", "Draft");
        }
    }
});
