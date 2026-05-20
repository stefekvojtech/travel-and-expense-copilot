# Normalized Block Preview: Per Diem Caps

- doc_id: `per-diem-caps-1639db42ae`
- source_path: `data/raw/per_diem_caps.xlsx`
- doc_type: `xlsx`
- blocks: `105`

## Blocks

### per-diem-caps-1639db42ae:00001

- order: `1`
- type: `heading` section='README'
- metadata: `{}`

```text
## README
```

### per-diem-caps-1639db42ae:00002

- order: `2`
- type: `table_header` section='README'
- metadata: `{"row_number": 1}`

```text
Columns: Atlas Mobility Group - Per Diem Caps Workbook 2026, column_2
```

### per-diem-caps-1639db42ae:00003

- order: `3`
- type: `table_row` section='README'
- metadata: `{"row_number": 2}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Purpose
column_2: Synthetic data source for local RAG and agentic reimbursement demo.
```

### per-diem-caps-1639db42ae:00004

- order: `4`
- type: `table_row` section='README'
- metadata: `{"row_number": 3}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Version
column_2: PDC-2026.2
```

### per-diem-caps-1639db42ae:00005

- order: `5`
- type: `table_row` section='README'
- metadata: `{"row_number": 4}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Effective date
column_2: 2026-01-01
```

### per-diem-caps-1639db42ae:00006

- order: `6`
- type: `table_row` section='README'
- metadata: `{"row_number": 5}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Owner
column_2: Finance Operations
```

### per-diem-caps-1639db42ae:00007

- order: `7`
- type: `table_row` section='README'
- metadata: `{"row_number": 6}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Source priority
column_2: Use this workbook for numeric caps, thresholds, and deterministic lookups. Use PDF/HTML for narrative policy rules.
```

### per-diem-caps-1639db42ae:00008

- order: `8`
- type: `table_row` section='README'
- metadata: `{"row_number": 7}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: RAG note
column_2: Every sheet is intentionally structured differently so loaders must preserve sheet name, row context, and metadata.
```

### per-diem-caps-1639db42ae:00009

- order: `9`
- type: `table_row` section='README'
- metadata: `{"row_number": 8}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Recommended metadata
column_2: doc_type=xlsx, source_name=per_diem_caps.xlsx, sheet=<sheet>, effective_date=2026-01-01
```

### per-diem-caps-1639db42ae:00010

- order: `10`
- type: `table_row` section='README'
- metadata: `{"row_number": 9}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: Sheets
column_2:
```

### per-diem-caps-1639db42ae:00011

- order: `11`
- type: `table_row` section='README'
- metadata: `{"row_number": 10}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: PerDiemCaps
column_2: Meal, hotel, taxi, and laundry caps by country/city.
```

### per-diem-caps-1639db42ae:00012

- order: `12`
- type: `table_row` section='README'
- metadata: `{"row_number": 11}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: TaxiRules
column_2: After-hours thresholds and city-specific transport notes.
```

### per-diem-caps-1639db42ae:00013

- order: `13`
- type: `table_row` section='README'
- metadata: `{"row_number": 12}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: MileageRates
column_2: Private car mileage rates and approval thresholds.
```

### per-diem-caps-1639db42ae:00014

- order: `14`
- type: `table_row` section='README'
- metadata: `{"row_number": 13}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: ExchangeRates
column_2: Monthly finance exchange rates for claim conversion.
```

### per-diem-caps-1639db42ae:00015

- order: `15`
- type: `table_row` section='README'
- metadata: `{"row_number": 14}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: ApprovalMatrix
column_2: Numeric thresholds for approval routing.
```

### per-diem-caps-1639db42ae:00016

- order: `16`
- type: `table_row` section='README'
- metadata: `{"row_number": 15}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: ClaimExamples
column_2: Worked examples with formulas for reimbursement logic.
```

### per-diem-caps-1639db42ae:00017

- order: `17`
- type: `table_row` section='README'
- metadata: `{"row_number": 16}`

