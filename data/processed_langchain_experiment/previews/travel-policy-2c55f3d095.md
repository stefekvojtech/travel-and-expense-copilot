# LangChain Chunk Preview: travel_policy.pdf

- doc_id: `travel-policy-2c55f3d095`
- source_path: `data/raw/travel_policy.pdf`
- loader: `PyPDFLoader`
- loaded_documents: `4`
- chunks: `7`

## Sample Chunks

### travel-policy-2c55f3d095:lc-chunk:00001

- strategy: `recursive_tiktoken`
- tokens: `572` pages=[1]

```text
Atlas Mobility Group synthetic policy corpus - Travel Policy 2026
Page 1
Atlas Mobility Group
 Travel Policy 2026
Document type: Synthetic internal travel policy PDF | Owner: Global Mobility & Finance Operations | Version: TRV-2026.1
| Effective: 2026-01-01
This synthetic policy is designed for a local RAG project. It contains realistic sections, evidence rules, approval thresholds,
and tables for testing chunking, table extraction, metadata, retrieval, context assembly, reranking, source priority,
groundedness, abstention, and tool use.
1. Policy Intent and Scope
This policy defines how employees and eligible contractors book business travel, document trips, select transport, obtain
approval, and submit travel-related claims. It applies to domestic and international business travel paid or reimbursed by
Atlas Mobility Group.
The policy does not replace country-specific tax rules, immigration requirements, security guidance, or written Finance
exceptions. If local law imposes stricter evidence or reporting duties, the stricter requirement applies.
For numeric reimbursement caps such as meal caps, hotel caps, mileage rates, and taxi after-hours thresholds, use the Per
Diem Caps spre
```

### travel-policy-2c55f3d095:lc-chunk:00002

- strategy: `recursive_tiktoken`
- tokens: `233` pages=[1]

```text
deviations.
 Finance Operations: maintain expense categories, caps, audit controls, reimbursement timing, and exception processing.
 Travel Security: advise on security-sensitive destinations, medical risk, and emergency travel changes.
3. Booking Rules
Employees must use the approved travel portal for flights, hotels, and rail bookings unless the portal is unavailable or the
traveler receives written approval to book outside the portal. Bookings made outside the portal must still follow policy caps
and evidence requirements.
The employee should normally select the lowest logical fare or rate. Lowest logical means a reasonable balance of price,
total travel time, safety, schedule, luggage needs, and meeting commitments. A cheaper option that creates an excessive
layover, late-night arrival without safe onward transport, or missed business meeting is not considered logical.
3.1 Advance Booking
 Domestic rail or short-haul flights should be booked at least 7 calendar days before travel when practical.
 International flights should be booked at least 14 calendar days before travel when practical.
 Conference hotels should be booked as soon as the event is approved because above-c
```

### travel-policy-2c55f3d095:lc-chunk:00003

- strategy: `recursive_tiktoken`
- tokens: `581` pages=[2]

```text
Atlas Mobility Group synthetic policy corpus - Travel Policy 2026
Page 2
 Last-minute travel is allowed for urgent business needs but may require manager explanation during audit.
4. Approval Matrix
The table below is intentionally included so the PDF is not just plain paragraphs. A good RAG pipeline should keep row
context and section metadata.
Travel or expense scenario
Default approval before
booking
Approver
Required evidence
Domestic trip under EUR 500 total
No, if within policy
Line manager can audit
afterwards
Trip purpose, receipt or booking evidence
International trip
Yes
Line manager
Trip purpose, destination, dates, estimated
cost
Hotel above city cap
Yes
Cost center owner
Hotel comparison, reason for above-cap
stay
Business class intercontinental flight
above 6 hours
Yes
Cost center owner
Flight duration, business reason, cost
comparison
Client entertainment above EUR 120
Yes
Cost center owner or Sales
VP
Attendee list, business purpose, receipt
Taxi before after-hours threshold
Only if exception applies
Line manager
Origin, destination, reason public transport
was not practical
Travel to high-risk destination
Yes
Travel Security + line
manager
Security approval, itine
```

### travel-policy-2c55f3d095:lc-chunk:00004

- strategy: `recursive_tiktoken`
- tokens: `242` pages=[2]

