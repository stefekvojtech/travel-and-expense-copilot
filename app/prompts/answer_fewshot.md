## Output Schema

Return a single JSON object with exactly these fields:

```json
{
  "answer": "Concise policy answer with citation markers on supported claims.",
  "citations": ["[1]"],
  "confidence": "high|medium|low",
  "abstained": false
}
```

Use `confidence` as follows:

- `high`: the evidence directly answers the question.
- `medium`: the answer is supported but requires combining multiple evidence blocks.
- `low`: evidence is partial, conflicting, or missing.

If you abstain, set `abstained` to `true`, use `confidence` of `low`, and include
an answer that explains that the available sources do not support a policy
decision.

## Examples

Question:
Can I claim a helicopter transfer from airport to hotel?

Evidence:
[1] Travel Policy
content:
Taxis may be reimbursed after-hours or when public transport is impractical.

Answer:
```json
{
  "answer": "The available evidence does not specify helicopter transfers, so I cannot decide this from the policy corpus. Manual review is required.",
  "citations": [],
  "confidence": "low",
  "abstained": true
}
```

Question:
Is public transport preferred over taxis?

Evidence:
[1] Expense Policy
content:
Employees should prefer public transport when safe and practical. Taxis are
reimbursable only under defined exceptions.

Answer:
```json
{
  "answer": "Yes. Employees should prefer public transport when it is safe and practical; taxis are reimbursable only under defined exceptions. [1]",
  "citations": ["[1]"],
  "confidence": "high",
  "abstained": false
}
```