```text
Atlas Mobility Group - Per Diem Caps Workbook 2026: PolicyTags
column_2: Metadata tags useful for filtering and retrieval.
```

### per-diem-caps-1639db42ae:00018

- order: `18`
- type: `heading` section='PerDiemCaps'
- metadata: `{}`

```text
## PerDiemCaps
```

### per-diem-caps-1639db42ae:00019

- order: `19`
- type: `table_header` section='PerDiemCaps'
- metadata: `{"row_number": 1}`

```text
Columns: country_code, country, city, currency, meal_cap_breakfast, meal_cap_lunch, meal_cap_dinner, meal_cap_daily, hotel_cap_per_night, taxi_allowed_after, laundry_after_nights, notes, effective_date
```

### per-diem-caps-1639db42ae:00020

- order: `20`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 2}`

```text
country_code: AT
country: Austria
city: Vienna
currency: EUR
meal_cap_breakfast: 12
meal_cap_lunch: 24
meal_cap_dinner: 35
meal_cap_daily: 71
hotel_cap_per_night: 160
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Dinner cap excludes alcohol unless client entertainment was pre-approved.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00021

- order: `21`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 3}`

```text
country_code: AT
country: Austria
city: Graz
currency: EUR
meal_cap_breakfast: 10
meal_cap_lunch: 22
meal_cap_dinner: 32
meal_cap_daily: 64
hotel_cap_per_night: 135
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Lower hotel cap than Vienna; airport taxi needs route evidence.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00022

- order: `22`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 4}`

```text
country_code: AT
country: Austria
city: Linz
currency: EUR
meal_cap_breakfast: 10
meal_cap_lunch: 21
meal_cap_dinner: 31
meal_cap_daily: 62
hotel_cap_per_night: 125
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Standard Austrian regional cap.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00023

- order: `23`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 5}`

```text
country_code: CZ
country: Czechia
city: Prague
currency: CZK
meal_cap_breakfast: 250
meal_cap_lunch: 500
meal_cap_dinner: 700
meal_cap_daily: 1450
hotel_cap_per_night: 3000
taxi_allowed_after: 21:00
laundry_after_nights: 5
notes: Caps stored in local currency; convert with Finance monthly rate.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00024

- order: `24`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 6}`

```text
country_code: CZ
country: Czechia
city: Brno
currency: CZK
meal_cap_breakfast: 220
meal_cap_lunch: 450
meal_cap_dinner: 620
meal_cap_daily: 1290
hotel_cap_per_night: 2500
taxi_allowed_after: 21:00
laundry_after_nights: 5
notes: Taxi before 21:00 requires exception reason.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00025

- order: `25`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 7}`

```text
country_code: CZ
country: Czechia
city: Ostrava
currency: CZK
meal_cap_breakfast: 200
meal_cap_lunch: 420
meal_cap_dinner: 580
meal_cap_daily: 1200
hotel_cap_per_night: 2300
taxi_allowed_after: 21:00
laundry_after_nights: 5
notes: Regional rate; hotel above cap needs manager approval.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00026

- order: `26`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 8}`

```text
country_code: DE
country: Germany
city: Berlin
currency: EUR
meal_cap_breakfast: 14
meal_cap_lunch: 28
meal_cap_dinner: 40
meal_cap_daily: 82
hotel_cap_per_night: 180
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Conference hotel above cap can be approved with evidence.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00027

- order: `27`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 9}`

```text
country_code: DE
country: Germany
city: Munich
currency: EUR
meal_cap_breakfast: 15
meal_cap_lunch: 30
meal_cap_dinner: 45
meal_cap_daily: 90
hotel_cap_per_night: 210
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Higher lodging cap due to market rates.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00028

- order: `28`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 10}`

```text
country_code: DE
country: Germany
city: Frankfurt
currency: EUR
meal_cap_breakfast: 14
meal_cap_lunch: 29
meal_cap_dinner: 42
meal_cap_daily: 85
hotel_cap_per_night: 190
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Airport taxi must include route or booking proof.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00029

