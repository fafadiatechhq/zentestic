"""Seed comprehensive Zentestic demo data for local development.

Creates a multi-project graph with users, products, test cases, plans, and
runs that exercise allocation strategies, result statuses, retests, and
common edge cases (unplanned cases, plans with no runs, chained retests).

Run with:
    bench --site <site> execute zentestic.zentestic.seed.run
    docker compose exec backend bench --site frontend execute zentestic.zentestic.seed.run

Reset and recreate:
    bench --site <site> execute zentestic.zentestic.seed.run --kwargs '{"reset": true}'
"""

from __future__ import annotations

import frappe

# ---------------------------------------------------------------------------
# Catalog helpers
# ---------------------------------------------------------------------------


def _steps(*lines: str) -> str:
	return "\n".join(f"{index}. {line}" for index, line in enumerate(lines, start=1))


def _tc(title: str, pre: str = "", steps: str = "", expected: str = "") -> dict:
	return {
		"title": title,
		"pre_condition": pre,
		"steps_to_reproduce": steps,
		"expected_result": expected,
	}


def _res(title: str, status: str, actual: str | None = None, assignee: str | None = None) -> dict:
	row = {"title": title, "status": status}
	if actual:
		row["actual_result"] = actual
	if assignee:
		row["assignee"] = assignee
	return row


# ---------------------------------------------------------------------------
# Seed catalog
# ---------------------------------------------------------------------------

USERS = [
	{"email": "qa.lead@zentestic.demo", "first_name": "Asha", "last_name": "Lead"},
	{"email": "tester.one@zentestic.demo", "first_name": "Ravi", "last_name": "Tester"},
	{"email": "tester.two@zentestic.demo", "first_name": "Maya", "last_name": "Tester"},
	{"email": "tester.three@zentestic.demo", "first_name": "Priya", "last_name": "Tester"},
	{"email": "tester.android@zentestic.demo", "first_name": "Ken", "last_name": "Mobile"},
	{"email": "stakeholder@zentestic.demo", "first_name": "Jordan", "last_name": "Stakeholder"},
	{"email": "product.owner@zentestic.demo", "first_name": "Sam", "last_name": "Owner"},
]

QA_LEAD = "qa.lead@zentestic.demo"
TESTER_ONE = "tester.one@zentestic.demo"
TESTER_TWO = "tester.two@zentestic.demo"
TESTER_THREE = "tester.three@zentestic.demo"
TESTER_ANDROID = "tester.android@zentestic.demo"
STAKEHOLDER = "stakeholder@zentestic.demo"
PRODUCT_OWNER = "product.owner@zentestic.demo"

