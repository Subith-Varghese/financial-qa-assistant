# Financial Document Q&A Assistant

An interactive Streamlit app that lets you upload PDF or Excel financial statements, automatically extracts key financial metrics (like Revenue, Profit, Expenses, etc.), and allows you to chat with the document using a local LLM (Ollama Gemma:2b).

---
## 📂 Project Structure
```
financial-qa-assistant/
│── app.py                         # Main Streamlit app
│── requirements.txt               # Python dependencies
│
└── utils/
    └── data_extractor.py          # Functions for table extraction & financial metric parsing
    └── logger.py                  # Logging setup for tracking events & debugging

```
--- 
### 1. App Home Page – Upload Section
Users can upload financial statements in **PDF/XLSX** format.  
![Upload Section](https://github.com/Subith-Varghese/financial-qa-assistant/blob/dccb96bd2be0eebbaf592ee8ba39679a44a7f191/screenshot_home_upload.png)

### 2. Extracted Financial Insights  
Once uploaded, The app automatically extracts key metrics such as Revenue, Profit, Expenses, Assets, Equity, and Cash Flow and displays them in a clean table.
![Extracted Insights](https://github.com/Subith-Varghese/financial-qa-assistant/blob/dccb96bd2be0eebbaf592ee8ba39679a44a7f191/screenshot_insights.png)

### 3. Ask Questions About the Document  
Users can ask questions like *“What was the revenue in 2022 and 2023?”*.  
![Ask Questions](https://github.com/Subith-Varghese/financial-qa-assistant/blob/dccb96bd2be0eebbaf592ee8ba39679a44a7f191/screenshot_question.png)

### 4. Interactive Q&A with Memory
The assistant provides instant answers based on extracted data, while remembering the conversation history for a smooth, chat-like experience.
![Interactive Q&A](https://github.com/Subith-Varghese/financial-qa-assistant/blob/dccb96bd2be0eebbaf592ee8ba39679a44a7f191/screenshot_answers.png)

---
## Workflow

### 1. Upload Financial Documents
- Supports .pdf, .xls, .xlsx.
- Extracts tables using pdfplumber (for PDFs) or pandas (for Excel).
- Concatenates tables from all pages/sheets into a single DataFrame.
```
df = pd.DataFrame(table)
if last_columns is None or df.iloc[0].tolist() == last_columns:
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)
    last_columns = df.columns.tolist()
all_tables.append(df)
```
✅ This ensures we don’t always reset the first row as column names if multiple tables share the same structure.

### 2. Summarize Financial Metrics
- Standard metrics like Revenue, Profit, Expenses, Assets, Equity, Cash Flow are detected.
- Uses spaCy similarity to match user text with canonical metrics.

### 3. Clean & Convert Numbers
- Handles currency symbols ($, €, £, ₹)
- Removes commas in amounts (1,234,567 → 1234567)
- Detects negative values in parentheses ((1,000) → -1000)

Example:
```
($1,234,567) → -1234567.0
$1,234,567   → 1234567.0

```
### 4. Ask Questions (Q&A)

- Chat interface powered by Streamlit st.chat_input.
- Sends extracted metrics + user question as context to Ollama (Gemma:2b).
- Maintains chat history like a real conversation.
---
## 🔑 Key Concepts Implemented

- Table extraction & concatenation across pages/sheets.
-  Dynamic column handling → prevents duplicate headers in multi-page tables.
- Robust number parsing → supports currency symbols, commas, and negative parentheses.
- 🤖 Semantic metric matching with spaCy similarity.
- 💬 Interactive chat interface with memory (st.session_state["history"]).
--- 

## 🛠️ Setup & Installation

### 1. Install Python dependencies
```
pip install -r requirements.txt
```
### 2. Install spaCy model
```
python -m spacy download en_core_web_md
```
### 3. Install & configure Ollama
- Download Ollama from: https://ollama.ai
- Pull the Gemma 2B model:
```
ollama pull gemma:2b
```
--- 
## ▶️ Run the App
```
streamlit run app.py
```
Then open 👉 http://localhost:8501
---

## 🎯 Example Usage
1. Upload financial_statement.xlsx
2. App extracts and shows metrics:
```
Revenue    1000000   1200000
Profit      250000    300000
Expenses    500000    550000

```
3. Ask questions in chat:

```
You: What was the revenue in 2023?
Assistant: The revenue in 2023 was 1000000.0

```