- order: `29`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 11}`

```text
country_code: CH
country: Switzerland
city: Zurich
currency: CHF
meal_cap_breakfast: 18
meal_cap_lunch: 36
meal_cap_dinner: 55
meal_cap_daily: 109
hotel_cap_per_night: 240
taxi_allowed_after: 22:30
laundry_after_nights: 4
notes: Caps are CHF; report in source currency and convert to EUR.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00030

- order: `30`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 12}`

```text
country_code: CH
country: Switzerland
city: Basel
currency: CHF
meal_cap_breakfast: 16
meal_cap_lunch: 33
meal_cap_dinner: 50
meal_cap_daily: 99
hotel_cap_per_night: 210
taxi_allowed_after: 22:30
laundry_after_nights: 4
notes: Client entertainment requires attendee list.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00031

- order: `31`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 13}`

```text
country_code: NL
country: Netherlands
city: Amsterdam
currency: EUR
meal_cap_breakfast: 13
meal_cap_lunch: 27
meal_cap_dinner: 39
meal_cap_daily: 79
hotel_cap_per_night: 175
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Taxi from Schiphol usually requires business reason.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00032

- order: `32`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 14}`

```text
country_code: FR
country: France
city: Paris
currency: EUR
meal_cap_breakfast: 15
meal_cap_lunch: 32
meal_cap_dinner: 46
meal_cap_daily: 93
hotel_cap_per_night: 220
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Hotel above cap often reviewed manually during trade fairs.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00033

- order: `33`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 15}`

```text
country_code: GB
country: United Kingdom
city: London
currency: GBP
meal_cap_breakfast: 13
meal_cap_lunch: 30
meal_cap_dinner: 48
meal_cap_daily: 91
hotel_cap_per_night: 210
taxi_allowed_after: 22:30
laundry_after_nights: 4
notes: Caps are GBP; use monthly Finance exchange rate.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00034

- order: `34`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 16}`

```text
country_code: US
country: United States
city: New York
currency: USD
meal_cap_breakfast: 18
meal_cap_lunch: 36
meal_cap_dinner: 60
meal_cap_daily: 114
hotel_cap_per_night: 280
taxi_allowed_after: 22:00
laundry_after_nights: 4
notes: Tips are reimbursable within reason but must be itemized.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00035

- order: `35`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 17}`

```text
country_code: US
country: United States
city: Houston
currency: USD
meal_cap_breakfast: 15
meal_cap_lunch: 30
meal_cap_dinner: 48
meal_cap_daily: 93
hotel_cap_per_night: 210
taxi_allowed_after: 22:00
laundry_after_nights: 4
notes: Rental car is common for plant visits but still needs business purpose.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00036

- order: `36`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 18}`

```text
country_code: PL
country: Poland
city: Warsaw
currency: PLN
meal_cap_breakfast: 50
meal_cap_lunch: 95
meal_cap_dinner: 140
meal_cap_daily: 285
hotel_cap_per_night: 520
taxi_allowed_after: 21:30
laundry_after_nights: 5
notes: Local taxi apps accepted with route evidence.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00037

- order: `37`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 19}`

```text
country_code: HU
country: Hungary
city: Budapest
currency: HUF
meal_cap_breakfast: 4500
meal_cap_lunch: 9000
meal_cap_dinner: 13000
meal_cap_daily: 26500
hotel_cap_per_night: 48000
taxi_allowed_after: 21:30
laundry_after_nights: 5
notes: Cash receipts must show vendor and date.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00038

- order: `38`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 20}`

```text
country_code: IT
country: Italy
city: Milan
currency: EUR
meal_cap_breakfast: 14
meal_cap_lunch: 30
meal_cap_dinner: 44
meal_cap_daily: 88
hotel_cap_per_night: 205
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: City tax reimbursable when shown on hotel folio.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00039

- order: `39`
- type: `table_row` section='PerDiemCaps'
- metadata: `{"row_number": 21}`

