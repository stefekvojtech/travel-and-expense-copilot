# Loaded Document Preview: Per Diem Caps

- doc_id: `per-diem-caps-1639db42ae`
- source_path: `data/raw/per_diem_caps.xlsx`
- doc_type: `xlsx`
- loader: `openpyxl_row_level`
- loaded_documents: `1`

## Document 1

- metadata: `{"extraction_method": "openpyxl_row_level", "extraction_warning": null, "source_block_count": 105}`

```text
## README
| Atlas Mobility Group - Per Diem Caps Workbook 2026 | column_2 |
| Purpose | Synthetic data source for local RAG and agentic reimbursement demo. |
| Version | PDC-2026.2 |
| Effective date | 2026-01-01 |
| Owner | Finance Operations |
| Source priority | Use this workbook for numeric caps, thresholds, and deterministic lookups. Use PDF/HTML for narrative policy rules. |
| RAG note | Every sheet is intentionally structured differently so loaders must preserve sheet name, row context, and metadata. |
| Recommended metadata | doc_type=xlsx, source_name=per_diem_caps.xlsx, sheet=<sheet>, effective_date=2026-01-01 |
| Sheets |  |
| PerDiemCaps | Meal, hotel, taxi, and laundry caps by country/city. |
| TaxiRules | After-hours thresholds and city-specific transport notes. |
| MileageRates | Private car mileage rates and approval thresholds. |
| ExchangeRates | Monthly finance exchange rates for claim conversion. |
| ApprovalMatrix | Numeric thresholds for approval routing. |
| ClaimExamples | Worked examples with formulas for reimbursement logic. |
| PolicyTags | Metadata tags useful for filtering and retrieval. |

## PerDiemCaps
| country_code | country | city | currency | meal_cap_breakfast | meal_cap_lunch | meal_cap_dinner | meal_cap_daily | hotel_cap_per_night | taxi_allowed_after | laundry_after_nights | notes | effective_date |
| AT | Austria | Vienna | EUR | 12 | 24 | 35 | 71 | 160 | 22:00 | 5 | Dinner cap excludes alcohol unless client entertainment was pre-approved. | 2026-01-01 |
| AT | Austria | Graz | EUR | 10 | 22 | 32 | 64 | 135 | 22:00 | 5 | Lower hotel cap than Vienna; airport taxi needs route evidence. | 2026-01-01 |
| AT | Austria | Linz | EUR | 10 | 21 | 31 | 62 | 125 | 22:00 | 5 | Standard Austrian regional cap. | 2026-01-01 |
| CZ | Czechia | Prague | CZK | 250 | 500 | 700 | 1450 | 3000 | 21:00 | 5 | Caps stored in local currency; convert with Finance monthly rate. | 2026-01-01 |
| CZ | Czechia | Brno | CZK | 220 | 450 | 620 | 1290 | 2500 | 21:00 | 5 | Taxi before 21:00 requires exception reason. | 2026-01-01 |
| CZ | Czechia | Ostrava | CZK | 200 | 420 | 580 | 1200 | 2300 | 21:00 | 5 | Regional rate; hotel above cap needs manager approval. | 2026-01-01 |
| DE | Germany | Berlin | EUR | 14 | 28 | 40 | 82 | 180 | 22:00 | 5 | Conference hotel above cap can be approved with evidence. | 2026-01-01 |
| DE | Germany | Munich | EUR | 15 | 30 | 45 | 90 | 210 | 22:00 | 5 | Higher lodging cap due to market rates. | 2026-01-01 |
| DE | Germany | Frankfurt | EUR | 14 | 29 | 42 | 85 | 190 | 22:00 | 5 | Airport taxi must include route or booking proof. | 2026-01-01 |
| CH | Switzerland | Zurich | CHF | 18 | 36 | 55 | 109 | 240 | 22:30 | 4 | Caps are CHF; report in source currency and convert to EUR. | 2026-01-01 |
| CH | Switzerland | Basel | CHF | 16 | 33 | 50 | 99 | 210 | 22:30 | 4 | Client entertainment requires attendee list. | 2026-01-01 |
| NL | Netherlands | Amsterdam | EUR | 13 | 27 | 39 | 79 | 175 | 22:00 | 5 | Taxi from Schiphol usually requires business reason. | 2026-01-01 |
| FR | France | Paris | EUR | 15 | 32 | 46 | 93 | 220 | 22:00 | 5 | Hotel above cap often reviewed manually during trade fairs. | 2026-01-01 |
| GB | United Kingdom | London | GBP | 13 | 30 | 48 | 91 | 210 | 22:30 | 4 | Caps are GBP; use monthly Finance exchange rate. | 2026-01-01 |
| US | United States | New York | USD | 18 | 36 | 60 | 114 | 280 | 22:00 | 4 | Tips are reimbursable within reason but must be itemized. | 2026-01-01 |
| US | United States | Houston | USD | 15 | 30 | 48 | 93 | 210 | 22:00 | 4 | Rental car is common for plant visits but still needs business purpose. | 2026-01-01 |
| PL | Poland | Warsaw | PLN | 50 | 95 | 140 | 285 | 520 | 21:30 | 5 | Local taxi apps accepted with route evidence. | 2026-01-01 |
| HU | Hungary | Budapest | HUF | 4500 | 9000 | 13000 | 26500 | 48000 | 21:30 | 5 | Cash receipts must show vendor and date. | 2026-01-01 |
| IT | Italy | Milan | EUR | 14 | 30 | 44 | 88 | 205 | 22:00 | 5 | City tax reimbursable when shown on hotel folio. | 2026-01-01 |
| ES | Spain | Madrid | EUR | 12 | 26 | 38 | 76 | 165 | 22:00 | 5 | Late dinner is normal locally but alcohol still excluded. | 2026-01-01 |

## TaxiRules
| country_code | city | default_after_hours_threshold | airport_to_city_allowed | home_to_office_allowed | requires_route_evidence | exception_keywords | audit_note |
| AT | Vienna | 22:00 | Yes if luggage, late arrival, or public transport disruption | No, unless approved overtime after 22:00 or safety issue | Yes | luggage; late arrival; safety; strike; disruption | Before 22:00 route evidence and exception reason are important. |
| CZ | Prague | 21:00 | Yes if after threshold or public transport not practical | No, unless overtime after 22:00 or safety issue | Yes | luggage; unsafe; disruption; late return | 20:30 is not after-hours in Prague under default rule. |
| CZ | Brno | 21:00 | Yes if after threshold or public transport not practical | No | Yes | plant visit; luggage; unsafe | Brno taxi claims often fail when business purpose is missing. |
| DE | Berlin | 22:00 | Yes for late arrivals and heavy luggage | No | Yes | trade fair; late arrival; strike | Public transit is expected unless exception applies. |
| DE | Munich | 22:00 | Yes if after threshold or luggage | No | Yes | airport; luggage; client equipment | Airport rides above EUR 90 require explanation. |
| CH | Zurich | 22:30 | Yes if after threshold or client equipment | No | Yes | late arrival; equipment; safety | High taxi costs are reviewed against public transit options. |
| FR | Paris | 22:00 | Yes if after threshold, luggage, or strike | No | Yes | strike; unsafe; luggage | Taxi receipts must include vendor and date. |
| GB | London | 22:30 | Yes if after threshold, safety issue, or rail strike | No | Yes | rail strike; safety; equipment | Black cab receipt without route needs manual route entry. |
| US | New York | 22:00 | Yes, route evidence required | No | Yes | late arrival; client materials | Tips above 20% require explanation in US cities. |

## MileageRates
| country_code | country | currency | private_car_rate_per_km | electric_car_rate_per_km | preapproval_distance_one_way_km | fuel_claim_separate_allowed | notes |
| AT | Austria | EUR | 0.42 | 0.45 | 150 | No | Private mileage includes fuel, wear, and standard insurance. |
| CZ | Czechia | CZK | 6.2 | 6.8 | 150 | No | Use local payroll/tax rate if different from Finance rate. |
| DE | Germany | EUR | 0.38 | 0.42 | 150 | No | Long-distance private car trips need manager approval. |
| CH | Switzerland | CHF | 0.7 | 0.72 | 120 | No | Parking can be claimed separately with business purpose. |
| NL | Netherlands | EUR | 0.34 | 0.38 | 120 | No | Bike mileage is not covered in this workbook. |
| FR | France | EUR | 0.4 | 0.44 | 150 | No | Tolls reimbursable with receipt if route was business-related. |
| GB | United Kingdom | GBP | 0.45 | 0.45 | 150 | No | Use local HMRC-compliant value if Finance updates rate. |
| US | United States | USD | 0.67 | 0.67 | 150 | No | Use IRS-compliant rate if Finance updates rate. |

## ExchangeRates
| month | currency | eur_rate | source | notes |
| 2026-01 | EUR | 1 | Finance monthly table | Base currency |
| 2026-01 | CZK | 0.04 | Finance monthly table | 25 CZK = 1 EUR equivalent |
| 2026-01 | CHF | 1.06 | Finance monthly table | Use for Swiss caps and claims |
| 2026-01 | GBP | 1.17 | Finance monthly table | Use for UK claims |
| 2026-01 | USD | 0.92 | Finance monthly table | Use for US claims |
| 2026-01 | PLN | 0.23 | Finance monthly table | Use for Poland claims |
| 2026-01 | HUF | 0.0026 | Finance monthly table | Use for Hungary claims |
| 2026-02 | EUR | 1 | Finance monthly table | Base currency |
| 2026-02 | CZK | 0.0396 | Finance monthly table | Monthly conversion rate |
| 2026-02 | CHF | 1.05 | Finance monthly table | Monthly conversion rate |
| 2026-02 | GBP | 1.16 | Finance monthly table | Monthly conversion rate |
| 2026-02 | USD | 0.93 | Finance monthly table | Monthly conversion rate |
| 2026-02 | PLN | 0.231 | Finance monthly table | Monthly conversion rate |
| 2026-02 | HUF | 0.00255 | Finance monthly table | Monthly conversion rate |

## ApprovalMatrix
| scenario | threshold | currency | approval_required | approver | source_priority | notes |
| Client entertainment total | 120 | EUR | Yes if above threshold | Cost center owner or Sales VP | Travel Policy PDF + Expense Policy HTML | Requires attendee list and business purpose. |
| Missing receipt declaration | 25 | EUR | Yes if above threshold | Line manager | Expense Policy HTML | Repeated missing evidence can trigger manual review. |
| Hotel above city cap | 0 | N/A | Yes if above applicable city cap | Cost center owner | PerDiemCaps + Travel Policy PDF | Document lack of reasonable alternatives. |
| Private car one-way distance | 150 | km | Yes if above threshold | Line manager | Expense Policy HTML + MileageRates | Applies unless plant visit exception is documented. |
| Business class flight duration | 6 | hours | Yes if intercontinental and above duration | Cost center owner | Travel Policy PDF | Also requires business reason. |
| Late expense submission | 90 | days | Yes for exception | Finance Operations | Expense Policy HTML + Travel Policy PDF | Claims older than 90 days normally rejected. |
| Team celebration per person | 50 | EUR | Yes if above threshold | Line manager or morale budget owner | Expense Policy HTML | Not normal travel expense category. |

## ClaimExamples
| claim_id | city | country_code | category | source_amount | currency | alcohol_amount | preapproved | cap_reference | cap_amount | fx_to_eur | converted_amount_eur | reimbursable_hint | notes |
| C-001 | Vienna | AT | Dinner | 40 | EUR | 8 | No | Dinner cap | 35 | 1 | 40 | 32 | Wine excluded; food portion 32 EUR below cap. |
| C-002 | Berlin | DE | Hotel | 175 | EUR | 0 | N/A | Hotel cap | 180 | 1 | 175 | 175 | Within cap. |
| C-003 | Prague | CZ | Taxi | 650 | CZK | 0 | No | Taxi after-hours | 0 | 0.04 | 26 | 26 | Eligibility depends on time threshold and exception reason. |
| C-004 | Zurich | CH | Hotel | 260 | CHF | 0 | No | Hotel cap | 240 | 1.06 | 275.6 | 254.4 | Above cap without approval; reimbursable hint capped. |
| C-005 | London | GB | Dinner | 62 | GBP | 0 | No | Dinner cap | 48 | 1.17 | 72.53999999999999 | 56.16 | Above meal cap; excess requires approval. |
| C-006 | New York | US | Dinner | 58 | USD | 0 | No | Dinner cap | 60 | 0.92 | 53.36 | 53.36 | Within cap. |
| C-007 | Vienna | AT | Client dinner | 150 | EUR | 20 | Yes | Entertainment threshold | 120 | 1 | 150 | 150 | Pre-approved client entertainment can include alcohol if attendee list exists. |
| C-008 | Brno | CZ | Hotel | 2800 | CZK | 0 | No | Hotel cap | 2500 | 0.04 | 112 | 100 | Above cap; needs approval or documented shortage. |

## PolicyTags
| source_name | sheet_or_section | doc_type | country | city | expense_category | recommended_filter | notes |
| per_diem_caps.xlsx | PerDiemCaps | xlsx | AT | Vienna | meals | country=AT, city=Vienna, expense_category=meals | Use for meal and hotel cap questions. |
| per_diem_caps.xlsx | PerDiemCaps | xlsx | DE | Berlin | hotel | country=DE, city=Berlin, expense_category=hotel | Use for hotel cap questions. |
| per_diem_caps.xlsx | TaxiRules | xlsx | CZ | Prague | taxi | country=CZ, city=Prague, expense_category=taxi | Use for taxi after-hours checks. |
| per_diem_caps.xlsx | MileageRates | xlsx | AT |  | mileage | country=AT, expense_category=mileage | Use for private car mileage rate. |
| expense_policy.html | Receipts | html |  |  | receipts | expense_category=receipts | Use for evidence and missing receipt questions. |
| expense_policy.html | Meals | html |  |  | meals | expense_category=meals | Use for alcohol, tips, and meal eligibility. |
| travel_policy.pdf | Flights | pdf |  |  | flights | expense_category=flights | Use for flight class, boarding pass, and air travel logistics. |
| travel_policy.pdf | Approval Matrix | pdf |  |  | approval | expense_category=approval | Use for pre-approval authority. |
```
