import pdfplumber
import pandas as pd
from io import BytesIO
import re
import spacy
from utils.logger import logger 

# Load spaCy NLP model
nlp = spacy.load("en_core_web_md")

# Keep only canonical financial metrics
FINANCIAL_METRICS = [
    "Revenue",
    "Expenses",
    "Profit",
    "Assets",
    "Liabilities",
    "Equity",
    "Cash Flow",
]

def extract_from_pdf(uploaded_file):
    #Extract tables from PDF into a DataFrame
    try:
        data = uploaded_file.read()
        all_tables = []
        last_columns = None

        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    df = pd.DataFrame(table)

                    if last_columns is None or df.iloc[0].tolist() == last_columns:
                        df.columns = df.iloc[0]
                        df = df.drop(0).reset_index(drop=True)
                        last_columns = df.columns.tolist()

                    all_tables.append(df)

        if all_tables:
            result = pd.concat(all_tables, ignore_index=True)
            logger.info(f"PDF extraction successful, {len(result)} rows obtained.")
            return result
        else:
            logger.warning("No tables found in PDF.")
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return pd.DataFrame()

def extract_from_excel(uploaded_file):
    #Extract all sheets from Excel into a DataFrame
    try:
        data = uploaded_file.read()
        xls = pd.ExcelFile(BytesIO(data))
        all_tables = [xls.parse(sheet) for sheet in xls.sheet_names]

        if all_tables:
            result = pd.concat(all_tables, ignore_index=True)
            logger.info(f"Excel extraction successful, {len(result)} rows obtained.")
            return result
        else:
            logger.warning("No sheets found in Excel file.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error extracting Excel: {e}")
        return pd.DataFrame()


def parse_number_str(num_str):
    #Clean and convert number strings to float if possible
    cleaned = num_str.strip()
    cleaned = re.sub(r'[\$\u20B9£€\s]', '', cleaned)

    negative = False
    if cleaned.startswith("(") and cleaned.endswith(")"):
        negative = True
        cleaned = cleaned[1:-1].strip()

    cleaned = cleaned.replace(",", "")
    if negative:
        cleaned = "-" + cleaned

    try:
        return float(cleaned)
    except Exception:
        return cleaned


def match_metric(user_text):
    """Find best matching financial metric using spaCy similarity"""
    try:
        user_text = user_text.lower()
        doc = nlp(user_text)

        best_match, best_score = None, 0.0
        for metric in FINANCIAL_METRICS:
            metric_doc = nlp(metric.lower())
            score = doc.similarity(metric_doc)
            if score > best_score:
                best_score = score
                best_match = metric

        logger.info(f"Matched metric '{best_match}' with score {best_score:.2f}")
        return best_match, best_score
    except Exception as e:
        logger.error(f"Error matching metric: {e}")
        return None, 0.0


def summarize_financials(full_table):
    #Extract and summarize financial metrics from table
    metrics_data = {}
    try:
        if full_table.empty:
            return metrics_data

        for idx, row in full_table.iterrows():
            metric_cell = str(row[full_table.columns[0]]).strip()
            canonical, score = match_metric(metric_cell)

            if canonical and score > 0.7:
                if canonical not in metrics_data:
                    metrics_data[canonical] = {}

                for col in full_table.columns[1:]:
                    cell_value = str(row[col]).strip()
                    if cell_value:
                        val = parse_number_str(cell_value)
                        metrics_data[canonical][col] = val

        logger.info(f"Financial metrics summarized: {list(metrics_data.keys())}")
        return metrics_data
    except Exception as e:
        logger.error(f"Error summarizing financials: {e}")
        return metrics_data