```text
country_code: ES
country: Spain
city: Madrid
currency: EUR
meal_cap_breakfast: 12
meal_cap_lunch: 26
meal_cap_dinner: 38
meal_cap_daily: 76
hotel_cap_per_night: 165
taxi_allowed_after: 22:00
laundry_after_nights: 5
notes: Late dinner is normal locally but alcohol still excluded.
effective_date: 2026-01-01
```

### per-diem-caps-1639db42ae:00040

- order: `40`
- type: `heading` section='TaxiRules'
- metadata: `{}`

```text
## TaxiRules
```

### per-diem-caps-1639db42ae:00041

- order: `41`
- type: `table_header` section='TaxiRules'
- metadata: `{"row_number": 1}`

```text
Columns: country_code, city, default_after_hours_threshold, airport_to_city_allowed, home_to_office_allowed, requires_route_evidence, exception_keywords, audit_note
```

### per-diem-caps-1639db42ae:00042

- order: `42`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 2}`

```text
country_code: AT
city: Vienna
default_after_hours_threshold: 22:00
airport_to_city_allowed: Yes if luggage, late arrival, or public transport disruption
home_to_office_allowed: No, unless approved overtime after 22:00 or safety issue
requires_route_evidence: Yes
exception_keywords: luggage; late arrival; safety; strike; disruption
audit_note: Before 22:00 route evidence and exception reason are important.
```

### per-diem-caps-1639db42ae:00043

- order: `43`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 3}`

```text
country_code: CZ
city: Prague
default_after_hours_threshold: 21:00
airport_to_city_allowed: Yes if after threshold or public transport not practical
home_to_office_allowed: No, unless overtime after 22:00 or safety issue
requires_route_evidence: Yes
exception_keywords: luggage; unsafe; disruption; late return
audit_note: 20:30 is not after-hours in Prague under default rule.
```

### per-diem-caps-1639db42ae:00044

- order: `44`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 4}`

```text
country_code: CZ
city: Brno
default_after_hours_threshold: 21:00
airport_to_city_allowed: Yes if after threshold or public transport not practical
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: plant visit; luggage; unsafe
audit_note: Brno taxi claims often fail when business purpose is missing.
```

### per-diem-caps-1639db42ae:00045

- order: `45`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 5}`

```text
country_code: DE
city: Berlin
default_after_hours_threshold: 22:00
airport_to_city_allowed: Yes for late arrivals and heavy luggage
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: trade fair; late arrival; strike
audit_note: Public transit is expected unless exception applies.
```

### per-diem-caps-1639db42ae:00046

- order: `46`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 6}`

```text
country_code: DE
city: Munich
default_after_hours_threshold: 22:00
airport_to_city_allowed: Yes if after threshold or luggage
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: airport; luggage; client equipment
audit_note: Airport rides above EUR 90 require explanation.
```

### per-diem-caps-1639db42ae:00047

- order: `47`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 7}`

```text
country_code: CH
city: Zurich
default_after_hours_threshold: 22:30
airport_to_city_allowed: Yes if after threshold or client equipment
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: late arrival; equipment; safety
audit_note: High taxi costs are reviewed against public transit options.
```

### per-diem-caps-1639db42ae:00048

- order: `48`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 8}`

```text
country_code: FR
city: Paris
default_after_hours_threshold: 22:00
airport_to_city_allowed: Yes if after threshold, luggage, or strike
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: strike; unsafe; luggage
audit_note: Taxi receipts must include vendor and date.
```

### per-diem-caps-1639db42ae:00049

- order: `49`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 9}`

```text
country_code: GB
city: London
default_after_hours_threshold: 22:30
airport_to_city_allowed: Yes if after threshold, safety issue, or rail strike
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: rail strike; safety; equipment
audit_note: Black cab receipt without route needs manual route entry.
```

### per-diem-caps-1639db42ae:00050

- order: `50`
- type: `table_row` section='TaxiRules'
- metadata: `{"row_number": 10}`

```text
country_code: US
city: New York
default_after_hours_threshold: 22:00
airport_to_city_allowed: Yes, route evidence required
home_to_office_allowed: No
requires_route_evidence: Yes
exception_keywords: late arrival; client materials
audit_note: Tips above 20% require explanation in US cities.
```

