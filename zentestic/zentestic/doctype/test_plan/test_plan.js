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
                
                // Ensure fields are pre-poulated
                let case_names = [...new Set(test_cases.map(row => row.test_case).filter(Boolean))];

                frappe.db.get_list('Test Case', {
                    filters: { name: ['in', case_names] },
                    fields: ['name', 'pre_condition', 'steps_to_reproduce', 'expected_result'],
                    limit: case_names.length
                }).then(function (case_docs) {
                    let snapshots = {};
                    (case_docs || []).forEach(function (tc) {
                        snapshots[tc.name] = {
                            pre_condition: tc.pre_condition || '',
                            steps_to_produce: tc.steps_to_reproduce || '',
                            expected_result: tc.expected_result || ''
                        };
                    });

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

                            let snapshot = snapshots[row.test_case] || {};

                            child.test_case = row.test_case;
                            child.assignee = assignee;
                            child.status = "Pending";
                            child.pre_condition = snapshot.pre_condition || '';
                            child.steps_to_produce = snapshot.steps_to_produce || '';
                            child.expected_result = snapshot.expected_result || '';
                        });

                        frappe.set_route('Form', 'Test Run', doc.name);
                    });
                });

            });
        }
    }
});
