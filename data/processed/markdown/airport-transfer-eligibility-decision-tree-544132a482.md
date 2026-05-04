# Airport Transfer Eligibility Decision Tree

- doc_id: `airport-transfer-eligibility-decision-tree-544132a482`
- source_path: `data/raw/airport_transfer_eligibility_decision_tree.png`
- doc_type: `image`
- content_hash: `e94cb293250911c0805b42b79cc59a2b66889cb7c29f83031e3ecb6dbe9ec695`
- extraction_method: `image_vision_openai`
- blocks_path: `data/processed/blocks/airport-transfer-eligibility-decision-tree-544132a482.jsonl`

## Content

```markdown
# Airport Transfer Eligibility Decision Tree

## Need airport transfer reimbursement?

### 1. Is public transport reasonably available and safe?

- YES → 2. Are you traveling with heavy luggage, medical needs, or client equipment?
- NO → 3. Is the transfer after the policy cutoff time?

### 2. Are you traveling with heavy luggage, medical needs, or client equipment?

- YES  
  ✅ Taxi or ride-hailing may be reimbursable.  
  Add justification in expense claim.
- NO  
  ❌ Use public transport.  
  Taxi is not normally reimbursable.

### 3. Is the transfer after the policy cutoff time?

- YES → 4. What is the city cutoff time?

- NO → 5. Is there a documented safety concern, service disruption, or no practical connection?

### 4. What is the city cutoff time?

- Vienna 22:00  
- Berlin 22:00  
- Prague 21:00  

✅ Taxi or ride-hailing is reimbursable if travel occurs after the city cutoff time.

### 5. Is there a documented safety concern, service disruption, or no practical connection?

- YES  
  ✔️ Taxi may be reimbursable with explanation and supporting details.
- NO  
  ❌ Taxi is not reimbursable.  
  Use public transport.

---

## Required claim details

- origin and destination  
- date and local time  
- business purpose  
- reason public transport was unsuitable  
- receipt required above policy minimum  

---

ℹ️ Reference guide only. Final reimbursement depends on company travel policy and manager/finance review.
```
