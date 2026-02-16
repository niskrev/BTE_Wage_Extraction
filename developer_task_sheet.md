### Developer Task Sheet: BTE Wage Extraction Pipeline

**Project Objective:**
Develop a robust, scalable Python pipeline to extract `Occupation -> Wage` relationships from hundreds of "Boletim do Trabalho e Emprego" (BTE) PDF files. The solution must handle idiosyncratic layouts, separate category/wage tables, and varying terminology (e.g., "Nível", "Grupo", "Escalão").

**Core Strategy:** **Layout-Aware Deterministic Extraction with LLM Fallback.**

* **Primary Path:** Use layout-aware parsers (`pdfplumber`, `Camelot`) to extract table structures deterministically.
* **Secondary Path:** Use OCR (`PaddleOCR`) for scanned/image-based tables.
* **Intelligence Layer:** Use an LLM only for semantic normalization (e.g., mapping "Chefia" to "Manager") and adjudicating ambiguous joins.

---

### **1. Technology Stack**

* **Language:** Python 3.10+
* **PDF Parsing (Digital):** `pdfplumber` (best for visual text extraction), `PyMuPDF` (fast metadata/page rendering).
* **Table Extraction:** `Camelot` (lattice mode for gridlines), `Tabula-py`.
* **OCR (Scanned/Image):** `PaddleOCR` or `Surya` (specialized for document layout).
* **Data Validation:** `Pydantic` (strict schema enforcement).
* **Orchestration/LLM:** `LangChain` (optional) or direct OpenAI/Gemini API calls.
* **Data Manipulation:** `Pandas`.

---

### **2. Target Data Schema (JSON Output)**

Every file must produce a list of objects adhering to this strict schema:

```json
[
  {
    "pdf_id": "00430074",
    "occupation_normalized": "Técnico de 2.ª",
    "occupation_raw": "Técnico de 2.ª / Grau III",
    "wage_group_raw": "Nível 7",
    "wage_amount": 1250.00,
    "currency": "EUR",
    "effective_year": 2024,
    "confidence_score": 0.95,
    "extraction_method": "deterministic_lattice"
  }
]

```

---

### **3. Implementation Phases**

#### **Phase 1: Ingestion & Segmentation (The "Filter")**

* **Goal:** Identify which pages contain the relevant data to avoid processing 50+ pages of legal text.
* **Logic:**
1. Load PDF with `PyMuPDF`.
2. Classify file type: **Born-Digital** (selectable text) vs. **Scanned** (images).
3. 
**Keyword Search:** Scan for "Tabela Salarial", "Remunerações", "Categorias Profissionais", "Anexo".


4. **Expansion Heuristic:** If a keyword is found on Page 20, check Page 19 and 21 for table continuity.


* **Deliverable:** A script returning a list of `page_indices` for each PDF.

#### **Phase 2: Table Extraction (The "Miner")**

* **Task A: Digital Extraction (Happy Path)**
* Use `pdfplumber` to extract text while preserving physical layout ( coordinates).
* Detect table boundaries using visible lines (`Camelot Lattice`) or whitespace columns (`Camelot Stream`).


* **Task B: Image Extraction (Fallback Path)**
* If digital extraction fails or returns empty tables (common in hybrid PDFs), render page as image.
* Run `PaddleOCR` to detect text blocks and table cells.


* **Deliverable:** A collection of raw Pandas DataFrames representing every table found on the target pages.

#### **Phase 3: Semantic Linking (The "Join")**

* **Challenge:** As seen in the source text, wages are often decoupled:
* 
*Table A (Annex II):* "Técnico" -> "Grupo GS5".


* 
*Table B (Annex III):* "Grupo GS5" -> "1.366,10 €".




* **Logic:**
1. **Identify the "Key":** Find the common column between tables (e.g., "Nível", "Grupo", "Índice").
2. **Merge:** Perform a database-style join on the Key.
3. **LLM Assist:** If keys don't match exactly (e.g., "Nível V" vs "Nível 5"), send the column headers and unique values to the LLM to generate a normalization map.



#### **Phase 4: Validation & Adjudication (The "Quality Gate")**

* **Validation Rules (Pydantic):**
* `wage_amount` must be a float > 500 (sanity check for monthly wage vs. hourly).
* `occupation` must not be null.


* **Confidence Scoring:**
* *High (1.0):* Perfect string match on join keys; wage column detected with currency symbol.
* *Low (<0.7):* Fuzzy match required; OCR confidence low.


* **The "Adjudicator":**
* If validation fails, package the raw text of the specific page and the error message (e.g., "Ambiguous join key") and send to LLM: *"Fix this JSON based on the text provided."*



---

### **4. Workflow Logic Diagram**

---

### **5. Immediate Next Steps**

1. **Audit:** Run a script to classify the hundreds of files into "Digital" vs. "Scanned".
2. **Prototype Parser:** Build the `pdfplumber` script targeting specifically the "Anexo" pages of the provided sample files (`00430074.pdf`, `00750165.pdf`, etc.) to test the segmentation logic.
3. **Schema Definition:** Write the `Pydantic` models to freeze the output format.
