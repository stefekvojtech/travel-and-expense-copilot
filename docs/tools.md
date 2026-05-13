# Deterministic Tools

This project now has a small deterministic tool layer under `app/tools/`.
These tools do not retrieve policy and do not replace grounded answer
generation. They receive structured claim facts and retrieved policy facts, then
return typed results that an agent, API route, or future UI can use.

## Current Tools

`app/tools/currency.py` converts amounts between currencies. It uses the
company Finance exchange rates from `data/raw/per_diem_caps.xlsx` first. If the
company workbook cannot satisfy the conversion, it can fall back to
Frankfurter's free exchange-rate API. User-provided exchange rates are not used
for reimbursement decisions.

`app/tools/evidence.py` checks evidence completeness. It takes an expense
category, amount, provided evidence fields, and retrieved evidence policy facts.
It returns missing fields, insufficient-evidence reasons, manual-review state,
and clarification questions for the agent or UI to ask.

`app/tools/eligibility.py` evaluates structured claim eligibility. It takes
claim lines, trip context, and retrieved eligibility policy facts. It returns
the claimed amount, reimbursable amount, excluded amount, above-cap amount,
required approval state, manual-review reasons, and clarification questions.

## How The Tools Work Together

The tools are designed to compose without hiding policy decisions:

```text
retrieved policy evidence
  -> structured policy facts

structured claim lines + trip context
  -> evaluate_claim_eligibility
  -> optional check_evidence_completeness
  -> structured tool result
  -> final grounded answer or clarification question
```

`evaluate_claim_eligibility` can call `check_evidence_completeness` when evidence
policy facts and provided evidence fields are available. If important claim data
or policy facts are missing, the tools return `needs_clarification`; they do not
guess and they do not ask the user directly.

## Boundaries

Implemented behavior:

- deterministic money totals
- exclusion of non-reimbursable line categories supplied in policy facts
- alcohol exclusion unless the context says the expense was approved client
  entertainment
- cap comparison for claim-level, per-night, and per-km caps
- taxi after-hours threshold checks when structured time and threshold are
  provided
- evidence field completeness checks with manual-review reasons
- clarification-question output for missing claim facts

Not yet implemented:

- automatic extraction of policy facts from retrieved evidence
- natural-language claim parsing
- receipt OCR post-processing
- agent tool-calling loop
- API or UI routes for claim evaluation
- persistence of tool calls or claim decisions

The current answer path does not call these tools yet.
