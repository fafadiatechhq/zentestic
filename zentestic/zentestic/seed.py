"""Seed comprehensive Zentestic demo data for local development.

Creates a multi-project graph with users, products, test cases, plans, and
runs that exercise allocation strategies, result statuses, and retests.

Run with:
    bench --site <site> execute zentestic.zentestic.seed.run
    docker compose exec backend bench --site frontend execute zentestic.zentestic.seed.run

Reset and recreate:
    bench --site <site> execute zentestic.zentestic.seed.run --kwargs '{"reset": true}'
"""

from __future__ import annotations

import frappe

# ---------------------------------------------------------------------------
# Seed catalog
# ---------------------------------------------------------------------------

USERS = [
	{
		"email": "qa.lead@zentestic.demo",
		"first_name": "Asha",
		"last_name": "Lead",
	},
	{
		"email": "tester.one@zentestic.demo",
		"first_name": "Ravi",
		"last_name": "Tester",
	},
	{
		"email": "tester.two@zentestic.demo",
		"first_name": "Maya",
		"last_name": "Tester",
	},
	{
		"email": "stakeholder@zentestic.demo",
		"first_name": "Jordan",
		"last_name": "Stakeholder",
	},
]

QA_LEAD = "qa.lead@zentestic.demo"
TESTER_ONE = "tester.one@zentestic.demo"
TESTER_TWO = "tester.two@zentestic.demo"
STAKEHOLDER = "stakeholder@zentestic.demo"

