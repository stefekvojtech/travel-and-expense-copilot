# LangChain Chunk Preview: extended_expense_scenarios.txt

- doc_id: `extended-expense-scenarios-b3f521ebe6`
- source_path: `data/raw/extended_expense_scenarios.txt`
- loader: `TextLoader`
- loaded_documents: `1`
- chunks: `8`

## Sample Chunks

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00001

- strategy: `recursive_tiktoken`
- tokens: `578`

```text
Atlas Mobility Group Extended Expense Scenario Narrative 2026. This plain text source is intentionally written as one long policy-style narrative rather than a structured handbook. It exists to test recursive chunking when Markdown header splitting has little useful structure to work with. The content follows the same synthetic company policy universe as the Travel Policy PDF, Expense Policy HTML page, and Per Diem Caps workbook. It is not a separate authority above those sources. It should be interpreted as explanatory operational guidance from Finance Operations, used for examples, audit reasoning, and edge cases where employees need to understand how the travel and expense rules are applied in practice.

The guiding principle is that Atlas reimburses reasonable business expenses when the employee can show a business purpose, a connection to company work, the date, the vendor, the amount, the currency, and enough evidence to let Finance verify the claim. A reimbursement claim does not become valid just because it was paid with a corporate card, approved in a calendar invitation, or discussed informally with a manager. The expense still needs to fit the policy category and the evi
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00002

- strategy: `recursive_tiktoken`
- tokens: `550`

```text
For receipts, the minimum evidence standard is practical rather than theatrical. Finance does not need a perfect document if the business facts are otherwise clear, but it does need enough information to validate the claim. A good receipt shows vendor, date, amount, currency, tax where available, and the item or service purchased. A hotel folio should show guest name, property, city, stay dates, room nights, taxes, breakfast indication when available, and total paid. A taxi or ride-hailing receipt should show pickup, drop-off, date, amount, currency, and vendor. If the receipt lacks route information, the employee should enter origin and destination manually. A credit card statement alone proves payment but normally does not prove the business purpose or item-level eligibility. Missing receipts are handled with judgment, but repeated missing evidence is a risk signal. If a receipt is lost and the amount is small, the employee may submit a missing receipt declaration explaining the reason. If the missing receipt declaration is above EUR 25, manager approval is required. If the expense is above a local threshold, unusual for the category, or connected to client entertainment, Finance
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00003

- strategy: `recursive_tiktoken`
- tokens: `500`

```text
Client entertainment requires stronger evidence than ordinary meals because it can easily be confused with team meals or personal hospitality. A valid client entertainment claim should show attendee names, companies, relationship to the project or opportunity, business purpose, date, vendor, amount, currency, and pre-approval when required. Client entertainment above EUR 120 total requires pre-approval from the cost center owner or Sales VP. Alcohol with a client meal also requires pre-approval. A vague note such as customer relationship building is usually not enough. A better explanation would identify the account, the meeting purpose, the opportunity, the negotiation, the implementation milestone, or the service issue discussed.

Team celebrations are not the same as client entertainment. A team dinner after a project milestone may be valuable, but it is normally charged to an employee morale or team budget rather than travel expense. If the cost is above EUR 50 per person, manager approval is required. Alcohol at team events follows local company rules and cannot be hidden inside a travel meal category. If a receipt mixes employees, clients, alcohol, and personal guests, the em
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00004

- strategy: `recursive_tiktoken`
- tokens: `569`

```text
Employees must pay attention to source currency. Claims should be entered in the currency shown on the receipt when possible. Finance conversion rates should come from the monthly Finance exchange table, not from a random search engine or a card statement, unless Finance explicitly requests the card statement. This matters for cities such as Prague, Zurich, London, New York, Warsaw, and Budapest where caps may be stored or paid in local currency. If an employee pays a Czech taxi receipt in CZK, the source amount should remain CZK and conversion should use the approved monthly rate.

Hotel reimbursement depends on city caps, reasonableness, and evidence. If a hotel is within the city cap and the folio is complete, reimbursement is usually straightforward. If the hotel is above the cap, the employee needs pre-approval or evidence that no reasonable alternatives were available. Examples include sold-out conference weeks, trade fairs, weather disruption, safety constraints, customer-required location, or late approval of urgent travel. A screenshot showing several unavailable or materially more expensive hotels can support the exception. A preference for a nicer hotel, loyalty points, 
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00005

