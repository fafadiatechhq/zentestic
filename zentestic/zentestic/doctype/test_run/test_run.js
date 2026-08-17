// Copyright (c) 2026, Fafadia Tech and contributors
// For license information, please see license.txt

function bulk_update_status(frm, status) {
	const grid = frm.fields_dict.test_results?.grid;
	const selected = grid?.get_selected_children() || [];

	if (!selected.length) {
		frappe.msgprint(__("Select one or more Test Results first."));
		return;
	}

	const current_user = frappe.session.user;
	const can_update_all = frappe.user.has_role("System Manager");
	let updated = 0;
	let skipped = 0;

	selected.forEach((row) => {
		if (!can_update_all && row.assignee && row.assignee !== current_user) {
			skipped++;
			return;
		}

		frappe.model.set_value(row.doctype, row.name, "status", status);
		updated++;
	});

	if (!updated) {
		frappe.msgprint(__("No selected results could be updated. You can only update rows assigned to you."));
		return;
	}

	frm.trigger("calculate_progress");

	let message = __("{0} result(s) marked as {1}", [updated, status]);
	if (skipped) {
		message += " " + __("({0} skipped — assigned to another user)", [skipped]);
	}

	frappe.show_alert({ message, indicator: "green" });
}

// Trigger when child Test Result status changes
frappe.ui.form.on("Test Result", {
	status(frm) {
		frm.trigger("calculate_progress");
	},
});

frappe.ui.form.on("Test Run", {
	refresh(frm) {
		frm.trigger("calculate_progress");

		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status === "Completed") {
			frm.add_custom_button(__("Schedule Retest"), function () {
				frappe.call({
					method: "zentestic.zentestic.doctype.test_run.test_run.schedule_retest",
					args: {
						test_run_name: frm.doc.name,
					},
					callback: function (r) {
						if (r.message) {
							frappe.set_route("Form", "Test Run", r.message);
						}
					},
				});
			});
			return;
		}

		const bulk_group = __("Bulk Update");
		frm.add_custom_button(__("Mark Selected as Pass"), () => bulk_update_status(frm, "Pass"), bulk_group);
		frm.add_custom_button(__("Mark Selected as Fail"), () => bulk_update_status(frm, "Fail"), bulk_group);
		frm.add_custom_button(__("Mark Selected as Blocked"), () => bulk_update_status(frm, "Blocked"), bulk_group);
	},

	calculate_progress(frm) {
		let total = frm.doc.test_results ? frm.doc.test_results.length : 0;
		let completed = 0;

		(frm.doc.test_results || []).forEach((row) => {
			if (["Pass", "Fail", "Blocked"].includes(row.status)) {
				completed++;
			}
		});

		let percentage = total ? (completed / total) * 100 : 0;

		frm.set_value("progress", percentage.toFixed(2));

		if (total === 0) {
			frm.set_value("status", "Draft");
		} else if (completed === total) {
			frm.set_value("status", "Completed");
		} else if (completed > 0) {
			frm.set_value("status", "In Progress");
		} else {
			frm.set_value("status", "Draft");
		}
	},
});
