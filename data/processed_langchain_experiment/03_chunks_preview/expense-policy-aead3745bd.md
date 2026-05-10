# LangChain Chunk Preview: expense_policy.html

- doc_id: `expense-policy-aead3745bd`
- source_path: `data/raw/expense_policy.html`
- loader: `BSHTMLLoader`
- loaded_documents: `1`
- chunks: `13`

## Chunks

### expense-policy-aead3745bd:chunk:00001

- strategy: `markdown_header+section_as_chunk`
- tokens: `91` section='Atlas Mobility Group - Expense Policy 2026'
- source_block_ids: `["expense-policy-aead3745bd:00001", "expense-policy-aead3745bd:00002", "expense-policy-aead3745bd:00003", "expense-policy-aead3745bd:00004", "expense-policy-aead3745bd:00005", "expense-policy-aead3745bd:00006", "expense-policy-aead3745bd:00007", "expense-policy-aead3745bd:00008", "expense-policy-aead3745bd:00009", "expense-policy-aead3745bd:00010", "expense-policy-aead3745bd:00011", "expense-policy-aead3745bd:00012", "expense-policy-aead3745bd:00013"]`

```text
# Atlas Mobility Group - Expense Policy 2026  
Document type: Internal HTML policy snapshot  
Effective: 2026-01-01 | Owner: Finance Operations | Version: EXP-2026.2  
This HTML policy governs reimbursement evidence, meal limits, receipts, entertainment, and expense audit behavior.  
Purpose  
Receipts  
Meals  
Entertainment  
Transport  
Mileage  
Digital tools  
Non-reimbursable  
FAQ
```

### expense-policy-aead3745bd:chunk:00002

- strategy: `markdown_header+section_as_chunk`
- tokens: `198` section='1. Purpose and Scope'
- source_block_ids: `["expense-policy-aead3745bd:00014", "expense-policy-aead3745bd:00015", "expense-policy-aead3745bd:00016", "expense-policy-aead3745bd:00017", "expense-policy-aead3745bd:00018", "expense-policy-aead3745bd:00019", "expense-policy-aead3745bd:00020", "expense-policy-aead3745bd:00021", "expense-policy-aead3745bd:00022", "expense-policy-aead3745bd:00023"]`

```text
## 1. Purpose and Scope  
This policy explains which expenses may be reimbursed by Atlas Mobility Group when an employee incurs reasonable business costs. The policy applies to employees, contractors with explicit written expense terms, and temporary workers travelling on behalf of the company.  
This HTML policy is intended to be read together with the Travel Policy PDF and the Per Diem Caps spreadsheet. If two sources conflict, use the following priority order:  
1. Country-specific legal rules and tax requirements.  
2. Written pre-approval from Finance Operations or the employee's cost center owner.  
3. The Travel Policy PDF for travel logistics and approval requirements.  
4. This Expense Policy HTML page for evidence and reimbursement rules.  
5. The Per Diem Caps spreadsheet for numeric country, city, lodging, meal, and taxi thresholds.  
Evidence principle:  
Atlas reimburses business expenses only when the business purpose, date, amount, currency, vendor, and employee connection are reasonably clear.
```

### expense-policy-aead3745bd:chunk:00003

- strategy: `markdown_header+section_as_chunk`
- tokens: `246` section='2. Receipt and Evidence Requirements'
- source_block_ids: `["expense-policy-aead3745bd:00024", "expense-policy-aead3745bd:00025", "expense-policy-aead3745bd:00026", "expense-policy-aead3745bd:00027"]`

```text
## 2. Receipt and Evidence Requirements  
Receipts are required for all expense claims above EUR 10.00. A card transaction alone is not sufficient evidence.  
| Evidence item | Required when | Minimum content | Fallback if missing |
| --- | --- | --- | --- |
| Itemized receipt | Meals, hotels, taxis, client entertainment, parking, supplies | Vendor, date, line items or description, tax if available, total amount, currency | Employee must submit missing receipt declaration and manager approval if over EUR 25 |
| Boarding pass | Flights | Passenger name, route, date, flight number or carrier | Airline travel certificate may replace boarding pass |
| Hotel folio | Hotel stays | Guest name, room nights, taxes, breakfast indication, city, total | Booking confirmation alone is not enough if it does not prove payment |
| Attendee list | Client entertainment or group meals above EUR 120 | Names, company, business purpose, host employee, relationship to project | Claim is held until attendee list is provided |  
Missing evidence does not automatically make an expense non-reimbursable, but it lowers confidence and may trigger manual review. Repeat missing evidence can lead to reimbursement refusal.
```

### expense-policy-aead3745bd:chunk:00004

