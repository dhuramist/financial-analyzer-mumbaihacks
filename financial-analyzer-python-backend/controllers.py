# Built-in Packages

import os
import io
import re
import csv
import json
import boto3
from concurrent.futures import ThreadPoolExecutor

# External Packages Packages

import PyPDF2
import pdfplumber
import pytesseract
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import fitz


def generate_recommendations(company, parsed_text):
    region_name = "us-east-1"
    bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name=region_name, aws_access_key_id=os.environ["SAGEMAKER_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["SAGEMAKER_SECRET_ACCESS_KEY"])
    bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region_name, aws_access_key_id=os.environ["SAGEMAKER_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["SAGEMAKER_SECRET_ACCESS_KEY"])

    model_id = "meta.llama3-8b-instruct-v1:0"
    kb_id = "NHR6DURFRT"
    
    # Fetch relevants docs
    print("Company: ", company)
    company_query = company.replace(" ", "").lower()
    print("Company query: ", company_query)

    kb_filter= {
        "equals": {
            "key": "company",
            "value": company_query
        }
    }

    query = f"""1) Years, Quarters, FY
    2) Revenue (income, revenue from operations, net income)
    3) Revenue growth
    4) Total expenses (expense, operating expense)
    5) PAT (Profit before tax, Profit after tax, Profit, Loss)
    6) Total Equity
    7) Total Liability (Current, Non-current liability)
    8) Debt-Equity (d/e ratio)
    9) Current ratio
    10) Working capital cycle (WCC)
    11) EBIDTA (Earnings Before Interest, Taxes, Depreciation, and Amortization)
    12) EBIDTA Margin
    13) ROCE (Return on Capital Employed)
    14) Gross margin (Operating margin)"""

    kb_response = bedrock_agent_runtime_client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={
            'text': query
        },
        retrievalConfiguration= {
            'vectorSearchConfiguration': {
                'filter': kb_filter,
                'numberOfResults': 15 # will fetch top 10 documents which matches closely with the query.
            }
        }
    )

    docs = "\n".join([res["content"]["text"] for res in kb_response["retrievalResults"]])

    # Generate Recommendations
    formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        You are a helpful AI assistant specializing in detailed investment or funding recommendations, risk factors and long-term/short-term investment factor based on financial statements (Balance Sheet, Profit and Loss, Cashflow) of a company. Based on the provided data, your task is to:
        1) Summarize the company's key financial metrics (Revenue growth, total expenses, total equity, total assets, total liabilities, debt-equity, current ratio, EBIDTA, EBIDTA margin, gross margin, ROCE).
        2) Offer investment or funding recommendations based on the following guidelines:
           - EBIDTA margin greater than 8% is considered good.
           - Gross margin greater than 40% is considered good.
           - Current ratio greater than 1 is considered good.
           - Debt/Equity ratio less than 1.5 is considered good.
           - Use the following general benchmarks for funding and investment recommendations:
             - Positive revenue growth is a good indicator of potential future profitability.
             - A PAT (Profit After Tax) increase year-on-year signals improving profitability.
             - A Debt/Equity ratio below 1.5 indicates manageable leverage.
             - An ROCE (Return on Capital Employed) greater than 15% is considered strong.
             - Working Capital Cycle efficiency indicates good operational cash flow.
        Also, apply rules and calculations as per domain, industry and size of the company if applicable. Give careful recommendations rather than direct.
        Example format:
        Based on the provided financial statements of {company}, here is the analysis of the company's key financial metrics:
        1)**Revenue Growth**: ...
        **Recommendation:**...
        2)**EBIDTA**: ....
        **Recommendation:**
        ...
        At last:
        **Final Recommendation:**...
        **Long-term factor:**
        **Short-term factor:**
        **Risk-factor:**

        <|eot_id|><|start_header_id|>user<|end_header_id|>{company}:
        {docs}<|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>"""
    
    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 4096,
        "temperature": 0.1,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = bedrock_runtime_client.invoke_model(modelId=model_id, body=request)

    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["generation"]
    print(response_text)

    return response_text


def is_image_pdf(pdf_path):

    # Checking if the PDF contains extractable text
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    return False
    except PyPDF2.errors.PdfReadError:
        # Handle the case when the file is not a PDF
        return False
    return True


def clean_text(text):


    # Replace escape characters with blank space
    text = re.sub(r'[\n\r\t]', ' ', text)
    
    # Replace special characters, and multiple dashes
    text = re.sub(r'[-–—~]+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


# def extract_text_from_pdf(pdf_path):
#     accumulated_text = ""
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 accumulated_text += clean_extracted_text(text) + " "  # Append page text
#     return accumulated_text.strip()  


# Get text and replace unwanted characters from text
def text_from_page(page):
    text = page.get_text()
    return clean_text(text) if text else ""

def extract_text_from_pdf(pdf_path):
    accumulated_text = ""
    with fitz.open(pdf_path) as pdf: # Reading using pymupdf
        with ThreadPoolExecutor() as executor: # Using threadpool behaviour to read the files in parallel manner
            results = executor.map(text_from_page, pdf)
        accumulated_text = " ".join(results)
    return accumulated_text.strip()



def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)  # Convert PDF pages to images
    ocr_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)  # Perform OCR on the image
        ocr_text += clean_text(text) + " "
    return ocr_text.strip()


# Main processing function
def process_pdf(company, file_path):

    extracted_text = ''  # List to hold the accumulated data

    if not file_path.lower().endswith('.pdf'):
        return { "err": True, "msg": "Incorrect File uploaded!" }
    
    print(f"Processing file: {file_path}")

    if is_image_pdf(file_path):
            # If the PDF is an image PDF, use OCR to extract text
        extracted_text = extract_text_with_ocr(file_path)
    else:
        # Otherwise, extract text normally
        extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text:
        return { "err": True, "msg": "No content available in file!" }

    
    print("Extracted Text => ", type(extracted_text))

    response = generate_recommendations(company, extracted_text)

    return { "err": False, "msg": response }