### per-diem-caps-1639db42ae:00051

- order: `51`
- type: `heading` section='MileageRates'
- metadata: `{}`

```text
## MileageRates
```

### per-diem-caps-1639db42ae:00052

- order: `52`
- type: `table_header` section='MileageRates'
- metadata: `{"row_number": 1}`

```text
Columns: country_code, country, currency, private_car_rate_per_km, electric_car_rate_per_km, preapproval_distance_one_way_km, fuel_claim_separate_allowed, notes
```

### per-diem-caps-1639db42ae:00053

- order: `53`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 2}`

```text
country_code: AT
country: Austria
currency: EUR
private_car_rate_per_km: 0.42
electric_car_rate_per_km: 0.45
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Private mileage includes fuel, wear, and standard insurance.
```

### per-diem-caps-1639db42ae:00054

- order: `54`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 3}`

```text
country_code: CZ
country: Czechia
currency: CZK
private_car_rate_per_km: 6.2
electric_car_rate_per_km: 6.8
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Use local payroll/tax rate if different from Finance rate.
```

### per-diem-caps-1639db42ae:00055

- order: `55`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 4}`

```text
country_code: DE
country: Germany
currency: EUR
private_car_rate_per_km: 0.38
electric_car_rate_per_km: 0.42
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Long-distance private car trips need manager approval.
```

### per-diem-caps-1639db42ae:00056

- order: `56`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 5}`

```text
country_code: CH
country: Switzerland
currency: CHF
private_car_rate_per_km: 0.7
electric_car_rate_per_km: 0.72
preapproval_distance_one_way_km: 120
fuel_claim_separate_allowed: No
notes: Parking can be claimed separately with business purpose.
```

### per-diem-caps-1639db42ae:00057

- order: `57`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 6}`

```text
country_code: NL
country: Netherlands
currency: EUR
private_car_rate_per_km: 0.34
electric_car_rate_per_km: 0.38
preapproval_distance_one_way_km: 120
fuel_claim_separate_allowed: No
notes: Bike mileage is not covered in this workbook.
```

### per-diem-caps-1639db42ae:00058

- order: `58`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 7}`

```text
country_code: FR
country: France
currency: EUR
private_car_rate_per_km: 0.4
electric_car_rate_per_km: 0.44
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Tolls reimbursable with receipt if route was business-related.
```

### per-diem-caps-1639db42ae:00059

- order: `59`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 8}`

```text
country_code: GB
country: United Kingdom
currency: GBP
private_car_rate_per_km: 0.45
electric_car_rate_per_km: 0.45
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Use local HMRC-compliant value if Finance updates rate.
```

### per-diem-caps-1639db42ae:00060

- order: `60`
- type: `table_row` section='MileageRates'
- metadata: `{"row_number": 9}`

```text
country_code: US
country: United States
currency: USD
private_car_rate_per_km: 0.67
electric_car_rate_per_km: 0.67
preapproval_distance_one_way_km: 150
fuel_claim_separate_allowed: No
notes: Use IRS-compliant rate if Finance updates rate.
```

### per-diem-caps-1639db42ae:00061

- order: `61`
- type: `heading` section='ExchangeRates'
- metadata: `{}`

```text
## ExchangeRates
```

### per-diem-caps-1639db42ae:00062

- order: `62`
- type: `table_header` section='ExchangeRates'
- metadata: `{"row_number": 1}`

```text
Columns: month, currency, eur_rate, source, notes
```

### per-diem-caps-1639db42ae:00063

- order: `63`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 2}`

```text
month: 2026-01
currency: EUR
eur_rate: 1
source: Finance monthly table
notes: Base currency
```

### per-diem-caps-1639db42ae:00064

- order: `64`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 3}`

```text
month: 2026-01
currency: CZK
eur_rate: 0.04
source: Finance monthly table
notes: 25 CZK = 1 EUR equivalent
```

### per-diem-caps-1639db42ae:00065

- order: `65`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 4}`

