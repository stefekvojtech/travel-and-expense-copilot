# Chunk Preview: Travel Policy

- doc_id: `travel-policy-2c55f3d095`
- source_path: `data/raw/travel_policy.pdf`
- doc_type: `pdf`
- chunks: `22`

## Chunks

### travel-policy-2c55f3d095:chunk:00001

- order: `1`
- strategy: `plain_text+section_as_chunk`
- tokens: `100` pages=[1]
- source_block_ids: `["travel-policy-2c55f3d095:00001"]`
- metadata: `{}`

```text
Atlas Mobility Group Travel Policy 2026 Document type: Synthetic internal travel policy PDF | Owner: Global Mobility & Finance Operations | Version: TRV-2026.1 | Effective: 2026-01-01 This synthetic policy is designed for a local RAG project. It contains realistic sections, evidence rules, approval thresholds, and tables for testing chunking, table extraction, metadata, retrieval, context assembly, reranking, source priority, groundedness, abstention, and tool use.
```

### travel-policy-2c55f3d095:chunk:00002

- order: `2`
- strategy: `markdown_header+section_as_chunk`
- tokens: `149` pages=[1] section='1. Policy Intent and Scope'
- source_block_ids: `["travel-policy-2c55f3d095:00002", "travel-policy-2c55f3d095:00003"]`
- metadata: `{}`

```text
## 1. Policy Intent and Scope  
This policy defines how employees and eligible contractors book business travel, document trips, select transport, obtain approval, and submit travel-related claims. It applies to domestic and international business travel paid or reimbursed by Atlas Mobility Group. The policy does not replace country-specific tax rules, immigration requirements, security guidance, or written Finance exceptions. If local law imposes stricter evidence or reporting duties, the stricter requirement applies. For numeric reimbursement caps such as meal caps, hotel caps, mileage rates, and taxi after-hours thresholds, use the Per Diem Caps spreadsheet. For receipt evidence and reimbursement submission rules, use the Expense Policy HTML page. For travel logistics and approval authority, this Travel Policy PDF is the governing source.
```

### travel-policy-2c55f3d095:chunk:00003

- order: `3`
- strategy: `markdown_header+section_as_chunk`
- tokens: `155` pages=[1] section='1.1 Source Priority'
- source_block_ids: `["travel-policy-2c55f3d095:00004", "travel-policy-2c55f3d095:00005", "travel-policy-2c55f3d095:00006"]`
- metadata: `{"table_indexes_on_page": [1]}`

```text
### 1.1 Source Priority  
#### Extracted Table 1 (Page 1)  
| Priority | Source | Use it for | Example |
| --- | --- | --- | --- |
| 1 | Local law and tax rule | Mandatory legal requirements | VAT invoice rules, tax deductibility |
| 2 | Written pre-approval | Approved exceptions | Hotel above cap due to conference shortage |
| 3 | Travel Policy PDF | Travel logistics, approval authority, booking class, travel evidence | Business class approval |
| 4 | Expense Policy HTML | Evidence requirements, submission rules, reimbursable categories | Receipt over EUR 10 |
| 5 | Per Diem Caps XLSX | Numeric city and country caps and thresholds | Berlin hotel cap |
```

### travel-policy-2c55f3d095:chunk:00004

- order: `4`
- strategy: `markdown_header+section_as_chunk`
- tokens: `124` pages=[1] section='2. Roles and Responsibilities'
- source_block_ids: `["travel-policy-2c55f3d095:00007", "travel-policy-2c55f3d095:00008", "travel-policy-2c55f3d095:00009", "travel-policy-2c55f3d095:00010", "travel-policy-2c55f3d095:00011", "travel-policy-2c55f3d095:00012", "travel-policy-2c55f3d095:00013", "travel-policy-2c55f3d095:00014", "travel-policy-2c55f3d095:00015"]`
- metadata: `{}`