PROJECTS = [
	{
		"project_name": "Zentestic Demo",
		"products": [
			{
				"product": "Billing Portal",
				"test_cases": [
					_tc(
						"Login succeeds with valid credentials",
						pre="A registered user exists and the login page is reachable.",
						steps=_steps(
							"Open the login page",
							"Enter a valid email and password",
							"Click Sign In",
						),
						expected="User is redirected to the dashboard.",
					),
					_tc(
						"Login fails with invalid password",
						pre="A registered user exists.",
						steps=_steps(
							"Open the login page",
							"Enter a valid email and an incorrect password",
							"Click Sign In",
						),
						expected="An error message is shown and the user remains on the login page.",
					),
					_tc(
						"Invoice list loads for billing admin",
						pre="User is logged in as a billing admin with at least one invoice.",
						steps=_steps("Navigate to Billing > Invoices", "Wait for the list to load"),
						expected="Invoice rows are displayed with status and amount columns.",
					),
					_tc(
						"Create invoice from customer profile",
						pre="User is logged in and a customer record exists.",
						steps=_steps(
							"Open a customer profile",
							"Click Create Invoice",
							"Fill required fields and submit",
						),
						expected="A new invoice is created and linked to the customer.",
					),
					_tc(
						"Payment webhook marks invoice as paid",
						pre="An unpaid invoice exists and the payment provider is configured.",
						steps=_steps(
							"Trigger a successful payment webhook for the invoice",
							"Refresh the invoice detail page",
						),
						expected="Invoice status changes to Paid and payment timestamp is recorded.",
					),
					_tc(
						"Refund request creates credit note",
						pre="A paid invoice exists and the user has refund permissions.",
						steps=_steps(
							"Open a paid invoice",
							"Click Request Refund",
							"Confirm the refund amount and submit",
						),
						expected="A credit note is created and invoice shows Refunded status.",
					),
					_tc(
						"Tax calculation includes GST for IN customers",
						pre="Customer country is India and tax rules are configured.",
						steps=_steps(
							"Create an invoice for an Indian customer",
							"Add a taxable line item",
							"Review tax summary",
						),
						expected="CGST and SGST (or IGST) lines appear with correct rates.",
					),
					_tc(
						"Overdue invoice reminder email is sent",
						pre="An invoice is past due and email notifications are enabled.",
						steps=_steps(
							"Run the overdue invoice reminder job",
							"Check the customer email inbox / email queue",
						),
						expected="A reminder email is queued or delivered for the overdue invoice.",
					),
					_tc(
						"Recurring invoice generates on schedule",
						pre="A customer has an active monthly subscription.",
						steps=_steps(
							"Advance the scheduler clock to the next billing date",
							"Open the customer invoice list",
						),
						expected="A new draft invoice is created with the recurring line items.",
					),
					_tc(
						"Discount code applies to invoice total",
						pre="A valid percentage discount code exists.",
						steps=_steps(
							"Create an invoice",
							"Apply the discount code",
							"Review totals",
						),
						expected="Discount line is shown and grand total is reduced by the correct amount.",
					),
					_tc(
						"Partial payment updates remaining balance",
						pre="An unpaid invoice of 1000 exists.",
						steps=_steps(
							"Record a payment of 400 against the invoice",
							"Refresh invoice detail",
						),
						expected="Paid amount is 400 and remaining balance is 600 with status Partially Paid.",
					),
					_tc(
						"Export invoices to CSV",
						pre="At least three invoices exist in the current filter.",
						steps=_steps(
							"Open Billing > Invoices",
							"Apply a date filter",
							"Click Export CSV",
						),
						expected="A CSV downloads with one row per invoice matching the filter.",
					),
					_tc(
						"Void draft invoice",
						pre="A draft invoice exists.",
						steps=_steps("Open the draft invoice", "Click Void", "Confirm"),
						expected="Invoice status becomes Void and it cannot be sent or paid.",
					),
					_tc(
						"Multi-currency invoice conversion",
						pre="Customer currency is EUR and base currency is USD.",
						steps=_steps(
							"Create an invoice in EUR",
							"Add a line item",
							"Review converted totals",
						),
						expected="EUR amounts display with a USD equivalent using the configured rate.",
					),
					_tc(
						"Dunning escalation after 30 days",
						pre="An invoice has been overdue for 30 days and dunning is enabled.",
						steps=_steps(
							"Run the dunning job",
							"Open the invoice activity timeline",
						),
						expected="A second-level dunning notice is recorded and emailed.",
					),
					_tc("Ad-hoc billing sanity check"),
					_tc(
						"Archive paid invoice older than 7 years",
						pre="A paid invoice with issue date older than 7 years exists.",
						steps=_steps(
							"Open retention settings",
							"Run archive job",
							"Search for the old invoice",
						),
						expected="Invoice is archived and no longer appears in the default list.",
					),
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
									_res(
										"Login succeeds with valid credentials",
										"Pass",
										"Redirected to dashboard within 2s.",
									),
									_res(
										"Login fails with invalid password",
										"Pass",
										"Inline error shown; session not created.",
									),
									_res("Invoice list loads for billing admin", "In progress"),
									_res("Create invoice from customer profile", "Pending"),
									_res("Payment webhook marks invoice as paid", "Pending"),
								],
							},
							{
								"title": "Sprint 1 Run 2 - Completed",
								"status": "Completed",
								"testing_lead": QA_LEAD,
								"stakeholders": [STAKEHOLDER],
								"results": [
									_res("Login succeeds with valid credentials", "Pass", "Login successful."),
									_res(
										"Login fails with invalid password",
										"Pass",
										"Error message displayed.",
									),
									_res(
										"Invoice list loads for billing admin",
										"Fail",
										"List spinner never resolves; API returns 500.",
									),
									_res(
										"Create invoice from customer profile",
										"Blocked",
										"Create Invoice button disabled for this role.",
									),
									_res(
										"Payment webhook marks invoice as paid",
										"Pass",
										"Status flipped to Paid after webhook.",
									),
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
									_res("Refund request creates credit note", "Pending"),
									_res("Tax calculation includes GST for IN customers", "Pending"),
									_res("Overdue invoice reminder email is sent", "Pending"),
									_res(
										"Payment webhook marks invoice as paid",
										"Retest",
										"Carried over from previous cycle.",
									),
								],
							}
						],
					},
					{
						"title": "Billing Full Cycle",
						"allocation_strategy": "Round Robin",
						"participants": [QA_LEAD, TESTER_ONE, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Recurring invoice generates on schedule",
							"Discount code applies to invoice total",
							"Partial payment updates remaining balance",
							"Export invoices to CSV",
							"Void draft invoice",
							"Multi-currency invoice conversion",
							"Dunning escalation after 30 days",
							"Ad-hoc billing sanity check",
						],
						"runs": [
							{
								"title": "Billing Nightly 2026-08-01",
								"status": "Completed",
								"testing_lead": QA_LEAD,
								"stakeholders": [STAKEHOLDER, PRODUCT_OWNER],
								"results": [
									_res(
										"Recurring invoice generates on schedule",
										"Pass",
										"Draft invoice created at 00:05 UTC.",
										assignee=TESTER_ONE,
									),
									_res(
										"Discount code applies to invoice total",
										"Fail",
										"10% code only reduced tax, not subtotal.",
										assignee=TESTER_TWO,
									),
									_res(
										"Partial payment updates remaining balance",
										"Fail",
										"Balance stayed at 1000 after 400 payment.",
										assignee=TESTER_THREE,
									),
									_res(
										"Export invoices to CSV",
										"Blocked",
										"Export endpoint returns 403 in staging.",
										assignee=QA_LEAD,
									),
									_res(
										"Void draft invoice",
										"Pass",
										"Voided invoice locked correctly.",
										assignee=TESTER_ONE,
									),
									_res(
										"Multi-currency invoice conversion",
										"Fail",
										"USD equivalent used stale FX rate from previous day.",
										assignee=TESTER_TWO,
									),
									_res(
										"Dunning escalation after 30 days",
										"Pass",
										"Level-2 notice queued.",
										assignee=TESTER_THREE,
									),
									_res(
										"Ad-hoc billing sanity check",
										"Pass",
										"Dashboard totals match invoice list.",
										assignee=QA_LEAD,
									),
								],
								"retest": {
									"title": "Billing Nightly 2026-08-01 - Retest",
									"status": "Completed",
									"testing_lead": QA_LEAD,
									"stakeholders": [STAKEHOLDER, PRODUCT_OWNER],
									"results": [
										_res(
											"Discount code applies to invoice total",
											"Pass",
											"Subtotal and tax both discounted.",
										),
										_res(
											"Partial payment updates remaining balance",
											"Fail",
											"Remaining balance still incorrect after hotfix.",
										),
										_res(
											"Export invoices to CSV",
											"Pass",
											"CSV download works after permission fix.",
										),
										_res(
											"Multi-currency invoice conversion",
											"Blocked",
											"FX service outage in EU region.",
										),
									],
									"retest": {
										"title": "Billing Nightly 2026-08-01 - Retest 2",
										"status": "Draft",
										"testing_lead": TESTER_TWO,
										"stakeholders": [QA_LEAD, PRODUCT_OWNER],
									},
								},
							},
							{
								"title": "Billing Nightly 2026-08-08",
								"status": "In Progress",
								"testing_lead": TESTER_THREE,
								"stakeholders": [QA_LEAD],
								"results": [
									_res(
										"Recurring invoice generates on schedule",
										"Pass",
										"Generated on schedule.",
									),
									_res("Discount code applies to invoice total", "Pass", "Totals correct."),
									_res("Partial payment updates remaining balance", "In progress"),
									_res("Export invoices to CSV", "Pending"),
									_res("Void draft invoice", "Pending"),
									_res("Multi-currency invoice conversion", "Pending"),
									_res("Dunning escalation after 30 days", "Pending"),
									_res("Ad-hoc billing sanity check", "Pending"),
								],
							},
						],
					},
					{
						"title": "Billing Exploratory",
						"allocation_strategy": "Random",
						"participants": [TESTER_ONE],
						"case_titles": [
							"Archive paid invoice older than 7 years",
							"Ad-hoc billing sanity check",
							"Void draft invoice",
						],
					},
				],
			},
			{
				"product": "Customer Portal",
				"test_cases": [
					_tc(
						"Customer can update profile details",
						pre="Customer is logged into the portal.",
						steps=_steps(
							"Open Profile settings",
							"Update phone number and address",
							"Save changes",
						),
						expected="Success toast appears and updated values persist after refresh.",
					),
					_tc(
						"Password reset email is delivered",
						pre="A verified customer email exists.",
						steps=_steps(
							"Open Forgot Password",
							"Enter the customer email",
							"Submit the form",
						),
						expected="Reset email is queued and contains a valid one-time link.",
					),
					_tc(
						"Download invoice PDF",
						pre="Customer has at least one paid invoice.",
						steps=_steps("Open Invoices", "Click Download PDF on a paid invoice"),
						expected="A PDF downloads and matches invoice totals.",
					),
					_tc(
						"Support ticket creation from portal",
						pre="Customer is logged in.",
						steps=_steps(
							"Navigate to Support",
							"Fill subject and description",
							"Submit ticket",
						),
						expected="Ticket is created with Open status and confirmation shown.",
					),
					_tc(
						"SSO login with Google",
						pre="Customer Google account is linked.",
						steps=_steps("Open portal login", "Click Continue with Google", "Approve consent"),
						expected="Customer is signed in and landed on the dashboard.",
					),
					_tc(
						"Invoice filter by date range",
						pre="Customer has invoices in at least two months.",
						steps=_steps(
							"Open Invoices",
							"Set From and To dates to last month",
							"Apply filter",
						),
						expected="Only invoices in the selected range are listed.",
					),
					_tc(
						"Dark mode persists after refresh",
						pre="Customer is logged in.",
						steps=_steps("Toggle dark mode on", "Refresh the browser", "Check theme"),
						expected="Dark mode remains active after reload.",
					),
					_tc(
						"Session timeout redirects to login",
						pre="Idle timeout is configured to 15 minutes.",
						steps=_steps("Stay idle past the timeout", "Click any navigation item"),
						expected="User is redirected to login with a session-expired message.",
					),
					_tc(
						"Change notification language",
						pre="Customer profile language is English.",
						steps=_steps(
							"Open Notification preferences",
							"Switch language to Spanish",
							"Save",
						),
						expected="Preference saves and subsequent emails use Spanish templates.",
					),
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
									_res(
										"Customer can update profile details",
										"Pass",
										"Profile saved successfully.",
									),
									_res(
										"Password reset email is delivered",
										"Fail",
										"Email not received within 5 minutes.",
									),
									_res(
										"Download invoice PDF",
										"Blocked",
										"PDF service unavailable in staging.",
									),
									_res("Support ticket creation from portal", "In progress"),
								],
							}
						],
					},
					{
						"title": "Portal Accessibility",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Dark mode persists after refresh",
							"Invoice filter by date range",
							"Session timeout redirects to login",
						],
						"runs": [
							{
								"title": "Portal A11y Draft",
								"status": "Draft",
								"testing_lead": TESTER_TWO,
								"stakeholders": [PRODUCT_OWNER],
								"results": [
									_res("Dark mode persists after refresh", "Pending"),
									_res("Invoice filter by date range", "Pending"),
									_res("Session timeout redirects to login", "Pending"),
								],
							}
						],
					},
					{
						"title": "Portal Security",
						"allocation_strategy": "Random",
						"participants": [QA_LEAD, TESTER_ONE, TESTER_THREE],
						"case_titles": [
							"SSO login with Google",
							"Password reset email is delivered",
							"Session timeout redirects to login",
						],
						"runs": [
							{
								"title": "Portal Security Cycle 2",
								"status": "In Progress",
								"testing_lead": QA_LEAD,
								"stakeholders": [STAKEHOLDER, PRODUCT_OWNER],
								"results": [
									_res(
										"SSO login with Google",
										"Pass",
										"Google consent completed; session created.",
										assignee=TESTER_ONE,
									),
									_res(
										"Password reset email is delivered",
										"Retest",
										"Waiting on mail-provider fix from UAT fail.",
										assignee=TESTER_THREE,
									),
									_res(
										"Session timeout redirects to login",
										"In progress",
										assignee=QA_LEAD,
									),
								],
							}
						],
					},
				],
			},
			{
				"product": "Admin Console",
				"test_cases": [
					_tc(
						"Invite team member by email",
						pre="Current user is an organization admin.",
						steps=_steps(
							"Open Team > Invite",
							"Enter a new email and role Tester",
							"Send invite",
						),
						expected="Invite email is queued and the member appears as Pending.",
					),
					_tc(
						"Revoke user access immediately",
						pre="A tester account is active and logged in on another session.",
						steps=_steps("Open Team", "Revoke the tester", "Attempt an API call as that user"),
						expected="Subsequent requests return 401 and the user cannot sign in.",
					),
					_tc(
						"Role change takes effect on next request",
						pre="A user has Tester role.",
						steps=_steps(
							"Change role to Billing Admin",
							"Refresh the user session",
							"Open Billing > Invoices",
						),
						expected="Invoices page is accessible without re-login beyond refresh.",
					),
					_tc(
						"Audit log records permission change",
						pre="Audit logging is enabled.",
						steps=_steps("Change a user role", "Open Audit Log", "Filter by that user"),
						expected="An entry shows actor, old role, new role, and timestamp.",
					),
					_tc(
						"Impersonate customer as support admin",
						pre="Support impersonation is enabled for the admin.",
						steps=_steps(
							"Open a customer record",
							"Click Impersonate",
							"Confirm the banner in the portal",
						),
						expected="Admin sees the portal as the customer with a clear impersonation banner.",
					),
					_tc(
						"Feature flag toggle without restart",
						pre="A boolean feature flag exists for invoice export.",
						steps=_steps("Disable the flag", "Reload Admin Console", "Open invoice export"),
						expected="Export action is hidden immediately without a process restart.",
					),
				],
				"plans": [
					{
						"title": "Admin Smoke",
						"allocation_strategy": "Round Robin",
						"participants": [QA_LEAD, TESTER_THREE],
						"case_titles": [
							"Invite team member by email",
							"Revoke user access immediately",
							"Role change takes effect on next request",
							"Audit log records permission change",
							"Feature flag toggle without restart",
						],
						"runs": [
							{
								"title": "Admin Smoke Build 18",
								"status": "Completed",
								"testing_lead": QA_LEAD,
								"stakeholders": [PRODUCT_OWNER, STAKEHOLDER],
								"results": [
									_res("Invite team member by email", "Pass", "Invite delivered."),
									_res("Revoke user access immediately", "Pass", "Session invalidated."),
									_res("Role change takes effect on next request", "Pass"),
									_res("Audit log records permission change", "Pass"),
									_res("Feature flag toggle without restart", "Pass"),
								],
							}
						],
					},
					{
						"title": "Admin RBAC",
						"allocation_strategy": "Random",
						"participants": [TESTER_ONE, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Impersonate customer as support admin",
							"Revoke user access immediately",
							"Role change takes effect on next request",
						],
						"runs": [
							{
								"title": "Admin RBAC Week 32",
								"status": "In Progress",
								"testing_lead": TESTER_THREE,
								"stakeholders": [QA_LEAD],
								"results": [
									_res(
										"Impersonate customer as support admin",
										"Fail",
										"Impersonation banner missing on mobile viewport.",
									),
									_res("Revoke user access immediately", "In progress"),
									_res("Role change takes effect on next request", "Pending"),
								],
							}
						],
					},
					{
						"title": "Admin Backlog Review",
						"allocation_strategy": "Round Robin",
						"participants": [QA_LEAD, PRODUCT_OWNER],
						"case_titles": [
							"Invite team member by email",
							"Feature flag toggle without restart",
						],
					},
				],
			},
			{
				"product": "Internal Tools",
				"test_cases": [
					_tc(
						"Ops runbook link opens in new tab",
						pre="User is on the internal tools home.",
						steps=_steps("Click Runbooks", "Select Incident Response"),
						expected="Runbook opens in a new tab at the documented URL.",
					),
					_tc(
						"Staging data reset completes under 10 minutes",
						pre="Staging reset job is idle.",
						steps=_steps("Trigger Reset Staging from Internal Tools", "Watch job status"),
						expected="Job reaches Success and key tables are non-empty.",
					),
				],
				"plans": [],
			},
		],
	},
	{
		"project_name": "Mobile App QA",
		"products": [
			{
				"product": "iOS Companion App",
				"test_cases": [
					_tc(
						"Push notification opens deep link",
						pre="App is installed and notifications are allowed.",
						steps=_steps("Send a campaign push with a deep link", "Tap the notification"),
						expected="App opens the correct in-app screen.",
					),
					_tc(
						"Offline invoice list shows cached data",
						pre="User previously loaded invoices while online.",
						steps=_steps("Enable airplane mode", "Open Invoices"),
						expected="Cached invoices display with an offline banner.",
					),
					_tc(
						"Biometric unlock returns to last screen",
						pre="Biometric unlock is enabled.",
						steps=_steps(
							"Background the app for 2 minutes",
							"Foreground and authenticate with biometrics",
						),
						expected="User lands on the previously active screen.",
					),
					_tc(
						"Apple Pay checkout",
						pre="Device has Apple Pay configured and an unpaid invoice.",
						steps=_steps("Open invoice", "Tap Pay with Apple Pay", "Confirm with Face ID"),
						expected="Payment succeeds and invoice shows Paid.",
					),
					_tc(
						"Background refresh updates invoice badge",
						pre="App has background refresh enabled and an overdue invoice exists.",
						steps=_steps(
							"Background the app",
							"Wait for background fetch",
							"Check home-screen badge",
						),
						expected="Badge count matches overdue invoices.",
					),
					_tc(
						"VoiceOver labels on invoice list",
						pre="VoiceOver is enabled.",
						steps=_steps("Open Invoices", "Swipe through the first three rows"),
						expected="Each row announces customer, amount, and status.",
					),
					_tc(
						"Widget shows overdue count",
						pre="Home-screen widget is added.",
						steps=_steps("Create an overdue invoice on web", "Wait for widget refresh"),
						expected="Widget count increments without opening the app.",
					),
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
									_res(
										"Push notification opens deep link",
										"Pass",
										"Deep link resolved to invoice detail.",
									),
									_res(
										"Offline invoice list shows cached data",
										"Pass",
										"Cached rows and offline banner shown.",
									),
									_res(
										"Biometric unlock returns to last screen",
										"Pass",
										"Returned to Settings after Face ID.",
									),
								],
							}
						],
					},
					{
						"title": "iOS Release 2.1",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_ONE, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Apple Pay checkout",
							"Background refresh updates invoice badge",
							"VoiceOver labels on invoice list",
							"Push notification opens deep link",
						],
						"runs": [
							{
								"title": "iOS 2.1 RC1",
								"status": "In Progress",
								"testing_lead": TESTER_ONE,
								"stakeholders": [PRODUCT_OWNER, QA_LEAD],
								"results": [
									_res("Apple Pay checkout", "Pass", "Payment captured."),
									_res(
										"Background refresh updates invoice badge",
										"Fail",
										"Badge stayed at 0 after 15 minutes.",
									),
									_res("VoiceOver labels on invoice list", "In progress"),
									_res("Push notification opens deep link", "Pending"),
								],
							}
						],
					},
					{
						"title": "iOS Accessibility",
						"allocation_strategy": "Random",
						"participants": [TESTER_TWO],
						"case_titles": [
							"VoiceOver labels on invoice list",
							"Biometric unlock returns to last screen",
						],
						"runs": [
							{
								"title": "iOS A11y Draft",
								"status": "Draft",
								"testing_lead": TESTER_TWO,
								"stakeholders": [QA_LEAD],
								"results": [
									_res("VoiceOver labels on invoice list", "Pending"),
									_res("Biometric unlock returns to last screen", "Pending"),
								],
							}
						],
					},
				],
			},
			{
				"product": "Android Companion App",
				"test_cases": [
					_tc(
						"FCM notification opens deep link",
						pre="App is installed and notifications are allowed.",
						steps=_steps("Send an FCM campaign with a deep link", "Tap the notification"),
						expected="App opens the correct in-app screen.",
					),
					_tc(
						"Offline mode queues payment",
						pre="User is viewing an unpaid invoice.",
						steps=_steps(
							"Enable airplane mode",
							"Tap Pay",
							"Disable airplane mode and wait",
						),
						expected="Payment is queued offline then submitted when connectivity returns.",
					),
					_tc(
						"Fingerprint unlock",
						pre="Fingerprint unlock is enabled.",
						steps=_steps("Background the app", "Foreground and authenticate"),
						expected="App unlocks and restores the last screen.",
					),
					_tc(
						"Back button restores list scroll",
						pre="Invoice list is scrolled past the first page.",
						steps=_steps("Open an invoice", "Press system Back"),
						expected="List returns at the previous scroll position.",
					),
					_tc(
						"Dark theme follows system",
						pre="Android dark theme is on.",
						steps=_steps("Force-stop the app", "Relaunch"),
						expected="App launches in dark theme without a flash of light UI.",
					),
					_tc(
						"Share invoice via Android share sheet",
						pre="A paid invoice exists.",
						steps=_steps("Open invoice", "Tap Share", "Choose Gmail"),
						expected="Share sheet opens with PDF attached or invoice link.",
					),
				],
				"plans": [
					{
						"title": "Android Smoke",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_ANDROID, TESTER_ONE],
						"case_titles": [
							"FCM notification opens deep link",
							"Offline mode queues payment",
							"Fingerprint unlock",
							"Back button restores list scroll",
						],
						"runs": [
							{
								"title": "Android Smoke Build 19",
								"status": "Completed",
								"testing_lead": TESTER_ANDROID,
								"stakeholders": [QA_LEAD, STAKEHOLDER],
								"results": [
									_res(
										"FCM notification opens deep link",
										"Pass",
										"Opened invoice detail.",
									),
									_res(
										"Offline mode queues payment",
										"Fail",
										"Pay button disabled offline instead of queueing.",
									),
									_res(
										"Fingerprint unlock",
										"Blocked",
										"Emulator has no fingerprint hardware.",
									),
									_res(
										"Back button restores list scroll",
										"Pass",
										"Scroll position restored.",
									),
								],
								"retest": {
									"title": "Android Smoke Build 19 - Retest",
									"status": "In Progress",
									"testing_lead": TESTER_ANDROID,
									"stakeholders": [QA_LEAD],
									"results": [
										_res(
											"Offline mode queues payment",
											"In progress",
											"Hotfix installed; retesting queue path.",
										),
										_res("Fingerprint unlock", "Pending", assignee=TESTER_ONE),
									],
								},
							}
						],
					},
					{
						"title": "Android Regression",
						"allocation_strategy": "Random",
						"participants": [TESTER_ANDROID, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Dark theme follows system",
							"Share invoice via Android share sheet",
							"FCM notification opens deep link",
							"Fingerprint unlock",
						],
						"runs": [
							{
								"title": "Android Regression Draft",
								"status": "Draft",
								"testing_lead": TESTER_ANDROID,
								"stakeholders": [PRODUCT_OWNER],
								"results": [
									_res("Dark theme follows system", "Pending"),
									_res("Share invoice via Android share sheet", "Pending"),
									_res("FCM notification opens deep link", "Pending"),
									_res("Fingerprint unlock", "Pending"),
								],
							}
						],
					},
				],
			},
		],
	},
	{
		"project_name": "Platform API QA",
		"products": [
			{
				"product": "Payments API",
				"test_cases": [
					_tc(
						"POST /payments returns 201",
						pre="A valid API key and unpaid invoice id exist.",
						steps=_steps(
							"POST /v1/payments with invoice id and amount",
							"Inspect status and body",
						),
						expected="201 Created with payment id and status processing or succeeded.",
					),
					_tc(
						"Idempotency key prevents double charge",
						pre="A valid payment payload and idempotency key are ready.",
						steps=_steps(
							"POST /v1/payments with Idempotency-Key A",
							"Repeat the same request",
						),
						expected="Second response matches the first and only one charge is created.",
					),
					_tc(
						"Invalid currency returns 422",
						pre="API key is valid.",
						steps=_steps("POST /v1/payments with currency ZZZ", "Inspect status and errors"),
						expected="422 with a machine-readable invalid_currency error.",
					),
					_tc(
						"Webhook signature verification",
						pre="Webhook secret is configured on the receiver.",
						steps=_steps(
							"Send a signed payment.succeeded event",
							"Send the same body with a bad signature",
						),
						expected="Valid signature is accepted; invalid signature is rejected with 401.",
					),
					_tc(
						"Refund endpoint is idempotent",
						pre="A succeeded payment exists.",
						steps=_steps(
							"POST /v1/refunds with a key",
							"Repeat the refund request",
						),
						expected="Only one refund is created; second call returns the same refund id.",
					),
					_tc(
						"Rate limit returns 429 with Retry-After",
						pre="Rate limit is 10 requests per minute for the test key.",
						steps=_steps("Burst 20 POST /v1/payments requests", "Inspect later responses"),
						expected="Excess requests return 429 with Retry-After header.",
					),
					_tc(
						"Pagination on GET /invoices",
						pre="More than one page of invoices exists.",
						steps=_steps(
							"GET /v1/invoices?limit=2",
							"Follow starting_after from the last id",
						),
						expected="Second page returns the next invoices without overlap.",
					),
					_tc(
						"Health check /readyz",
						steps=_steps("GET /readyz"),
						expected="200 with status ok when dependencies are healthy.",
					),
				],
				"plans": [
					{
						"title": "API Contract",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_ONE, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"POST /payments returns 201",
							"Idempotency key prevents double charge",
							"Invalid currency returns 422",
							"Webhook signature verification",
							"Refund endpoint is idempotent",
							"Rate limit returns 429 with Retry-After",
							"Pagination on GET /invoices",
						],
						"runs": [
							{
								"title": "API Contract v4.2",
								"status": "Completed",
								"testing_lead": TESTER_ONE,
								"stakeholders": [QA_LEAD, PRODUCT_OWNER],
								"results": [
									_res("POST /payments returns 201", "Pass", "201 with payment_id."),
									_res("Idempotency key prevents double charge", "Pass"),
									_res(
										"Invalid currency returns 422",
										"Fail",
										"API returned 400 with a plain-text body.",
									),
									_res(
										"Webhook signature verification",
										"Blocked",
										"Staging webhook secret not provisioned.",
									),
									_res("Refund endpoint is idempotent", "Pass"),
									_res(
										"Rate limit returns 429 with Retry-After",
										"Pass",
										"Retry-After was 12 seconds.",
									),
									_res(
										"Pagination on GET /invoices",
										"Fail",
										"Page 2 repeated the last id from page 1.",
									),
								],
								"retest": {
									"title": "API Contract v4.2 - Retest",
									"status": "Completed",
									"testing_lead": TESTER_ONE,
									"stakeholders": [QA_LEAD, PRODUCT_OWNER],
									"results": [
										_res(
											"Invalid currency returns 422",
											"Pass",
											"Now 422 with invalid_currency.",
										),
										_res(
											"Webhook signature verification",
											"Pass",
											"Bad signatures rejected with 401.",
										),
										_res(
											"Pagination on GET /invoices",
											"Pass",
											"Pages no longer overlap.",
										),
									],
								},
							}
						],
					},
					{
						"title": "API Chaos",
						"allocation_strategy": "Random",
						"participants": [TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Rate limit returns 429 with Retry-After",
							"Idempotency key prevents double charge",
							"Health check /readyz",
						],
						"runs": [
							{
								"title": "API Chaos Week 32",
								"status": "In Progress",
								"testing_lead": TESTER_TWO,
								"stakeholders": [QA_LEAD],
								"results": [
									_res(
										"Rate limit returns 429 with Retry-After",
										"Pass",
										"Limiter held under burst.",
									),
									_res("Idempotency key prevents double charge", "In progress"),
									_res("Health check /readyz", "Pending"),
								],
							}
						],
					},
					{
						"title": "API Unscheduled",
						"allocation_strategy": "Round Robin",
						"participants": [TESTER_ONE],
						"case_titles": [
							"Health check /readyz",
							"POST /payments returns 201",
						],
					},
				],
			},
			{
				"product": "Notifications Service",
				"test_cases": [
					_tc(
						"Email template renders customer name",
						pre="A customer named Ada Lovelace exists.",
						steps=_steps("Trigger invoice_ready email", "Inspect rendered HTML"),
						expected="Greeting includes Ada Lovelace and no leftover mustache tokens.",
					),
					_tc(
						"SMS fallback when email bounces",
						pre="Customer email is configured to bounce and SMS number is verified.",
						steps=_steps("Trigger overdue reminder", "Check email then SMS logs"),
						expected="After bounce, an SMS reminder is sent within 5 minutes.",
					),
					_tc(
						"Digest email batches overnight",
						pre="Customer has digest=daily and three events during the day.",
						steps=_steps("Advance clock to digest send window", "Inspect outbound email"),
						expected="One digest email lists all three events.",
					),
					_tc(
						"Unsubscribe link is one-click",
						pre="A marketing email was delivered.",
						steps=_steps("Open unsubscribe URL without logging in", "Confirm"),
						expected="Customer is unsubscribed and sees a confirmation page.",
					),
				],
				"plans": [
					{
						"title": "Notifications UAT",
						"allocation_strategy": "Round Robin",
						"participants": [QA_LEAD],
						"case_titles": [
							"Email template renders customer name",
							"SMS fallback when email bounces",
							"Digest email batches overnight",
							"Unsubscribe link is one-click",
						],
						"runs": [
							{
								"title": "Notifications UAT Cycle 3",
								"status": "Completed",
								"testing_lead": QA_LEAD,
								"stakeholders": [PRODUCT_OWNER],
								"results": [
									_res(
										"Email template renders customer name",
										"Pass",
										"Name rendered correctly.",
									),
									_res("SMS fallback when email bounces", "Pass"),
									_res("Digest email batches overnight", "Pass"),
									_res("Unsubscribe link is one-click", "Pass"),
								],
							}
						],
					},
					{
						"title": "Notifications Load",
						"allocation_strategy": "Random",
						"participants": [TESTER_ONE, TESTER_TWO, TESTER_THREE],
						"case_titles": [
							"Digest email batches overnight",
							"Email template renders customer name",
							"Unsubscribe link is one-click",
						],
						"runs": [
							{
								"title": "Notifications Load Draft",
								"status": "Draft",
								"testing_lead": TESTER_THREE,
								"stakeholders": [QA_LEAD, STAKEHOLDER],
								"results": [
									_res("Digest email batches overnight", "Pending"),
									_res("Email template renders customer name", "Pending"),
									_res("Unsubscribe link is one-click", "Pending"),
								],
							}
						],
					},
				],
			},
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
			for case_spec in product_spec.get("test_cases", []):
				tc = _ensure_test_case(project.name, product.name, case_spec)
				cases_by_title[case_spec["title"]] = tc

			product_summary = {
				"product": product.name,
				"product_label": product.product,
				"test_cases": [tc.name for tc in cases_by_title.values()],
				"plans": [],
			}

			for plan_spec in product_spec.get("plans", []):
				selected = [cases_by_title[title] for title in plan_spec["case_titles"]]
				plan = _ensure_test_plan(project.name, product.name, plan_spec, selected)
				plan_summary = {
					"test_plan": plan.name,
					"title": plan.title,
					"runs": [],
				}

				for run_spec in plan_spec.get("runs", []):
					test_run = _ensure_test_run(plan, run_spec, cases_by_title)
					run_summary = {
						"test_run": test_run.name,
						"title": test_run.title,
						"status": test_run.status,
					}

					retest_spec = run_spec.get("retest")
					if retest_spec:
						run_summary["retest"] = _seed_retest_chain(
							plan, test_run, retest_spec, cases_by_title
						)

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
	existing = frappe.db.get_value("Product", {"product": product_label, "project": project}, "name")
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
			"allocation_strategy": plan_spec.get("allocation_strategy") or "Round Robin",
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


def _apply_run_status(doc, result_rows: list[dict], desired_status: str):
	progress = _progress_for(result_rows)
	updates = {"progress": progress}
	if desired_status == "Completed":
		updates["status"] = "Completed"
	doc.db_set(updates, update_modified=False)
	doc.reload()
	return doc


def _ensure_test_run(plan, run_spec: dict, cases_by_title: dict):
	existing = frappe.db.get_value("Test Run", {"title": run_spec["title"], "test_plan": plan.name}, "name")
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
			"stakeholders": [{"user": user} for user in run_spec.get("stakeholders", [])],
		}
	).insert(ignore_permissions=True)

	return _apply_run_status(doc, result_rows, desired_status)