```text
month: 2026-01
currency: CHF
eur_rate: 1.06
source: Finance monthly table
notes: Use for Swiss caps and claims
```

### per-diem-caps-1639db42ae:00066

- order: `66`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 5}`

```text
month: 2026-01
currency: GBP
eur_rate: 1.17
source: Finance monthly table
notes: Use for UK claims
```

### per-diem-caps-1639db42ae:00067

- order: `67`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 6}`

```text
month: 2026-01
currency: USD
eur_rate: 0.92
source: Finance monthly table
notes: Use for US claims
```

### per-diem-caps-1639db42ae:00068

- order: `68`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 7}`

```text
month: 2026-01
currency: PLN
eur_rate: 0.23
source: Finance monthly table
notes: Use for Poland claims
```

### per-diem-caps-1639db42ae:00069

- order: `69`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 8}`

```text
month: 2026-01
currency: HUF
eur_rate: 0.0026
source: Finance monthly table
notes: Use for Hungary claims
```

### per-diem-caps-1639db42ae:00070

- order: `70`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 9}`

```text
month: 2026-02
currency: EUR
eur_rate: 1
source: Finance monthly table
notes: Base currency
```

### per-diem-caps-1639db42ae:00071

- order: `71`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 10}`

```text
month: 2026-02
currency: CZK
eur_rate: 0.0396
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00072

- order: `72`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 11}`

```text
month: 2026-02
currency: CHF
eur_rate: 1.05
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00073

- order: `73`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 12}`

```text
month: 2026-02
currency: GBP
eur_rate: 1.16
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00074

- order: `74`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 13}`

```text
month: 2026-02
currency: USD
eur_rate: 0.93
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00075

- order: `75`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 14}`

```text
month: 2026-02
currency: PLN
eur_rate: 0.231
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00076

- order: `76`
- type: `table_row` section='ExchangeRates'
- metadata: `{"row_number": 15}`

```text
month: 2026-02
currency: HUF
eur_rate: 0.00255
source: Finance monthly table
notes: Monthly conversion rate
```

### per-diem-caps-1639db42ae:00077

- order: `77`
- type: `heading` section='ApprovalMatrix'
- metadata: `{}`

```text
## ApprovalMatrix
```

### per-diem-caps-1639db42ae:00078

- order: `78`
- type: `table_header` section='ApprovalMatrix'
- metadata: `{"row_number": 1}`

```text
Columns: scenario, threshold, currency, approval_required, approver, source_priority, notes
```

### per-diem-caps-1639db42ae:00079

- order: `79`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 2}`

```text
scenario: Client entertainment total
threshold: 120
currency: EUR
approval_required: Yes if above threshold
approver: Cost center owner or Sales VP
source_priority: Travel Policy PDF + Expense Policy HTML
notes: Requires attendee list and business purpose.
```

### per-diem-caps-1639db42ae:00080

- order: `80`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 3}`

```text
scenario: Missing receipt declaration
threshold: 25
currency: EUR
approval_required: Yes if above threshold
approver: Line manager
source_priority: Expense Policy HTML
notes: Repeated missing evidence can trigger manual review.
```

### per-diem-caps-1639db42ae:00081

- order: `81`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 4}`

```text
scenario: Hotel above city cap
threshold: 0
currency: N/A
approval_required: Yes if above applicable city cap
approver: Cost center owner
source_priority: PerDiemCaps + Travel Policy PDF
notes: Document lack of reasonable alternatives.
```

### per-diem-caps-1639db42ae:00082

- order: `82`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 5}`

```text
scenario: Private car one-way distance
threshold: 150
currency: km
approval_required: Yes if above threshold
approver: Line manager
source_priority: Expense Policy HTML + MileageRates
notes: Applies unless plant visit exception is documented.
```

### per-diem-caps-1639db42ae:00083

- order: `83`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 6}`

```text
scenario: Business class flight duration
threshold: 6
currency: hours
approval_required: Yes if intercontinental and above duration
approver: Cost center owner
source_priority: Travel Policy PDF
notes: Also requires business reason.
```

