# Invoice Management System

startup dev server with:

```bash
python -m venv venv
source venv/bin/activate && pip install -r requirements.txt
./run.sh
```

## what was done
The tests are now running smoothly using SQLite for the test database. Here's what was tested:

- 8 Company & Customer tests - Model creation and string representations
- 12 Invoice tests - Creation, validation, calculations (subtotal, discount, shipping, total)
- 6 InvoiceItem tests - Creation, validation, total calculation, cascade delete
- 3 Form tests - Valid/invalid data handling
- 11 View tests - List, detail, create, update, delete, search, filtering, and PDF generation


## ToDo:
- the PDF should be exactly like the "invoice details" page