def _seed_retest_chain(plan, source_run, retest_spec: dict, cases_by_title: dict) -> dict:
	retest = _ensure_retest_run(plan, source_run, retest_spec, cases_by_title)
	summary = {
		"test_run": retest.name,
		"title": retest.title,
		"status": retest.status,
	}
	nested = retest_spec.get("retest")
	if nested:
		summary["retest"] = _seed_retest_chain(plan, retest, nested, cases_by_title)
	return summary


def _ensure_retest_run(plan, source_run, retest_spec: dict, cases_by_title: dict):
	existing = frappe.db.get_value(
		"Test Run", {"title": retest_spec["title"], "test_plan": plan.name}, "name"
	)
	if existing:
		return frappe.get_doc("Test Run", existing)

	overlay_by_case = {}
	for result_spec in retest_spec.get("results", []):
		overlay_by_case[cases_by_title[result_spec["title"]].name] = result_spec

	carry_forward = []
	for row in source_run.test_results:
		if row.status not in {"Fail", "Blocked"}:
			continue
		result_row = {
			"test_case": row.test_case,
			"assignee": row.assignee,
			"status": "Pending",
			"pre_condition": row.pre_condition,
			"steps_to_produce": row.steps_to_produce,
			"expected_result": row.expected_result,
		}
		overlay = overlay_by_case.get(row.test_case)
		if overlay:
			result_row["status"] = overlay["status"]
			if overlay.get("assignee"):
				result_row["assignee"] = overlay["assignee"]
			if overlay.get("actual_result"):
				result_row["actual_result"] = overlay["actual_result"]
		carry_forward.append(result_row)

	desired_status = retest_spec.get("status") or "Draft"
	insert_status = "In Progress" if desired_status == "Completed" else desired_status

	doc = frappe.get_doc(
		{
			"doctype": "Test Run",
			"title": retest_spec["title"],
			"test_plan": plan.name,
			"testing_lead": retest_spec.get("testing_lead") or source_run.testing_lead,
			"status": insert_status,
			"is_retest": 1,
			"retest_of": source_run.name,
			"test_results": carry_forward,
			"stakeholders": [
				{"user": user} for user in retest_spec.get("stakeholders", [STAKEHOLDER])
			],
		}
	).insert(ignore_permissions=True)

	return _apply_run_status(doc, carry_forward, desired_status)


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def _all_plan_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for plan in product.get("plans", []):
				titles.append(plan["title"])
	return titles


def _walk_run_titles(run_spec: dict, titles: list[str]):
	titles.append(run_spec["title"])
	if run_spec.get("retest"):
		_walk_run_titles(run_spec["retest"], titles)


def _all_run_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for plan in product.get("plans", []):
				for run in plan.get("runs", []):
					_walk_run_titles(run, titles)
	return titles


def _all_case_titles() -> list[str]:
	titles = []
	for project in PROJECTS:
		for product in project["products"]:
			for case in product.get("test_cases", []):
				titles.append(case["title"])
	return titles


def _all_product_labels() -> list[str]:
	return [product["product"] for project in PROJECTS for product in project["products"]]


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
			run_names.update(frappe.get_all("Test Run", filters={"test_plan": plan_name}, pluck="name"))

	_delete_docs("Test Run", sorted(run_names))

	for plan_title in _all_plan_titles():
		_delete_docs(
			"Test Plan",
			frappe.get_all("Test Plan", filters={"title": plan_title}, pluck="name"),
		)

	for product_label in _all_product_labels():
		product_names = frappe.get_all("Product", filters={"product": product_label}, pluck="name")
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