```text
## 2. Roles and Responsibilities  
- Employee: book travel through approved channels, keep evidence, submit claims on time, and split mixed receipts  
accurately.  
- Line manager: confirm business purpose, approve travel when required, and reject expenses that lack a valid business  
reason.  
- Cost center owner: approve high-cost travel, premium cabin exceptions, client entertainment above threshold, and policy  
deviations.  
- Finance Operations: maintain expense categories, caps, audit controls, reimbursement timing, and exception processing.  
- Travel Security: advise on security-sensitive destinations, medical risk, and emergency travel changes.
```

### travel-policy-2c55f3d095:chunk:00005

- order: `5`
- strategy: `markdown_header+section_as_chunk`
- tokens: `117` pages=[1] section='3. Booking Rules'
- source_block_ids: `["travel-policy-2c55f3d095:00016", "travel-policy-2c55f3d095:00017"]`
- metadata: `{}`

```text
## 3. Booking Rules  
Employees must use the approved travel portal for flights, hotels, and rail bookings unless the portal is unavailable or the traveler receives written approval to book outside the portal. Bookings made outside the portal must still follow policy caps and evidence requirements. The employee should normally select the lowest logical fare or rate. Lowest logical means a reasonable balance of price, total travel time, safety, schedule, luggage needs, and meeting commitments. A cheaper option that creates an excessive layover, late-night arrival without safe onward transport, or missed business meeting is not considered logical.
```

### travel-policy-2c55f3d095:chunk:00006

- order: `6`
- strategy: `markdown_header+section_as_chunk`
- tokens: `96` pages=[1, 2] section='3.1 Advance Booking'
- source_block_ids: `["travel-policy-2c55f3d095:00018", "travel-policy-2c55f3d095:00019", "travel-policy-2c55f3d095:00020", "travel-policy-2c55f3d095:00021", "travel-policy-2c55f3d095:00022", "travel-policy-2c55f3d095:00023"]`
- metadata: `{}`

```text
### 3.1 Advance Booking  
- Domestic rail or short-haul flights should be booked at least 7 calendar days before travel when practical.  
- International flights should be booked at least 14 calendar days before travel when practical.  
- Conference hotels should be booked as soon as the event is approved because above-cap hotel exceptions require  
evidence that reasonable alternatives were unavailable.  
- Last-minute travel is allowed for urgent business needs but may require manager explanation during audit.
```

### travel-policy-2c55f3d095:chunk:00007

- order: `7`
- strategy: `markdown_header+section_as_chunk`
- tokens: `35` pages=[2] section='4. Approval Matrix'
- source_block_ids: `["travel-policy-2c55f3d095:00024", "travel-policy-2c55f3d095:00025"]`
- metadata: `{}`

```text
## 4. Approval Matrix  
The table below is intentionally included so the PDF is not just plain paragraphs. A good RAG pipeline should keep row context and section metadata.
```

### travel-policy-2c55f3d095:chunk:00008

- order: `8`
- strategy: `markdown_header+section_as_chunk`
- tokens: `208` pages=[2] section='4. Approval Matrix'
- source_block_ids: `["travel-policy-2c55f3d095:00026", "travel-policy-2c55f3d095:00027"]`
- metadata: `{"table_indexes_on_page": [1]}`

```text
#### Extracted Table 1 (Page 2)  
| Travel or expense scenario | Default approval before booking | Approver | Required evidence |
| --- | --- | --- | --- |
| Domestic trip under EUR 500 total | No, if within policy | Line manager can audit afterwards | Trip purpose, receipt or booking evidence |
| International trip | Yes | Line manager | Trip purpose, destination, dates, estimated cost |
| Hotel above city cap | Yes | Cost center owner | Hotel comparison, reason for above-cap stay |
| Business class intercontinental flight above 6 hours | Yes | Cost center owner | Flight duration, business reason, cost comparison |
| Client entertainment above EUR 120 | Yes | Cost center owner or Sales VP | Attendee list, business purpose, receipt |
| Taxi before after-hours threshold | Only if exception applies | Line manager | Origin, destination, reason public transport was not practical |
| Travel to high-risk destination | Yes | Travel Security + line manager | Security approval, itinerary, emergency contact |
```

### travel-policy-2c55f3d095:chunk:00009

