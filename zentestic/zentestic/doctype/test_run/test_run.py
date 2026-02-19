import frappe
from frappe.model.document import Document


class TestRun(Document):
    pass


@frappe.whitelist()
def schedule_retest(test_run_name):

    old_run = frappe.get_doc("Test Run", test_run_name)

    new_run = frappe.new_doc("Test Run")

    # ✅ Mandatory fields
    new_run.test_plan = old_run.test_plan
    new_run.title = f"{old_run.title} - Retest"
    new_run.testing_lead = old_run.testing_lead

    # Optional fields
    new_run.status = "Draft"
    new_run.is_retest = 1
    new_run.retest_of = old_run.name

    new_run.insert()

    # Copy only failed/blocked cases
    for row in old_run.test_results:
        if row.status in ["Fail", "Blocked"]:
            new_run.append("test_results", {
                "test_case": row.test_case,
                "assignee": row.assignee,
                "status": "Pending"
            })

    new_run.save()

    return new_run.name

