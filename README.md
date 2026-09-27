# Multilingual Question-Answer (QnA) Generation System

A Python application that accepts documents in PDF, DOCX, or TXT format and generates aligned Question-Answer (QnA) pairs in English, Hindi, and Marathi using the Google Gemini API.

---

## 1. Project Objective

1. Accept documents in PDF, DOCX, or TXT format (English, Hindi, Marathi, or mixed languages).
2. Extract and clean the document text.
3. Generate canonical Question-Answer pairs in English based only on document content.
4. Translate the same QnA pairs into Hindi and Marathi, maintaining identical order and meaning.
5. Save the output to `QnA.xlsx` with three sheets (`English`, `Hindi`, `Marathi`) and two columns (`Questions`, `Answers`).
6. Provide a simple Streamlit interface for upload, question count selection, preview, and download.

---

## 2. Technologies Used

- **Python**: Core programming language
- **Streamlit**: Web interface
- **google-genai**: Google Gemini API client
- **pypdf**: PDF text extraction
- **python-docx**: Word document text extraction
- **openpyxl**: Excel creation and formatting
- **pandas**: Tabular preview rendering
- **python-dotenv**: Environment variable configuration

---

## 3. Project Structure

```text
project/
│
├── app.py                  # Streamlit UI and pipeline controller
├── document_processor.py   # PDF, DOCX, TXT text extraction and cleaning
├── qna_generator.py        # Gemini client, QnA generation, and deduplication
├── translator.py           # Hindi and Marathi translation functions
├── excel_generator.py      # openpyxl workbook creation and validation
├── requirements.txt        # Project dependencies
├── .env                    # Gemini API key (kept secret)
├── .env.example            # Example API key template
├── .gitignore              # Ignores sensitive and temporary files
├── sample_documents/       # Sample PDF, DOCX, and TXT files
└── QnA.xlsx                # Output Excel file
```

---

## 4. How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env` with your API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key
   ```
3. Run the Streamlit application:
   ```bash
   python -m streamlit run app.py
   ```
4. Open `http://localhost:8501` in your browser.
5. Upload a document, select the number of questions, and click **Generate QnA**.
6. Preview the questions and click **Download QnA.xlsx**.

---

## 5. Output Format (QnA.xlsx)

- **Sheet 1**: `English`
- **Sheet 2**: `Hindi`
- **Sheet 3**: `Marathi`
- **Columns in every sheet**: `Questions` | `Answers`
- Same row corresponds to the same question across all three sheets.