```text
control.
6. Rail, Public Transport, Taxi, and Rental Car
Rail is preferred over short-haul flights when total travel time is reasonable and the destination is reachable with reliable
service. Public transport is preferred over taxi when safe and practical.
Taxi or ride-hailing services are reimbursable only when public transport is unavailable, impractical due to luggage, unsafe,
or when travel occurs after the city-specific after-hours threshold in the Per Diem Caps spreadsheet.
Rental cars require pre-approval unless they are part of a customer visit, plant visit, field operation, or location without
reliable public transport. Compact or mid-size category is the default. Luxury, SUV, or premium class requires cost center
owner approval.
6.1 Taxi Evidence
 Taxi claims must show date, vendor, amount, currency, origin or pickup, destination or drop-off, and business purpose.
 If the receipt does not show route information, the employee must enter origin and destination manually in the claim.
 Taxi between home and office is normally not reimbursable unless approved overtime ends after 22:00, public transport is
unsafe, or Travel Security approves.
7. Hotels and Accommodation
```

### travel-policy-2c55f3d095:lc-chunk:00005

- strategy: `recursive_tiktoken`
- tokens: `563` pages=[3]

```text
Atlas Mobility Group synthetic policy corpus - Travel Policy 2026
Page 3
Hotels must be booked through the approved portal when available. The traveler should choose a hotel near the business
location when total cost is reasonable. The lodging cap for each city is maintained in the Per Diem Caps spreadsheet.
If the hotel price exceeds the cap, reimbursement is allowed only when there is pre-approval or when the employee
documents that no reasonable alternative was available. Examples include conference hotels, sold-out city events, weather
disruption, or safety constraints.
7.1 Hotel Evidence
 A hotel folio must show guest name, property, city, stay dates, nightly rate or room nights, taxes, and total amount.
 A booking confirmation is not sufficient if it does not prove payment.
 Mini-bar, movies, spa, laundry for trips shorter than five nights, and personal services are not reimbursable.
 Breakfast cannot be claimed separately when the hotel folio shows breakfast included in the rate.
8. Meals, Subsistence, and Entertainment
Meal reimbursement is governed by the Expense Policy HTML page and numeric caps in the Per Diem Caps spreadsheet.
The travel policy defines when a meal i
```

### travel-policy-2c55f3d095:lc-chunk:00006

- strategy: `recursive_tiktoken`
- tokens: `313` pages=[3]

```text
date consistency, route reasonableness, alcohol removal, missing receipt declarations, and source-currency verification.
9.1 Missing Evidence
 Missing receipt declarations are allowed only when the expense is otherwise reasonable and the employee explains why
the receipt is unavailable.
 Missing receipt declarations above EUR 25 require manager approval.
 Repeated missing evidence may lead to reimbursement refusal or mandatory manual review for future claims.
10. Non-Reimbursable Travel Items
 Traffic fines, speeding tickets, parking violations, lost ticket fees, and penalties.
 Mini-bar, hotel movies, spa, gym day passes, personal laundry for short trips, and personal hotel services.
 Personal clothing, luggage for private use, headphones, chargers, toiletries, and travel accessories.
 Airline seat upgrades, lounge access, priority boarding, extra legroom, and premium services unless approved.
 Expenses that are primarily private, family-related, recreational, or unrelated to the business purpose.
11. Worked Examples
Case
Likely result
Reason
Vienna dinner: food EUR 32, wine EUR
8, ordinary travel meal
Food reimbursable, wine
removed
Food is below Vienna cap; alcohol is no
```

### travel-policy-2c55f3d095:lc-chunk:00007

- strategy: `recursive_tiktoken`
- tokens: `171` pages=[4]

```text
Atlas Mobility Group synthetic policy corpus - Travel Policy 2026
Page 4
Case
Likely result
Reason
Business class flight Vienna to New
York, 9 hours, no approval
Manual review or rejection
Business class requires pre-approval
Hotel breakfast included, separate cafe
breakfast claimed
Not reimbursable
Duplicate breakfast claim
12. RAG Notes for Builders
This PDF intentionally mixes paragraphs, bullets, and tables. Good retrieval should preserve section metadata, page
number, policy version, and table row context. It should not answer from general knowledge when policy evidence is missing.
Recommended metadata values for chunks from this PDF include doc_type=pdf, source_name=travel_policy.pdf,
policy_owner=Global Mobility & Finance Operations, effective_date=2026-01-01, and section_path based on headings.
```
