# Environment Notes

## Environment identifiers

| Item | Value |
|---|---|
| Region | us-east-1 |
| Account | 500245700673 |
| Flow | customer-support-flow (UMXBKSKW0K) |
| Flow alias | prod (DCEN1QYLNG) |
| Lambda function | create-bug-report-421c6b10 |
| DynamoDB table | BugReports-421c6b10 |
| Guardrail | support-chatbot-guardrail |
| Eval dataset bucket | udacity-agentic-engineer-c1-eval-500245700673 |
| Evaluation job | support-chatbot-eval-run-1 |

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
anything else. A Flow Lambda node sends a different structure - the tool arguments arrive
wrapped in `node.inputs[0].value` - so the handler was updated to detect the payload shape
and respond in kind. It now accepts three shapes: the Flow node envelope, the Agents Classic
envelope, and a plain JSON object (or a JSON string), returning the Classic wrapper only for
the Classic envelope.

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

The fictional number **1-800-555-0147** is therefore used in both the `HandOff` node and the
not-covered-by-FAQ fallback in the `FaqAnswer` node. It is drawn from the 555-01XX range
reserved for fictional use, so it cannot connect to a real party.

**Known inconsistency.** The two nodes do not quote hours identically. `HandOff` says
"available Monday to Friday", which matches Q30. The `FaqAnswer` fallback says "9am to 6pm
Monday to Friday" - Q30 gives no times, so those hours are an unsourced addition rather than
FAQ-derived. This is visible in `evidence/09_test_faq_uncovered.png` and in the `t08`/`t09`
responses in `output_eval_dataset.jsonl`. No FAQ policy is invented in either case; only the
hours differ. Fixing the `FaqAnswer` fallback prompt to drop the times would make the two
nodes consistent.