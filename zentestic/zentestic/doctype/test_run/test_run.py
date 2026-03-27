import frappe
import requests
from frappe.model.document import Document


class TestRun(Document):

    def validate(self):

        if self.status == "Completed":

            message = generate_test_run_report(self, "✅ Test Run Completed")

            send_telegram_group_message(message)


@frappe.whitelist()
def schedule_retest(test_run_name):

    old_run = frappe.get_doc("Test Run", test_run_name)

    new_run = frappe.new_doc("Test Run")
    new_run.test_plan = old_run.test_plan
    new_run.title = f"{old_run.title} - Retest"
    new_run.testing_lead = old_run.testing_lead
    new_run.status = "Draft"
    new_run.is_retest = 1
    new_run.retest_of = old_run.name

    new_run.insert()

    for row in old_run.test_results:
        if row.status in ["Fail", "Blocked"]:
            new_run.append("test_results", {
                "test_case": row.test_case,
                "assignee": row.assignee,
                "status": "Pending"
            })

    new_run.save()

    message = generate_test_run_report(old_run, "🔁 Retest Scheduled")
    send_telegram_group_message(message)

    return new_run.name


def send_telegram_group_message(message):

    bot_token = frappe.conf.get("telegram_bot_token")
    chat_id = frappe.conf.get("telegram_chat_id")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload)
    print(response.text)


def generate_test_run_report(test_run, notification_type):

    total = len(test_run.test_results)
    passed = len([r for r in test_run.test_results if r.status == "Pass"])
    failed = len([r for r in test_run.test_results if r.status == "Fail"])
    retest = len([r for r in test_run.test_results if r.status == "Retest"])

    return f"""
<b>{notification_type}</b>

<b>Test Run:</b> {test_run.name}
<b>Title:</b> {test_run.title}

<b>Total:</b> {total}
<b>Passed:</b> {passed}
<b>Failed:</b> {failed}
<b>Retest:</b> {retest}

<b>Status:</b> {test_run.status}
"""