PROJECTS = [
	{
		"project_name": "Zentestic Demo",
		"products": [
			{
				"product": "Billing Portal",
				"test_cases": [
					{
						"title": "Login succeeds with valid credentials",
						"pre_condition": "A registered user exists and the login page is reachable.",
						"steps_to_reproduce": (
							"1. Open the login page\n"
							"2. Enter a valid email and password\n"
							"3. Click Sign In"
						),
						"expected_result": "User is redirected to the dashboard.",
					},
					{
						"title": "Login fails with invalid password",
						"pre_condition": "A registered user exists.",
						"steps_to_reproduce": (
							"1. Open the login page\n"
							"2. Enter a valid email and an incorrect password\n"
							"3. Click Sign In"
						),
						"expected_result": (
							"An error message is shown and the user remains on the login page."
						),
					},
					{
						"title": "Invoice list loads for billing admin",
						"pre_condition": "User is logged in as a billing admin with at least one invoice.",
						"steps_to_reproduce": (
							"1. Navigate to Billing > Invoices\n"
							"2. Wait for the list to load"
						),
						"expected_result": "Invoice rows are displayed with status and amount columns.",
					},
					{
						"title": "Create invoice from customer profile",
						"pre_condition": "User is logged in and a customer record exists.",
						"steps_to_reproduce": (
							"1. Open a customer profile\n"
							"2. Click Create Invoice\n"
							"3. Fill required fields and submit"
						),
						"expected_result": "A new invoice is created and linked to the customer.",
					},
					{
						"title": "Payment webhook marks invoice as paid",
						"pre_condition": "An unpaid invoice exists and the payment provider is configured.",
						"steps_to_reproduce": (
							"1. Trigger a successful payment webhook for the invoice\n"
							"2. Refresh the invoice detail page"
						),
						"expected_result": "Invoice status changes to Paid and payment timestamp is recorded.",
					},
					{
						"title": "Refund request creates credit note",
						"pre_condition": "A paid invoice exists and the user has refund permissions.",
						"steps_to_reproduce": (
							"1. Open a paid invoice\n"
							"2. Click Request Refund\n"
							"3. Confirm the refund amount and submit"
						),
						"expected_result": "A credit note is created and invoice shows Refunded status.",
					},
					{
						"title": "Tax calculation includes GST for IN customers",
						"pre_condition": "Customer country is India and tax rules are configured.",
						"steps_to_reproduce": (
							"1. Create an invoice for an Indian customer\n"
							"2. Add a taxable line item\n"
							"3. Review tax summary"
						),
						"expected_result": "CGST and SGST (or IGST) lines appear with correct rates.",
					},
					{
						"title": "Overdue invoice reminder email is sent",
						"pre_condition": "An invoice is past due and email notifications are enabled.",
						"steps_to_reproduce": (
							"1. Run the overdue invoice reminder job\n"
							"2. Check the customer email inbox / email queue"
						),
						"expected_result": "A reminder email is queued or delivered for the overdue invoice.",
					},
				],
				"plans": [
					{
						"title": "Sprint 1 Smoke",
						"allocation_strategy": "Round Robin",
						"participants": [QA_LEAD, TESTER_ONE, TESTER_TWO],
						"case_titles": [
							"Login succeeds with valid credentials",
							"Login fails with invalid password",
							"Invoice list loads for billing admin",
							"Create invoice from customer profile",
							"Payment webhook marks invoice as paid",
						],
						"runs": [
							{
								"title": "Sprint 1 Run 1",
								"status": "In Progress",
								"testing_lead": QA_LEAD,
								"stakeholders": [STAKEHOLDER, QA_LEAD],
								"results": [
									{
										"title": "Login succeeds with valid credentials",
										"status": "Pass",
										"actual_result": "Redirected to dashboard within 2s.",
									},
									{
										"title": "Login fails with invalid password",
										"status": "Pass",
										"actual_result": "Inline error shown; session not created.",
									},
									{
										"title": "Invoice list loads for billing admin",
										"status": "In progress",
									},
									{
										"title": "Create invoice from customer profile",
										"status": "Pending",
									},
									{
										"title": "Payment webhook marks invoice as paid",
										"status": "Pending",
									},
								],
							},
							{
								"title": "Sprint 1 Run 2 - Completed",
								"status": "Completed",
								"testing_lead": QA_LEAD,
								"stakeholders": [STAKEHOLDER],
								"results": [
									{
										"title": "Login succeeds with valid credentials",
										"status": "Pass",
										"actual_result": "Login successful.",
									},
									{
										"title": "Login fails with invalid password",
										"status": "Pass",
										"actual_result": "Error message displayed.",
									},
									{
										"title": "Invoice list loads for billing admin",
										"status": "Fail",
										"actual_result": "List spinner never resolves; API returns 500.",
									},
									{
										"title": "Create invoice from customer profile",
										"status": "Blocked",
										"actual_result": "Create Invoice button disabled for this role.",
									},
									{
										"title": "Payment webhook marks invoice as paid",
										"status": "Pass",
										"actual_result": "Status flipped to Paid after webhook.",
									},
								],
								"retest": {
									"title": "Sprint 1 Run 2 - Retest",
									"status": "Draft",
									"testing_lead": QA_LEAD,
									"stakeholders": [STAKEHOLDER, QA_LEAD],
								},
							},
						],
					},
					{
						"title": "Billing Regression",
						"allocation_strategy": "Random",
						"participants": [TESTER_ONE, TESTER_TWO],
						"case_titles": [
							"Refund request creates credit note",
							"Tax calculation includes GST for IN customers",
							"Overdue invoice reminder email is sent",
							"Payment webhook marks invoice as paid",
						],
						"runs": [
							{
								"title": "Billing Regression Draft",
								"status": "Draft",
								"testing_lead": TESTER_ONE,
								"stakeholders": [QA_LEAD],
								"results": [
									{
										"title": "Refund request creates credit note",
										"status": "Pending",
									},
									{
										"title": "Tax calculation includes GST for IN customers",
										"status": "Pending",
									},
									{
										"title": "Overdue invoice reminder email is sent",
										"status": "Pending",
									},
									{
										"title": "Payment webhook marks invoice as paid",
										"status": "Retest",
										"actual_result": "Carried over from previous cycle.",
									},
								],
							}
						],
					},
				],
			},
			{
				"product": "Customer Portal",
				"test_cases": [
					{
						"title": "Customer can update profile details",
						"pre_condition": "Customer is logged into the portal.",
						"steps_to_reproduce": (
							"1. Open Profile settings\n"
							"2. Update phone number and address\n"
							"3. Save changes"
						),
						"expected_result": "Success toast appears and updated values persist after refresh.",
					},
					{
						"title": "Password reset email is delivered",
						"pre_condition": "A verified customer email exists.",
						"steps_to_reproduce": (
							"1. Open Forgot Password\n"
							"2. Enter the customer email\n"
							"3. Submit the form"
						),
						"expected_result": "Reset email is queued and contains a valid one-time link.",
					},
					{
						"title": "Download invoice PDF",
						"pre_condition": "Customer has at least one paid invoice.",
						"steps_to_reproduce": (
							"1. Open Invoices\n"
							"2. Click Download PDF on a paid invoice"
						),
						"expected_result": "A PDF downloads and matches invoice totals.",
					},
					{
						"title": "Support ticket creation from portal",
						"pre_condition": "Customer is logged in.",
						"steps_to_reproduce": (
							"1. Navigate to Support\n"
							"2. Fill subject and description\n"
							"3. Submit ticket"
						),
						"expected_result": "Ticket is created with Open status and confirmation shown.",
					},
				],
				"plans": [
					{
						"title": "Portal UAT",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_TWO, QA_LEAD],
						"case_titles": [
							"Customer can update profile details",
							"Password reset email is delivered",
							"Download invoice PDF",
							"Support ticket creation from portal",
						],
						"runs": [
							{
								"title": "Portal UAT Cycle 1",
								"status": "In Progress",
								"testing_lead": TESTER_TWO,
								"stakeholders": [STAKEHOLDER],
								"results": [
									{
										"title": "Customer can update profile details",
										"status": "Pass",
										"actual_result": "Profile saved successfully.",
									},
									{
										"title": "Password reset email is delivered",
										"status": "Fail",
										"actual_result": "Email not received within 5 minutes.",
									},
									{
										"title": "Download invoice PDF",
										"status": "Blocked",
										"actual_result": "PDF service unavailable in staging.",
									},
									{
										"title": "Support ticket creation from portal",
										"status": "In progress",
									},
								],
							}
						],
					}
				],
			},
		],
	},
	{
		"project_name": "Mobile App QA",
		"products": [
			{
				"product": "iOS Companion App",
				"test_cases": [
					{
						"title": "Push notification opens deep link",
						"pre_condition": "App is installed and notifications are allowed.",
						"steps_to_reproduce": (
							"1. Send a campaign push with a deep link\n"
							"2. Tap the notification"
						),
						"expected_result": "App opens the correct in-app screen.",
					},
					{
						"title": "Offline invoice list shows cached data",
						"pre_condition": "User previously loaded invoices while online.",
						"steps_to_reproduce": (
							"1. Enable airplane mode\n"
							"2. Open Invoices"
						),
						"expected_result": "Cached invoices display with an offline banner.",
					},
					{
						"title": "Biometric unlock returns to last screen",
						"pre_condition": "Biometric unlock is enabled.",
						"steps_to_reproduce": (
							"1. Background the app for 2 minutes\n"
							"2. Foreground and authenticate with biometrics"
						),
						"expected_result": "User lands on the previously active screen.",
					},
				],
				"plans": [
					{
						"title": "iOS Smoke",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_ONE, TESTER_TWO],
						"case_titles": [
							"Push notification opens deep link",
							"Offline invoice list shows cached data",
							"Biometric unlock returns to last screen",
						],
						"runs": [
							{
								"title": "iOS Smoke Build 42",
								"status": "Completed",
								"testing_lead": TESTER_ONE,
								"stakeholders": [QA_LEAD, STAKEHOLDER],
								"results": [
									{
										"title": "Push notification opens deep link",
										"status": "Pass",
										"actual_result": "Deep link resolved to invoice detail.",
									},
									{
										"title": "Offline invoice list shows cached data",
										"status": "Pass",
										"actual_result": "Cached rows and offline banner shown.",
									},
									{
										"title": "Biometric unlock returns to last screen",
										"status": "Pass",
										"actual_result": "Returned to Settings after Face ID.",
									},
								],
							}
						],
					}
				],
			}
		],
	},
]


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def run(reset: bool | str = False):
	"""Create a comprehensive Project → Product → Plan → Run graph."""
	reset = _as_bool(reset)

	if reset:
		_clear_seed_data()

	users = [_ensure_user(spec) for spec in USERS]
	summary = {"users": [u.name for u in users], "projects": []}

	for project_spec in PROJECTS:
		project = _ensure_project(project_spec["project_name"])
		project_summary = {
			"project": project.name,
			"project_name": project.project_name,
			"products": [],
		}

		for product_spec in project_spec["products"]:
			product = _ensure_product(project.name, product_spec["product"])
			cases_by_title = {}
			for case_spec in product_spec["test_cases"]:
				tc = _ensure_test_case(project.name, product.name, case_spec)
				cases_by_title[case_spec["title"]] = tc

			product_summary = {
				"product": product.name,
				"product_label": product.product,
				"test_cases": [tc.name for tc in cases_by_title.values()],
				"plans": [],
			}

			for plan_spec in product_spec["plans"]:
				selected = [cases_by_title[title] for title in plan_spec["case_titles"]]
				plan = _ensure_test_plan(project.name, product.name, plan_spec, selected)
				plan_summary = {
					"test_plan": plan.name,
					"title": plan.title,
					"runs": [],
				}

				for run_spec in plan_spec["runs"]:
					test_run = _ensure_test_run(plan, run_spec, cases_by_title)
					run_summary = {
						"test_run": test_run.name,
						"title": test_run.title,
						"status": test_run.status,
					}

					retest_spec = run_spec.get("retest")
					if retest_spec:
						retest = _ensure_retest_run(plan, test_run, retest_spec)
						run_summary["retest"] = {
							"test_run": retest.name,
							"title": retest.title,
							"status": retest.status,
						}

					plan_summary["runs"].append(run_summary)

				product_summary["plans"].append(plan_summary)

			project_summary["products"].append(product_summary)

		summary["projects"].append(project_summary)

	frappe.db.commit()
	print(frappe.as_json(summary, indent=2))
	return summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _as_bool(value) -> bool:
	if isinstance(value, bool):
		return value
	if value is None:
		return False
	return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _completed_statuses():
	return {"Pass", "Fail", "Blocked"}