### per-diem-caps-1639db42ae:00084

- order: `84`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 7}`

```text
scenario: Late expense submission
threshold: 90
currency: days
approval_required: Yes for exception
approver: Finance Operations
source_priority: Expense Policy HTML + Travel Policy PDF
notes: Claims older than 90 days normally rejected.
```

### per-diem-caps-1639db42ae:00085

- order: `85`
- type: `table_row` section='ApprovalMatrix'
- metadata: `{"row_number": 8}`

```text
scenario: Team celebration per person
threshold: 50
currency: EUR
approval_required: Yes if above threshold
approver: Line manager or morale budget owner
source_priority: Expense Policy HTML
notes: Not normal travel expense category.
```

### per-diem-caps-1639db42ae:00086

- order: `86`
- type: `heading` section='ClaimExamples'
- metadata: `{}`

```text
## ClaimExamples
```

### per-diem-caps-1639db42ae:00087

- order: `87`
- type: `table_header` section='ClaimExamples'
- metadata: `{"row_number": 1}`

```text
Columns: claim_id, city, country_code, category, source_amount, currency, alcohol_amount, preapproved, cap_reference, cap_amount, fx_to_eur, converted_amount_eur, reimbursable_hint, notes
```

### per-diem-caps-1639db42ae:00088

- order: `88`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 2}`

```text
claim_id: C-001
city: Vienna
country_code: AT
category: Dinner
source_amount: 40
currency: EUR
alcohol_amount: 8
preapproved: No
cap_reference: Dinner cap
cap_amount: 35
fx_to_eur: 1
converted_amount_eur: 40
reimbursable_hint: 32
notes: Wine excluded; food portion 32 EUR below cap.
```

### per-diem-caps-1639db42ae:00089

- order: `89`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 3}`

```text
claim_id: C-002
city: Berlin
country_code: DE
category: Hotel
source_amount: 175
currency: EUR
alcohol_amount: 0
preapproved: N/A
cap_reference: Hotel cap
cap_amount: 180
fx_to_eur: 1
converted_amount_eur: 175
reimbursable_hint: 175
notes: Within cap.
```

### per-diem-caps-1639db42ae:00090

- order: `90`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 4}`

```text
claim_id: C-003
city: Prague
country_code: CZ
category: Taxi
source_amount: 650
currency: CZK
alcohol_amount: 0
preapproved: No
cap_reference: Taxi after-hours
cap_amount: 0
fx_to_eur: 0.04
converted_amount_eur: 26
reimbursable_hint: 26
notes: Eligibility depends on time threshold and exception reason.
```

### per-diem-caps-1639db42ae:00091

- order: `91`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 5}`

```text
claim_id: C-004
city: Zurich
country_code: CH
category: Hotel
source_amount: 260
currency: CHF
alcohol_amount: 0
preapproved: No
cap_reference: Hotel cap
cap_amount: 240
fx_to_eur: 1.06
converted_amount_eur: 275.6
reimbursable_hint: 254.4
notes: Above cap without approval; reimbursable hint capped.
```

### per-diem-caps-1639db42ae:00092

- order: `92`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 6}`

```text
claim_id: C-005
city: London
country_code: GB
category: Dinner
source_amount: 62
currency: GBP
alcohol_amount: 0
preapproved: No
cap_reference: Dinner cap
cap_amount: 48
fx_to_eur: 1.17
converted_amount_eur: 72.53999999999999
reimbursable_hint: 56.16
notes: Above meal cap; excess requires approval.
```

### per-diem-caps-1639db42ae:00093

- order: `93`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 7}`

```text
claim_id: C-006
city: New York
country_code: US
category: Dinner
source_amount: 58
currency: USD
alcohol_amount: 0
preapproved: No
cap_reference: Dinner cap
cap_amount: 60
fx_to_eur: 0.92
converted_amount_eur: 53.36
reimbursable_hint: 53.36
notes: Within cap.
```

### per-diem-caps-1639db42ae:00094

- order: `94`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 8}`

