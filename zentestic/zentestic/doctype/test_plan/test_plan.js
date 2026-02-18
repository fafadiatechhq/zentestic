// Copyright (c) 2026, Fafadia Tech and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Test Plan", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Test Plan', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Start Test Run', function () {

                // Create new Test Run document
                frappe.new_doc('Test Run', {
                    test_plan: frm.doc.name,
                    project: frm.doc.project,
                    product: frm.doc.product
                }, function (doc) {

                    // Copy Test Cases into Test Run child table
                    frm.doc.test_cases.forEach(function (row) {
                        let child = frappe.model.add_child(doc, "Test Result", "test_results");
                        child.test_case = row.test_case;
                    });

                    frappe.set_route('Form', 'Test Run', doc.name);
                });

            });
        }
    }
});