def _progress_for(results: list[dict]) -> float:
	if not results:
		return 0.0
	done = sum(1 for row in results if row.get("status") in _completed_statuses())
	return round(100.0 * done / len(results), 2)


def _snapshot_fields(test_case) -> dict:
	return {
		"pre_condition": test_case.pre_condition or "",
		"steps_to_produce": test_case.steps_to_reproduce or "",
		"expected_result": test_case.expected_result or "",
	}


def _ensure_user(spec: dict):
	email = spec["email"]
	if frappe.db.exists("User", email):
		return frappe.get_doc("User", email)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": spec["first_name"],
			"last_name": spec["last_name"],
			"send_welcome_email": 0,
			"user_type": "System User",
		}
	)
	user.insert(ignore_permissions=True)
	user.add_roles("System Manager")
	return user


def _ensure_project(project_name: str):
	existing = frappe.db.get_value("Project", {"project_name": project_name}, "name")
	if existing:
		return frappe.get_doc("Project", existing)

	return frappe.get_doc(
		{
			"doctype": "Project",
			"project_name": project_name,
		}
	).insert(ignore_permissions=True)


def _ensure_product(project: str, product_label: str):
	existing = frappe.db.get_value(
		"Product", {"product": product_label, "project": project}, "name"
	)
	if existing:
		return frappe.get_doc("Product", existing)

	return frappe.get_doc(
		{
			"doctype": "Product",
			"product": product_label,
			"project": project,
		}
	).insert(ignore_permissions=True)


