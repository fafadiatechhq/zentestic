import frappe
from frappe.model.document import Document
import random

from zentestic.zentestic.doctype.test_run.test_run import get_test_case_snapshot


class TestPlan(Document):

	@frappe.whitelist()
	def start_test_run(self):

		# --------------------
		# 1. Basic Validation
		# --------------------
		if not self.test_cases:
			frappe.throw("Please add Test Cases.")

		if not self.participants:
			frappe.throw("Please add Participants.")

		# --------------------
		# 2. Create Test Run
		# --------------------
		test_run = frappe.new_doc("Test Run")
		test_run.test_plan = self.name
		test_run.project = self.project
		test_run.product = self.product
		test_run.status = "In Progress"

		participants = [p.user for p in self.participants]
		total_participants = len(participants)

		# --------------------
		# 3. Apply Strategy
		# --------------------

		if self.allocation_strategy == "Random":
			random.shuffle(participants)

		allocation_index = 0

		for row in self.test_cases:
			assignee = participants[allocation_index]
			snapshot = get_test_case_snapshot(row.test_case)

			test_run.append(
				"test_results",
				{
					"test_case": row.test_case,
					"assignee": assignee,
					"status": "Pending",
					**snapshot,
				},
			)

			# Round Robin rotation
			allocation_index = (allocation_index + 1) % total_participants

		test_run.insert(ignore_permissions=True)

		return test_run.name