```text
claim_id: C-007
city: Vienna
country_code: AT
category: Client dinner
source_amount: 150
currency: EUR
alcohol_amount: 20
preapproved: Yes
cap_reference: Entertainment threshold
cap_amount: 120
fx_to_eur: 1
converted_amount_eur: 150
reimbursable_hint: 150
notes: Pre-approved client entertainment can include alcohol if attendee list exists.
```

### per-diem-caps-1639db42ae:00095

- order: `95`
- type: `table_row` section='ClaimExamples'
- metadata: `{"row_number": 9}`

```text
claim_id: C-008
city: Brno
country_code: CZ
category: Hotel
source_amount: 2800
currency: CZK
alcohol_amount: 0
preapproved: No
cap_reference: Hotel cap
cap_amount: 2500
fx_to_eur: 0.04
converted_amount_eur: 112
reimbursable_hint: 100
notes: Above cap; needs approval or documented shortage.
```

### per-diem-caps-1639db42ae:00096

- order: `96`
- type: `heading` section='PolicyTags'
- metadata: `{}`

```text
## PolicyTags
```

### per-diem-caps-1639db42ae:00097

- order: `97`
- type: `table_header` section='PolicyTags'
- metadata: `{"row_number": 1}`

```text
Columns: source_name, sheet_or_section, doc_type, country, city, expense_category, recommended_filter, notes
```

### per-diem-caps-1639db42ae:00098

- order: `98`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 2}`

```text
source_name: per_diem_caps.xlsx
sheet_or_section: PerDiemCaps
doc_type: xlsx
country: AT
city: Vienna
expense_category: meals
recommended_filter: country=AT, city=Vienna, expense_category=meals
notes: Use for meal and hotel cap questions.
```

### per-diem-caps-1639db42ae:00099

- order: `99`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 3}`

```text
source_name: per_diem_caps.xlsx
sheet_or_section: PerDiemCaps
doc_type: xlsx
country: DE
city: Berlin
expense_category: hotel
recommended_filter: country=DE, city=Berlin, expense_category=hotel
notes: Use for hotel cap questions.
```

### per-diem-caps-1639db42ae:00100

- order: `100`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 4}`

```text
source_name: per_diem_caps.xlsx
sheet_or_section: TaxiRules
doc_type: xlsx
country: CZ
city: Prague
expense_category: taxi
recommended_filter: country=CZ, city=Prague, expense_category=taxi
notes: Use for taxi after-hours checks.
```

### per-diem-caps-1639db42ae:00101

- order: `101`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 5}`

```text
source_name: per_diem_caps.xlsx
sheet_or_section: MileageRates
doc_type: xlsx
country: AT
city:
expense_category: mileage
recommended_filter: country=AT, expense_category=mileage
notes: Use for private car mileage rate.
```

### per-diem-caps-1639db42ae:00102

- order: `102`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 6}`

```text
source_name: expense_policy.html
sheet_or_section: Receipts
doc_type: html
country:
city:
expense_category: receipts
recommended_filter: expense_category=receipts
notes: Use for evidence and missing receipt questions.
```

### per-diem-caps-1639db42ae:00103

- order: `103`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 7}`

```text
source_name: expense_policy.html
sheet_or_section: Meals
doc_type: html
country:
city:
expense_category: meals
recommended_filter: expense_category=meals
notes: Use for alcohol, tips, and meal eligibility.
```

### per-diem-caps-1639db42ae:00104

- order: `104`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 8}`

```text
source_name: travel_policy.pdf
sheet_or_section: Flights
doc_type: pdf
country:
city:
expense_category: flights
recommended_filter: expense_category=flights
notes: Use for flight class, boarding pass, and air travel logistics.
```

### per-diem-caps-1639db42ae:00105

- order: `105`
- type: `table_row` section='PolicyTags'
- metadata: `{"row_number": 9}`

```text
source_name: travel_policy.pdf
sheet_or_section: Approval Matrix
doc_type: pdf
country:
city:
expense_category: approval
recommended_filter: expense_category=approval
notes: Use for pre-approval authority.
```
