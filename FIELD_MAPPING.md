# Field Mapping Comparison

## Booking_DataTable.xlsx (Excel) Fields
- **Amount**: `Amount` (column 14)
- **Invoice/Receipt Number**: `Belegfeld 1`, `Belegfeld 2` (columns 17, 18)
- **Cost Center**: `KOST1 - Kostenstelle`, `KOST2 - Kostenstelle`, `CostCenter_id` (columns 15, 16, 26)

## Flowwer Data Explorer Fields
- **Amount**: `Gross`, `Net` (from split or document)
- **Invoice/Receipt Number**: `Receipt Number` (from document)
- **Cost Center**: `Cost Center` (from split)
- **Cost Unit**: `Cost Unit (KOST2)` (from split)

## Mapping for Comparison

| Excel Field | Flowwer Field | Match Type |
|-------------|---------------|------------|
| Amount | Gross | Direct comparison |
| Belegfeld 1 or Belegfeld 2 | Receipt Number | May need normalization |
| KOST1 - Kostenstelle | Cost Center | Direct comparison |
| KOST2 - Kostenstelle | Cost Unit (KOST2) | Direct comparison |
| CostCenter_id | Cost Center | May need ID lookup |

## Additional Fields in Excel
- Company_id, Company_Name
- Belegdatum (Document Date)
- Konto, Gegenkonto (Account numbers)
- Buchungstext (Booking text)
- Umsatz Soll, Umsatz Haben (Debit/Credit)

## Additional Fields in Flowwer
- Document ID
- Invoice Date
- Supplier Name
- Payment State
- Flow (Approval workflow)
- Document Status