- strategy: `recursive_tiktoken`
- tokens: `446`

```text
Rental cars should be compact or mid-size by default. A larger vehicle may be reimbursable when business equipment, customer materials, safety, weather, or passenger count makes it reasonable. Luxury, premium, SUV, or sports categories require cost center owner approval. Insurance upgrades require a business justification. Fuel for rental cars can be reimbursed with receipt when the rental was approved and the route was business-related. Traffic fines, speeding tickets, private parking violations, penalties, and lost ticket fees are never reimbursable, even when they happened during a business trip.

Flights follow a strict cabin policy. Economy is the default. Premium economy may be selected when flight duration exceeds 4 hours and the price difference is reasonable. Business class requires pre-approval and is normally limited to intercontinental trips above 6 hours or documented medical, security, or critical business need. A business class flight from Vienna to New York lasting 9 hours may be eligible only when pre-approved and supported by business reason. Without approval it should go to manual review or be rejected. Boarding passes or equivalent proof of travel are required b
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00006

- strategy: `recursive_tiktoken`
- tokens: `388`

```text
Expense timing matters. Claims should be submitted within 30 calendar days after trip end. Claims older than 90 days are normally rejected unless Finance approves an exception. A late claim with complete evidence can still fail because timely submission is part of the policy. Finance may audit before or after reimbursement. Audit checks may include duplicate detection, cap validation, receipt completeness, date consistency, route reasonableness, alcohol removal, missing receipt declarations, exchange rate consistency, and whether the selected source has priority for the question.

Policy source priority matters when sources seem to conflict. Local law and tax rules come first. Written pre-approval comes next for approved exceptions. The Travel Policy PDF governs travel logistics, approval authority, booking class, travel evidence, and travel security. The Expense Policy HTML page governs evidence requirements, reimbursement categories, submission rules, meals, entertainment, transport evidence, and non-reimbursable items. The Per Diem Caps workbook governs numeric meal caps, hotel caps, taxi after-hours thresholds, mileage rates, exchange rates, approval thresholds, and determinist
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00007

- strategy: `recursive_tiktoken`
- tokens: `545`

```text
Corporate travel cards simplify payment but do not change eligibility. The employee remains responsible for explaining the business purpose and attaching evidence. A corporate card transaction without a receipt may still require a missing receipt declaration. Personal expenses accidentally charged to a corporate card must be repaid or deducted according to Finance procedure. Employees should not use the corporate card for family travel, leisure activities, personal subscriptions, private commuting, personal clothing, gifts without approval, or expenses for companions unless an explicit policy exception applies. Mixed receipts are common and should be handled transparently. A hotel folio may include room charges, breakfast, city tax, laundry, mini-bar, and parking. The employee should claim room charges, required taxes, approved breakfast if not already included or otherwise eligible, business parking where allowed, and laundry only when trip length qualifies. The employee should remove mini-bar, movies, spa, personal services, and duplicate breakfast. A restaurant receipt may include food, alcohol, tips, and personal guests. The employee should claim eligible food, reasonable tips 
```

### extended-expense-scenarios-b3f521ebe6:lc-chunk:00008

- strategy: `recursive_tiktoken`
- tokens: `514`

```text
Manual review is not punishment. It is the normal process for cases where eligibility is unclear, evidence is incomplete, approval is missing, source priority conflicts, or the cost is high. Manual review may approve the claim, cap the reimbursement, request more evidence, reclassify the expense, or reject a personal portion. Employees can reduce manual review by documenting the business reason at the time of travel rather than trying to reconstruct it later. Managers should approve only expenses they understand and should reject claims where business purpose or evidence is not credible.

Several examples illustrate the logic. A Berlin hotel at EUR 175 per night is within the Berlin cap if the workbook cap is EUR 180, assuming the folio is complete. A Zurich hotel at CHF 260 when the cap is CHF 240 needs approval or shortage evidence, and the reimbursable hint may be capped if no approval exists. A Vienna dinner with EUR 32 food and EUR 8 wine during ordinary travel should reimburse the food portion only if within cap. A client dinner of EUR 150 with EUR 20 alcohol may be reimbursable when pre-approved and supported by attendee list and business purpose. A Prague taxi at 20:30 with
```
