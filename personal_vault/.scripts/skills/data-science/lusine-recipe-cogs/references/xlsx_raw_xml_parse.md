# XLSX Raw XML Parse (hermes venv workaround)

## Problem
On hermes venv (Python 3.14), both `openpyxl` and `pandas` fail on L'Usine recipe XLSX:
- `openpyxl.load_workbook()`: `TypeError: CellStyle.__init__() got an unexpected keyword argument 'applyFormat'` (newer Excel style node)
- `pandas.read_excel()`: `ModuleNotFoundError: numpy._core._multiarray_umath` (numpy 2.4 C-extension built for cp311, not cp314)

## Fix: parse the zip directly
XLSX is a ZIP of XML. Read `xl/sharedStrings.xml` (string table) + `xl/worksheets/sheet1.xml` (cells). No external lib needed.

```python
import zipfile, xml.etree.ElementTree as ET
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def read_xlsx(path):
    z = zipfile.ZipFile(path)
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.iter(NS+'si'):
            strings.append(''.join(t.text or '' for t in si.iter(NS+'t')))
    root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = []
    for row in root.iter(NS+'row'):
        cells = []
        for c in row.iter(NS+'c'):
            v = c.find(NS+'v')
            if v is not None:
                txt = v.text
                if c.get('t') == 's':
                    txt = strings[int(txt)]
                cells.append(txt)
            else:
                cells.append('')
        rows.append(cells)
    return rows

# Extract cost: "Cost, VND" row -> first non-empty cell to the right
# Price: "Price, VAT inclusive" or "Price excluding VAT" -> value right of label
# Item name: "Item name:" -> value right of label
# Cost VND is in THOUSANDS -> multiply by 1000
```

## Notes
- CSV files: just `cat` via terminal (no parsing lib needed).
- Always multiply the "Cost, VND" figure by 1000 (IKKO exports in thousands).
- This same raw-XML approach works for any .xlsx Warren sends (recipe cards, invoices).