- order: `9`
- strategy: `markdown_header+section_as_chunk`
- tokens: `111` pages=[2] section='5. Flights'
- source_block_ids: `["travel-policy-2c55f3d095:00028", "travel-policy-2c55f3d095:00029"]`
- metadata: `{}`

```text
## 5. Flights  
Economy class is the default cabin for all flights. Premium economy may be selected when the flight duration exceeds 4 hours and the price difference is reasonable. Business class requires pre-approval and is limited to intercontinental trips above 6 hours or documented medical, security, or critical business need. Travelers must keep a boarding pass or equivalent proof of travel. A booking confirmation alone is not enough to prove that the passenger travelled. If the airline does not provide a boarding pass, an airline travel certificate may be used.
```

### travel-policy-2c55f3d095:chunk:00010

- order: `10`
- strategy: `markdown_header+section_as_chunk`
- tokens: `121` pages=[2] section='5.1 Flight Reimbursement Restrictions'
- source_block_ids: `["travel-policy-2c55f3d095:00030", "travel-policy-2c55f3d095:00031", "travel-policy-2c55f3d095:00032", "travel-policy-2c55f3d095:00033", "travel-policy-2c55f3d095:00034", "travel-policy-2c55f3d095:00035", "travel-policy-2c55f3d095:00036"]`
- metadata: `{}`

```text
### 5.1 Flight Reimbursement Restrictions  
- Priority boarding is not reimbursable unless required due to business-critical timing or approved medical need.  
- Lounge access is not reimbursable by default.  
- Seat selection fees are reimbursable only when required for a disability, medical need, or documented work requirement.  
- Baggage fees are reimbursable when the baggage is needed for business equipment, travel length, or customer materials.  
- Airline change fees are reimbursable only when the change is caused by business need or disruption outside the traveler's  
control.
```

### travel-policy-2c55f3d095:chunk:00011

- order: `11`
- strategy: `markdown_header+section_as_chunk`
- tokens: `143` pages=[2] section='6. Rail, Public Transport, Taxi, and Rental Car'
- source_block_ids: `["travel-policy-2c55f3d095:00037", "travel-policy-2c55f3d095:00038"]`
- metadata: `{}`

```text
## 6. Rail, Public Transport, Taxi, and Rental Car  
Rail is preferred over short-haul flights when total travel time is reasonable and the destination is reachable with reliable service. Public transport is preferred over taxi when safe and practical. Taxi or ride-hailing services are reimbursable only when public transport is unavailable, impractical due to luggage, unsafe, or when travel occurs after the city-specific after-hours threshold in the Per Diem Caps spreadsheet. Rental cars require pre-approval unless they are part of a customer visit, plant visit, field operation, or location without reliable public transport. Compact or mid-size category is the default. Luxury, SUV, or premium class requires cost center owner approval.
```

### travel-policy-2c55f3d095:chunk:00012

- order: `12`
- strategy: `markdown_header+section_as_chunk`
- tokens: `91` pages=[2] section='6.1 Taxi Evidence'
- source_block_ids: `["travel-policy-2c55f3d095:00039", "travel-policy-2c55f3d095:00040", "travel-policy-2c55f3d095:00041", "travel-policy-2c55f3d095:00042", "travel-policy-2c55f3d095:00043"]`
- metadata: `{}`

```text
### 6.1 Taxi Evidence  
- Taxi claims must show date, vendor, amount, currency, origin or pickup, destination or drop-off, and business purpose.  
- If the receipt does not show route information, the employee must enter origin and destination manually in the claim.  
- Taxi between home and office is normally not reimbursable unless approved overtime ends after 22:00, public transport is  
unsafe, or Travel Security approves.
```

### travel-policy-2c55f3d095:chunk:00013

- order: `13`
- strategy: `markdown_header+section_as_chunk`
- tokens: `100` pages=[2, 3] section='7. Hotels and Accommodation'
- source_block_ids: `["travel-policy-2c55f3d095:00044", "travel-policy-2c55f3d095:00045"]`
- metadata: `{}`