def _ensure_test_case(project: str, product: str, spec: dict):
	existing = frappe.db.get_value(
		"Test Case",
		{"title": spec["title"], "product": product, "project": project},
		"name",
	)
	if existing:
		return frappe.get_doc("Test Case", existing)

	return frappe.get_doc(
		{
			"doctype": "Test Case",
			"title": spec["title"],
			"project": project,
			"product": product,
			"pre_condition": spec.get("pre_condition"),
			"steps_to_reproduce": spec.get("steps_to_reproduce"),
			"expected_result": spec.get("expected_result"),
		}
	).insert(ignore_permissions=True)


def _ensure_test_plan(project: str, product: str, plan_spec: dict, test_cases: list):
	existing = frappe.db.get_value(
		"Test Plan",
		{"title": plan_spec["title"], "product": product, "project": project},
		"name",
	)
	if existing:
		return frappe.get_doc("Test Plan", existing)

	return frappe.get_doc(
		{
			"doctype": "Test Plan",
			"title": plan_spec["title"],
			"project": project,
			"product": product,
			"allocation_strategy": plan_spec["allocation_strategy"],
			"test_cases": [{"test_case": tc.name} for tc in test_cases],
			"participants": [{"user": user} for user in plan_spec["participants"]],
		}
	).insert(ignore_permissions=True)


def _build_result_rows(plan, run_spec: dict, cases_by_title: dict) -> list[dict]:
	participants = [row.user for row in plan.participants] or ["Administrator"]
	rows = []
	for index, result_spec in enumerate(run_spec["results"]):
		test_case = cases_by_title[result_spec["title"]]
		assignee = result_spec.get("assignee") or participants[index % len(participants)]
		row = {
			"test_case": test_case.name,
			"assignee": assignee,
			"status": result_spec["status"],
			**_snapshot_fields(test_case),
		}
		if result_spec.get("actual_result"):
			row["actual_result"] = result_spec["actual_result"]
		rows.append(row)
	return rows


