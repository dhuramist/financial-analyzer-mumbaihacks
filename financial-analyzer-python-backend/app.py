from datetime import datetime
from distutils.log import error
import os
import logging
import traceback
from flask import Flask, json, request, jsonify, send_file
from flask.wrappers import Response
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import io
from dotenv import load_dotenv
import boto3
import time
from werkzeug.utils import secure_filename
from controllers import ( generate_recommendations, process_pdf )

load_dotenv()

UPLOAD_FOLDER = 'Balance Sheets'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

root = os.path.dirname(os.path.abspath(__file__))
logdir = os.path.join(root, 'logs')
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.basicConfig(
    filename='logs/record.log',
    level=logging.DEBUG,
    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return "Welcome to Flask app - Document Analyzer!"

@app.route('/hello', methods=['GET'])
def say_hello():
    print(request)
    return jsonify({'message': 'Hello World'})

@app.route('/generate', methods=['POST'])
def generate_recommend():
    print(request)
    try: 
        company = request.json.get('company', '')
        parsed_text = parsed_text = """"Apple Inc.
        CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)
        (In millions, except number of shares, which are reflected in thousands, and per-share amounts)
        Three Months Ended Nine Months Ended
        June 29,
        2024 July 1,
        2023 June 29,
        2024 July 1,
        2023
        Net sales:
        Products $ 61,564 $ 60,584 $ 224,908 $ 230,901
        Services 24,213 21,213 71,197 62,886
        Total net sales (1) 85,777 81,797 296,105 293,787
        Cost of sales:
        Products 39,803 39,136 140,667 146,696
        Services 6,296 6,248 18,634 18,370
        Total cost of sales 46,099
        45,384 159,301 165,066
        Gross margin 39,678 36,413 136,804 128,721
        Operating expenses:
        Research and development 8,006 7,442 23,605 22,608
        Selling, general and administrative 6,320 5,973 19,574 18,781
        Total operating expenses 14,326 13,415 43,179 41,389
        Operating income 25,352 22,998 93,625 87,332
        Other income/(expense), net 142 (265) 250 (594)
        Income before provision for income taxes 25,494 22,733 93,875 86,738
        Provision for income taxes 4,046 2,852 14,875 12,699
        Net income $ 21,448 $ 19,881 $ 79,000 $ 74,039
        Earnings per share:
        Basic $ 1.40 $ 1.27 $ 5.13 $ 4.69
        Diluted $ 1.40 $ 1.26 $ 5.11 $ 4.67
        Shares used in computing earnings per share:
        Basic 15,287,521 15,697,614 15,401,047 15,792,497
        Diluted 15,348,175 15,775,021 15,463,175 15,859,263
        (1) Net sales by reportable segment:
        Americas $ 37,678 $ 35,383 $ 125,381 $ 122,445
        Europe 21,884 20,205 76,404 71,831
        Greater China 14,728 15,758 51,919 57,475
        Japan 5,097 4,821 19,126 18,752
        Rest of Asia Pacific 6,390 5,630 23,275 23,284
        Total net sales $ 85,777 $ 81,797 $ 296,105 $ 293,787
        (1) Net sales by category:
        iPhone $ 39,296 $ 39,669
        $ 154,961 $ 156,778
        Mac 7,009 6,840 22,240 21,743
        iPad 7,162 5,791 19,744 21,857
        Wearables, Home and Accessories 8,097 8,284 27,963 30,523
        Services 24,213 21,213 71,197 62,886
        Total net sales $ 85,777 $ 81,797 $ 296,105 $ 293,787
        Apple Inc.
        CONDENSED CONSOLIDATED BALANCE SHEETS (Unaudited)
        (In millions, except number of shares, which are reflected in thousands, and par value)
        June 29,
        2024 September 30,
        2023
        ASSETS:
        Current assets:
        Cash and cash equivalents $ 25,565 $ 29,965
        Marketable securities 36,236 31,590
        Accounts receivable, net 22,795 29,508
        Vendor non-trade receivables 20,377 31,477
        Inventories 6,165 6,331
        Other current assets 14,297 14,695
        Total current assets 125,435 143,566
        Non-current assets:
        Marketable securities 91,240 100,544
        Property, plant and equipment, net 44,502 43,715
        Other non-current assets 70,435 64,758
        Total non-current assets 206,177 209,017
        Total assets $ 331,612 $ 352,583
        LIABILITIES AND SHAREHOLDERS’ EQUITY:
        Current liabilities:
        Accounts payable $ 47,574 $ 62,611
        Other current liabilities 60,889 58,829
        Deferred revenue 8,053 8,061
        Commercial paper 2,994 5,985
        Term debt 12,114 9,822
        Total current liabilities 131,624 145,308
        Non-current liabilities:
        Term debt 86,196 95,281
        Other non-current liabilities 47,084 49,848
        Total non-current liabilities 133,280 145,129
        Total liabilities 264,904
        290,437
        Commitments and contingencies
        Shareholders’ equity:
        Common stock and additional paid-in capital, $0.00001 par value: 50,400,000 shares
        authorized; 15,222,259 and 15,550,061 shares issued and outstanding, respectively 79,850 73,812
        Accumulated deficit (4,726) (214)
        Accumulated other comprehensive loss (8,416) (11,452)
        Total shareholders’ equity 66,708 62,146
        Total liabilities and shareholders’ equity $ 331,612 $ 352,583
        Apple Inc.
        CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS (Unaudited)
        (In millions)
        Nine Months Ended
        June 29,
        2024 July 1,
        2023
        Cash, cash equivalents and restricted cash, beginning balances $ 30,737 $ 24,977
        Operating activities:
        Net income 79,000 74,039
        Adjustments to reconcile net income to cash generated by operating activities:
        Depreciation and amortization 8,534 8,866
        Share-based compensation expense 8,830 8,208
        Other (1,964) (1,651)
        Changes in operating assets and liabilities:
        Accounts receivable, net 6,697 7,609
        Vendor non-trade receivables 11,100 13,111
        Inventories 41 (2,570)
        Other current and non-current assets (5,626) (4,863)
        Accounts payable (15,171) (16,790)
        Other current and non-current liabilities 2 2,986
        Cash generated by operating activities 91,443 88,945
        Investing activities:
        Purchases of marketable securities (38,074) (20,956)
        Proceeds from maturities of marketable securities 39,838 27,857
        Proceeds from sales of marketable securities 7,382 3,959
        Payments for acquisition of property, plant and equipment (6,539) (8,796)
        Other (1,117) (753)
        Cash generated by investing activities 1,490 1,311
        Financing activities:
        Payments for taxes related to net share settlement of equity awards (5,163) (5,119)
        Payments for dividends and dividend equivalents (11,430) (11,267)
        Repurchases of common stock (69,866) (56,547)
        Proceeds from issuance of term debt, net — 5,228
        Repayments of term debt (7,400) (11,151)
        Repayments of commercial paper, net (2,985) (5,971)
        Other (191) (508)
        Cash used in financing activities (97,035) (85,335)
        Increase/(Decrease) in cash, cash equivalents and restricted cash (4,102) 4,921
        Cash, cash equivalents and restricted cash, ending balances $ 26,635 $ 29,898
        Supplemental cash flow disclosure:
        Cash paid for income taxes, net $ 19,230 $ 7,020"""

        response = generate_recommendations(company, parsed_text)

        return jsonify({"msg": response})
        

    except Exception as e:
        return jsonify({"msg": f"Something went wrong {e}"})
        

@app.route('/extractText', methods=['POST'])
def extractTextFromFile():
    try:

        if 'companyName' not in request.form or not request.form["companyName"]:
            return jsonify({'msg': "Company name not found!"}), 400

        if 'file' not in request.files:
            return jsonify({'msg': "File not found!"}), 400

        company = request.form["companyName"]
        file = request.files['file']

        if not file.filename:
            return jsonify({'msg': "No file selected!"}), 400

        print("File => ", file.filename)


        if not (file and allowed_file(file.filename)):
            return jsonify({'msg': "Incorrect File format"}), 400
            
        filename = secure_filename(file.filename)

        new_directory_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])

        if not os.path.exists(new_directory_path):
            os.makedirs(new_directory_path)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        result = process_pdf(company, file_path)

        if result["err"]: 
            return jsonify({'msg': result["msg"]}), 400

        return jsonify({'msg': result["msg"]}), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'msg': e}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)