```text
## 7. Hotels and Accommodation  
Hotels must be booked through the approved portal when available. The traveler should choose a hotel near the business location when total cost is reasonable. The lodging cap for each city is maintained in the Per Diem Caps spreadsheet. If the hotel price exceeds the cap, reimbursement is allowed only when there is pre-approval or when the employee documents that no reasonable alternative was available. Examples include conference hotels, sold-out city events, weather disruption, or safety constraints.
```

### travel-policy-2c55f3d095:chunk:00014

- order: `14`
- strategy: `markdown_header+section_as_chunk`
- tokens: `97` pages=[3] section='7.1 Hotel Evidence'
- source_block_ids: `["travel-policy-2c55f3d095:00046", "travel-policy-2c55f3d095:00047", "travel-policy-2c55f3d095:00048", "travel-policy-2c55f3d095:00049", "travel-policy-2c55f3d095:00050"]`
- metadata: `{}`

```text
### 7.1 Hotel Evidence  
- A hotel folio must show guest name, property, city, stay dates, nightly rate or room nights, taxes, and total amount.  
- A booking confirmation is not sufficient if it does not prove payment.  
- Mini-bar, movies, spa, laundry for trips shorter than five nights, and personal services are not reimbursable.  
- Breakfast cannot be claimed separately when the hotel folio shows breakfast included in the rate.
```

### travel-policy-2c55f3d095:chunk:00015

- order: `15`
- strategy: `markdown_header+section_as_chunk`
- tokens: `103` pages=[3] section='8. Meals, Subsistence, and Entertainment'
- source_block_ids: `["travel-policy-2c55f3d095:00051", "travel-policy-2c55f3d095:00052"]`
- metadata: `{}`

```text
## 8. Meals, Subsistence, and Entertainment  
Meal reimbursement is governed by the Expense Policy HTML page and numeric caps in the Per Diem Caps spreadsheet. The travel policy defines when a meal is connected to travel. Meals are normally reimbursable during overnight business travel, approved offsite meetings, customer visits, or late return after 20:00. Alcohol is not reimbursable for ordinary employee meals. Alcohol may be reimbursed only as pre-approved client entertainment with attendee list and business purpose.
```

### travel-policy-2c55f3d095:chunk:00016

- order: `16`
- strategy: `markdown_header+section_as_chunk`
- tokens: `71` pages=[3] section='8.1 Client Entertainment'
- source_block_ids: `["travel-policy-2c55f3d095:00053", "travel-policy-2c55f3d095:00054", "travel-policy-2c55f3d095:00055", "travel-policy-2c55f3d095:00056", "travel-policy-2c55f3d095:00057"]`
- metadata: `{}`

```text
### 8.1 Client Entertainment  
- Client entertainment must have a clear business purpose and attendee list.  
- Client entertainment above EUR 120 total requires pre-approval.  
- Entertainment must not be used to bypass ordinary meal caps for team meals.  
- Alcohol with client meals requires pre-approval even when total cost is below EUR 120.
```

### travel-policy-2c55f3d095:chunk:00017

- order: `17`
- strategy: `markdown_header+section_as_chunk`
- tokens: `100` pages=[3] section='9. Expense Submission and Audit'
- source_block_ids: `["travel-policy-2c55f3d095:00058", "travel-policy-2c55f3d095:00059"]`
- metadata: `{}`

```text
## 9. Expense Submission and Audit  
Claims should be submitted within 30 calendar days after the trip end date. Finance may reject claims older than 90 days unless an exception is approved. Claims must include business purpose, category, date, vendor, currency, amount, and supporting evidence. Finance may audit any claim before or after reimbursement. Audit checks may include duplicate detection, cap validation, date consistency, route reasonableness, alcohol removal, missing receipt declarations, and source-currency verification.
```

### travel-policy-2c55f3d095:chunk:00018

- order: `18`
- strategy: `markdown_header+section_as_chunk`
- tokens: `64` pages=[3] section='9.1 Missing Evidence'
- source_block_ids: `["travel-policy-2c55f3d095:00060", "travel-policy-2c55f3d095:00061", "travel-policy-2c55f3d095:00062", "travel-policy-2c55f3d095:00063", "travel-policy-2c55f3d095:00064"]`
- metadata: `{}`

