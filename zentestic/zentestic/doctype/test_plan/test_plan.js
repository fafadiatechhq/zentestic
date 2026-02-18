frappe.ui.form.on('Test Plan', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Start Test Run', function () {

                let test_cases = frm.doc.test_cases || [];
                let participants = frm.doc.participants || [];

                if (test_cases.length === 0) {
                    frappe.msgprint("Please add Test Cases first.");
                    return;
                }

                if (participants.length === 0) {
                    frappe.msgprint("Please add Participants first.");
                    return;
                }

                frappe.new_doc('Test Run', {
                    test_plan: frm.doc.name,
                    project: frm.doc.project,
                    product: frm.doc.product
                }, function (doc) {

                    doc.test_results = [];
                    let users = participants.map(p => p.user);
                    let total = users.length;
                    let strategy = frm.doc.allocation_strategy || "Round Robin";
                    let index = 0;

                    test_cases.forEach(function (row) {

                        let assignee;

                        if (strategy === "Random") {
                            let random_index = Math.floor(Math.random() * total);
                            assignee = users[random_index];
                        } else {
                            assignee = users[index];
                            index = (index + 1) % total;
                        }

                        let child = frappe.model.add_child(
                            doc,
                            "Test Result",
                            "test_results"
                        );

                        child.test_case = row.test_case;
                        child.assignee = assignee;
                        child.status = "Pending";
                    });

                    frappe.set_route('Form', 'Test Run', doc.name);
                });

            });
        }
    }
});
