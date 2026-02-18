import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import random

class TestPlan(Document):

    @frappe.whitelist()
    def start_test_run(self):

        # --------------------
        # 1️⃣ Basic Validation
        # --------------------
        if not self.test_cases:
            frappe.throw("Please add Test Cases.")

        if not self.participants:
            frappe.throw("Please add Participants.")

        # --------------------
        # 2️⃣ Create Test Run
        # --------------------
        test_run = frappe.new_doc("Test Run")
        test_run.test_plan = self.name
        test_run.project = self.project
        test_run.product = self.product
        test_run.status = "In Progress"
        test_run.insert(ignore_permissions=True)

        participants = [p.user for p in self.participants]
        total_participants = len(participants)

        # --------------------
        # 3️⃣ Apply Strategy
        # --------------------

        if self.allocation_strategy == "Random":
            random.shuffle(participants)

        allocation_index = 0

        for row in self.test_cases:

            assignee = participants[allocation_index]

            frappe.get_doc({
                "doctype": "Test Result",
                "title": row.test_case,
                "test_run": test_run.name,
                "test_case": row.test_case,
                "assignee": assignee,
                "status": "Pending"
            }).insert(ignore_permissions=True)

            # Round Robin rotation
            allocation_index = (allocation_index + 1) % total_participants

        return test_run.name