```text
### 9.1 Missing Evidence  
- Missing receipt declarations are allowed only when the expense is otherwise reasonable and the employee explains why  
the receipt is unavailable.  
- Missing receipt declarations above EUR 25 require manager approval.  
- Repeated missing evidence may lead to reimbursement refusal or mandatory manual review for future claims.
```

### travel-policy-2c55f3d095:chunk:00019

- order: `19`
- strategy: `markdown_header+section_as_chunk`
- tokens: `119` pages=[3] section='10. Non-Reimbursable Travel Items'
- source_block_ids: `["travel-policy-2c55f3d095:00065", "travel-policy-2c55f3d095:00066", "travel-policy-2c55f3d095:00067", "travel-policy-2c55f3d095:00068", "travel-policy-2c55f3d095:00069", "travel-policy-2c55f3d095:00070"]`
- metadata: `{}`

```text
## 10. Non-Reimbursable Travel Items  
- Traffic fines, speeding tickets, parking violations, lost ticket fees, and penalties.  
- Mini-bar, hotel movies, spa, gym day passes, personal laundry for short trips, and personal hotel services.  
- Personal clothing, luggage for private use, headphones, chargers, toiletries, and travel accessories.  
- Airline seat upgrades, lounge access, priority boarding, extra legroom, and premium services unless approved.  
- Expenses that are primarily private, family-related, recreational, or unrelated to the business purpose.
```

### travel-policy-2c55f3d095:chunk:00020

- order: `20`
- strategy: `markdown_header+section_as_chunk`
- tokens: `138` pages=[3] section='11. Worked Examples'
- source_block_ids: `["travel-policy-2c55f3d095:00071", "travel-policy-2c55f3d095:00072", "travel-policy-2c55f3d095:00073"]`
- metadata: `{"table_indexes_on_page": [1]}`

```text
## 11. Worked Examples  
#### Extracted Table 1 (Page 3)  
| Case | Likely result | Reason |
| --- | --- | --- |
| Vienna dinner: food EUR 32, wine EUR 8, ordinary travel meal | Food reimbursable, wine removed | Food is below Vienna cap; alcohol is not reimbursable without entertainment pre-approval |
| Berlin hotel EUR 175 per night | Within cap | Berlin hotel cap is maintained in XLSX and is EUR 180 |
| Prague taxi at 20:30 without safety issue | Usually not reimbursable | Prague after-hours threshold is 21:00 in XLSX |
```

### travel-policy-2c55f3d095:chunk:00021

- order: `21`
- strategy: `markdown_header+section_as_chunk`
- tokens: `74` pages=[4] section='11. Worked Examples'
- source_block_ids: `["travel-policy-2c55f3d095:00074", "travel-policy-2c55f3d095:00075"]`
- metadata: `{"table_indexes_on_page": [1]}`

```text
#### Extracted Table 1 (Page 4)  
| Case | Likely result | Reason |
| --- | --- | --- |
| Business class flight Vienna to New York, 9 hours, no approval | Manual review or rejection | Business class requires pre-approval |
| Hotel breakfast included, separate cafe breakfast claimed | Not reimbursable | Duplicate breakfast claim |
```

### travel-policy-2c55f3d095:chunk:00022

- order: `22`
- strategy: `markdown_header+section_as_chunk`
- tokens: `99` pages=[4] section='12. RAG Notes for Builders'
- source_block_ids: `["travel-policy-2c55f3d095:00076", "travel-policy-2c55f3d095:00077"]`
- metadata: `{}`

```text
## 12. RAG Notes for Builders  
This PDF intentionally mixes paragraphs, bullets, and tables. Good retrieval should preserve section metadata, page number, policy version, and table row context. It should not answer from general knowledge when policy evidence is missing. Recommended metadata values for chunks from this PDF include doc_type=pdf, source_name=travel_policy.pdf, policy_owner=Global Mobility & Finance Operations, effective_date=2026-01-01, and section_path based on headings.
```
