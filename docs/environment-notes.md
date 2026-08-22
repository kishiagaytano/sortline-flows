# Environment Notes

## Bedrock Agents Classic unavailable
The project instructions assume the bug-report path is handled by a Bedrock Agent with an
action group. In this lab account, Agents Classic is in Maintenance Mode and new agent
creation is blocked:

> Bedrock Agents is in Maintenance Mode. New agent creation is not available for accounts
> without prior service usage.

The bug-report path is therefore implemented natively in the Flow as an extraction Prompt
node, a Condition node that checks whether all three required fields were collected, and a
Lambda node that invokes create_bug_report. This satisfies the same rubric requirement -
the path uses a tool to collect information and persist a ticket - without depending on a
service that is closed to new usage.

## Lambda payload handling
create_bug_report.py originally accepted only the Agents Classic envelope
(messageVersion / parameters / functionResponse) and returned {"error": "unsupported"} for
anything else. Since a Flow Lambda node sends a plain JSON object, the handler was updated
to accept both shapes and respond in kind.

## Resource naming
CloudFormation provisions the tool resources in this account as:

| Instructions | Actual |
|---|---|
| bug-report-tool-stack-create-bug-report | create-bug-report-421c6b10 |
| bug-report-tool-stack-bug-reports | BugReports-421c6b10 |

These are the same resources created by cloudformation-tool.yaml; only the generated names differ.

## Support phone number

The rubric requires that out-of-scope requests and questions not covered by the FAQ be
directed to a human support phone line. The provided `online_shop_faq.md` does not contain a
phone number - Q29 directs customers to a web contact form, and Q30 gives support hours
(Monday-Friday, excluding holidays) without a number.

The fictional number **1-800-555-0147** is therefore used consistently in both the `HandOff`
node and the not-covered-by-FAQ fallback in the `FaqAnswer` node. It is drawn from the
555-01XX range reserved for fictional use, so it cannot connect to a real party. The hours
quoted in the hand-off match Q30 of the FAQ.