- strategy: `markdown_header+section_as_chunk`
- tokens: `295` section='3. Meals and Daily Subsistence'
- source_block_ids: `["expense-policy-aead3745bd:00028", "expense-policy-aead3745bd:00029", "expense-policy-aead3745bd:00030", "expense-policy-aead3745bd:00031", "expense-policy-aead3745bd:00032", "expense-policy-aead3745bd:00033"]`

```text
## 3. Meals and Daily Subsistence  
Meal reimbursement must be reasonable for the travel location. The numeric cap is maintained in the Per Diem Caps spreadsheet. The meal cap applies to the reimbursable food portion before non-reimbursable alcohol is removed.  
| Meal type | Default rule | Receipt required? | Important limitation |
| --- | --- | --- | --- |
| Breakfast | Reimbursable only if not included in hotel rate or event package | Yes if above EUR 10 | Do not claim separate breakfast when hotel folio shows breakfast included |
| Lunch | Reimbursable during business travel or approved offsite meetings | Yes if above EUR 10 | Office cafeteria lunch at home location is not reimbursable |
| Dinner | Reimbursable during overnight business travel or late return after 20:00 | Yes if above EUR 10 | Alcohol must be removed unless client entertainment was pre-approved |
| Snacks and coffee | Allowed only when part of a documented meeting or travel day | Yes if above EUR 10 | Daily personal coffee is not reimbursable |  
Alcohol rule:  
Alcohol is not reimbursable for ordinary employee meals. It may be reimbursed only for pre-approved client entertainment with attendee list and business purpose.  
Tips are reimbursable up to 10% of the pre-tax meal amount where tipping is customary. Tips above 10% require manager approval and a short explanation.
```

### expense-policy-aead3745bd:chunk:00005

- strategy: `markdown_header+section_as_chunk`
- tokens: `176` section='4. Client Entertainment and Hospitality'
- source_block_ids: `["expense-policy-aead3745bd:00034", "expense-policy-aead3745bd:00035", "expense-policy-aead3745bd:00036"]`

```text
## 4. Client Entertainment and Hospitality  
Client entertainment is a stricter category than meals. It requires evidence of a real business purpose and cannot be used to bypass meal caps for ordinary team dinners.  
| Scenario | Approval required before expense? | Required evidence | Default treatment |
| --- | --- | --- | --- |
| Client dinner below EUR 120 total | No, unless alcohol is included | Receipt, attendee names, business purpose | Reimbursable if reasonable |
| Client dinner above EUR 120 total | Yes | Receipt, attendee list, agenda or opportunity reference | Manual review |
| Alcohol with client meal | Yes | Pre-approval, attendee list, business purpose | Not reimbursable without pre-approval |
| Team celebration | Yes if above EUR 50 per person | Manager approval, attendee count, cost center | Employee morale budget, not travel expense |
```

### expense-policy-aead3745bd:chunk:00006

- strategy: `markdown_header+section_as_chunk`
- tokens: `171` section='5. Local Transport, Taxi, Parking, and Public Transit'
- source_block_ids: `["expense-policy-aead3745bd:00037", "expense-policy-aead3745bd:00038", "expense-policy-aead3745bd:00039", "expense-policy-aead3745bd:00040", "expense-policy-aead3745bd:00041", "expense-policy-aead3745bd:00042", "expense-policy-aead3745bd:00043"]`

```text
## 5. Local Transport, Taxi, Parking, and Public Transit  
Employees should prefer public transport when safe and practical. Taxi rules depend on city and time threshold in the Per Diem Caps spreadsheet. Taxi claims must include origin, destination, date, and business purpose.  
- Taxi from airport to hotel is reimbursable if public transport is unavailable, impractical due to luggage, or travel occurs after the city-specific after-hours threshold.  
- Taxi between office and home is normally not reimbursable unless there is approved overtime ending after 22:00 or a safety concern.  
- Ride-hailing receipts are accepted if they show route or pickup/dropoff information.  
- Parking is reimbursable only during approved business travel or client meetings.  
- Traffic fines, speeding tickets, and private parking violations are never reimbursable.
```

### expense-policy-aead3745bd:chunk:00007

- strategy: `markdown_header+section_as_chunk`
- tokens: `133` section='6. Private Car and Mileage'
- source_block_ids: `["expense-policy-aead3745bd:00044", "expense-policy-aead3745bd:00045", "expense-policy-aead3745bd:00046"]`