def _ensure_test_run(plan, run_spec: dict, cases_by_title: dict):
	existing = frappe.db.get_value(
		"Test Run", {"title": run_spec["title"], "test_plan": plan.name}, "name"
	)
	if existing:
		return frappe.get_doc("Test Run", existing)

	result_rows = _build_result_rows(plan, run_spec, cases_by_title)
	desired_status = run_spec["status"]
	# Avoid Test Run.validate Telegram side-effect on Completed inserts.
	insert_status = "In Progress" if desired_status == "Completed" else desired_status

	doc = frappe.get_doc(
		{
			"doctype": "Test Run",
			"title": run_spec["title"],
			"test_plan": plan.name,
			"testing_lead": run_spec.get("testing_lead") or "Administrator",
			"status": insert_status,
			"test_results": result_rows,
			"stakeholders": [
				{"user": user} for user in run_spec.get("stakeholders", [])
			],
		}
	).insert(ignore_permissions=True)

	progress = _progress_for(result_rows)
	updates = {"progress": progress}
	if desired_status == "Completed":
		updates["status"] = "Completed"
	doc.db_set(updates, update_modified=False)
	doc.reload()
	return doc


def _ensure_retest_run(plan, source_run, retest_spec: dict):
	existing = frappe.db.get_value(
		"Test Run", {"title": retest_spec["title"], "test_plan": plan.name}, "name"
	)
	if existing:
		return frappe.get_doc("Test Run", existing)

	carry_forward = []
	for row in source_run.test_results:
		if row.status in {"Fail", "Blocked"}:
			carry_forward.append(
				{
					"test_case": row.test_case,
					"assignee": row.assignee,
					"status": "Pending",
					"pre_condition": row.pre_condition,
					"steps_to_produce": row.steps_to_produce,
					"expected_result": row.expected_result,
				}
			)

	doc = frappe.get_doc(
		{
			"doctype": "Test Run",
			"title": retest_spec["title"],
			"test_plan": plan.name,
			"testing_lead": retest_spec.get("testing_lead") or source_run.testing_lead,
			"status": retest_spec.get("status") or "Draft",
			"is_retest": 1,
			"retest_of": source_run.name,
			"test_results": carry_forward,
			"stakeholders": [
				{"user": user}
				for user in retest_spec.get("stakeholders", [STAKEHOLDER])
			],
		}
	).insert(ignore_permissions=True)

	doc.db_set("progress", _progress_for(carry_forward), update_modified=False)
	doc.reload()
	return doc


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def _all_plan_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for plan in product["plans"]:
				titles.append(plan["title"])
	return titles


def _all_run_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for plan in product["plans"]:
				for run in plan["runs"]:
					titles.append(run["title"])
					if run.get("retest"):
						titles.append(run["retest"]["title"])
	return titles


def _all_case_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for case in product["test_cases"]:
				titles.append(case["title"])
	return titles


def _all_product_labels() -> list[str]:
	return [
		product["product"]
		for project in PROJECTS
		for product in project["products"]
	]


def _all_project_names() -> list[str]:
	return [project["project_name"] for project in PROJECTS]


def _delete_docs(doctype: str, names: list[str]):
	for name in names:
		if name and frappe.db.exists(doctype, name):
			frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)


def _clear_seed_data():
	"""Delete previously seeded docs in reverse dependency order."""
	# Test Runs (including retests) linked to seeded plans / titles
	run_names = set()
	for title in _all_run_titles():
		run_names.update(frappe.get_all("Test Run", filters={"title": title}, pluck="name"))

	for plan_title in _all_plan_titles():
		for plan_name in frappe.get_all("Test Plan", filters={"title": plan_title}, pluck="name"):
			run_names.update(
				frappe.get_all("Test Run", filters={"test_plan": plan_name}, pluck="name")
			)

	_delete_docs("Test Run", sorted(run_names))

	for plan_title in _all_plan_titles():
		_delete_docs(
			"Test Plan",
			frappe.get_all("Test Plan", filters={"title": plan_title}, pluck="name"),
		)

	for product_label in _all_product_labels():
		product_names = frappe.get_all(
			"Product", filters={"product": product_label}, pluck="name"
		)
		for product_name in product_names:
			for title in _all_case_titles():
				_delete_docs(
					"Test Case",
					frappe.get_all(
						"Test Case",
						filters={"title": title, "product": product_name},
						pluck="name",
					),
				)
			_delete_docs("Product", [product_name])

	for project_name in _all_project_names():
		name = frappe.db.get_value("Project", {"project_name": project_name}, "name")
		if name:
			frappe.delete_doc("Project", name, ignore_permissions=True, force=True)

	# Demo users are left in place so re-seed stays fast and login-friendly.