```text
## 6. Private Car and Mileage  
Private car use should be pre-approved when the one-way distance exceeds 150 km. Mileage rates are maintained in the spreadsheet because they may change with local tax rules.  
| Vehicle type | Evidence | Notes |
| --- | --- | --- |
| Private car | Route, distance, business purpose, approval if above 150 km one way | Fuel receipts cannot be claimed separately when mileage is claimed |
| Rental car | Rental agreement, fuel receipt, approval if above compact class | Insurance upgrades require business justification |
| Company car | Trip log where required | Do not claim private mileage reimbursement for company car trips |
```

### expense-policy-aead3745bd:chunk:00008

- strategy: `markdown_header+section_as_chunk`
- tokens: `134` section='7. Digital Tools and Submission Rules'
- source_block_ids: `["expense-policy-aead3745bd:00047", "expense-policy-aead3745bd:00048", "expense-policy-aead3745bd:00049", "expense-policy-aead3745bd:00050", "expense-policy-aead3745bd:00051", "expense-policy-aead3745bd:00052"]`

```text
## 7. Digital Tools and Submission Rules  
Expense claims must be submitted within 30 calendar days after the trip end date. The preferred submission format is the company expense portal. Each claim should include category, cost center, trip purpose, source currency, and supporting evidence.  
- Use the exchange rate from the Finance monthly table, not a random card statement rate, unless Finance explicitly asks for the card statement.  
- Split mixed receipts into reimbursable and non-reimbursable portions.  
- Submit hotel, meal, taxi, and flight evidence as separate line items when possible.  
- Do not upload full passport scans unless explicitly requested by Travel Security.
```

### expense-policy-aead3745bd:chunk:00009

- strategy: `markdown_header+section_as_chunk`
- tokens: `123` section='8. Non-Reimbursable Expenses'
- source_block_ids: `["expense-policy-aead3745bd:00053", "expense-policy-aead3745bd:00054", "expense-policy-aead3745bd:00055", "expense-policy-aead3745bd:00056", "expense-policy-aead3745bd:00057", "expense-policy-aead3745bd:00058", "expense-policy-aead3745bd:00059", "expense-policy-aead3745bd:00060"]`

```text
## 8. Non-Reimbursable Expenses  
The following are normally not reimbursable:  
- Alcohol without pre-approved client entertainment classification.  
- Mini-bar, movies, spa, gym day passes, and personal hotel services.  
- Traffic fines, penalties, private parking violations, and lost ticket fees.  
- Personal clothing, luggage, headphones, chargers, toiletries, and travel accessories.  
- Airline seat upgrades, priority boarding, lounge access, and extra legroom unless approved for medical or business reasons.  
- Expenses submitted more than 90 days late without Finance exception approval.
```

### expense-policy-aead3745bd:chunk:00010

- strategy: `markdown_header+section_as_chunk`
- tokens: `55` section='9. FAQ'
- source_block_ids: `["expense-policy-aead3745bd:00061", "expense-policy-aead3745bd:00062", "expense-policy-aead3745bd:00063"]`

```text
## 9. FAQ  
### Can I claim dinner in Vienna if the receipt includes wine?  
You may claim the reimbursable food portion up to the applicable meal cap, but the wine must be removed unless the dinner was approved as client entertainment before the expense occurred.
```

### expense-policy-aead3745bd:chunk:00011

- strategy: `markdown_header+section_as_chunk`
- tokens: `32` section='Can I use my credit card statement instead of a receipt?'
- source_block_ids: `["expense-policy-aead3745bd:00064", "expense-policy-aead3745bd:00065"]`

```text
### Can I use my credit card statement instead of a receipt?  
No. A card statement proves payment but does not prove business purpose or item-level eligibility.
```

### expense-policy-aead3745bd:chunk:00012

- strategy: `markdown_header+section_as_chunk`
- tokens: `43` section='What if the local cap is lower than the actual hotel price during a conference?'
- source_block_ids: `["expense-policy-aead3745bd:00066", "expense-policy-aead3745bd:00067"]`

```text
### What if the local cap is lower than the actual hotel price during a conference?  
The claim may be reimbursed above cap only if the employee obtained pre-approval or documented that no reasonable alternatives were available.
```

### expense-policy-aead3745bd:chunk:00013

- strategy: `markdown_header+section_as_chunk`
- tokens: `59` section='What if the spreadsheet and HTML policy disagree?'
- source_block_ids: `["expense-policy-aead3745bd:00068", "expense-policy-aead3745bd:00069", "expense-policy-aead3745bd:00070"]`

```text
### What if the spreadsheet and HTML policy disagree?  
Use the spreadsheet for numeric caps and this HTML policy for evidence requirements. If the conflict concerns approval authority, use the Travel Policy PDF first.  
Atlas Mobility Group synthetic policy corpus for local RAG demo. Generated for learning and evaluation only.
```
