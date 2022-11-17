from flask import render_template, Flask, request
import numpy as np
import pandas as pd
import pickle
import requests
import os

app = Flask(__name__, template_folder='templates')
model = pickle.load(open('rf.pkl', 'rb'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/predict.html', methods=['GET'])
def form():
    return render_template('predict.html')

@app.route('/submit.html', methods=['POST'])
def predict():
    Applicant_Name, Gender, Married, Dependents, Education, Self_Employed, ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History, Property_Area = [x for x in request.form.values()]

    if Gender == 'Male':
        Gender = 1
    else:
        Gender = 0

    if Married == 'Yes':
        Married = 1
    else:
        Married = 0

    if Dependents == '3+':
        Dependents = 3
    Dependents=int(Dependents)
    
    if Education == 'Graduate':
        Education = 0
    else:
        Education = 1

    if Self_Employed == 'Yes':
        Self_Employed = 1
    else:
        Self_Employed = 0

    ApplicantIncome = int(ApplicantIncome)
    CoapplicantIncome = int(CoapplicantIncome)
    LoanAmount = int(LoanAmount)
    Loan_Amount_Term = int(Loan_Amount_Term)
    emi=LoanAmount//Loan_Amount_Term
    LoanAmount = int(LoanAmount)//1000

    flag=1
    if emi>0.4*ApplicantIncome:
        flag=0

    if Credit_History == 'Yes':
        Credit_History = 1
    else:
        Credit_History = 0

    if Property_Area == 'Urban':
        Property_Area = 3
    elif Property_Area == 'Semi-Urban':
        Property_Area = 2
    elif Property_Area == 'Rural':
        Property_Area = 1
    else:
        Property_Area = 0
      
    headers = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'ApplicantIncome',
                'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Property_Area']
    features = [Gender, Married, Dependents, Education, Self_Employed, ApplicantIncome,
                CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History, Property_Area]

    API_KEY = "iyf1_HmB2bORijpoH0dAVju3kmTZGCiq9l3S4AOHZDpv"
    url = 'https://iam.cloud.ibm.com/identity/token'
    data = {"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'}
    token_response = requests.post(url, data=data)
    mltoken = token_response.json()["access_token"]
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    data = {"input_data": [{"fields": [headers], "values": [features]}]}
    url = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/10c5e1b3-cbb6-42f4-8faa-7c183ba289ed/predictions?version=2022-11-17'
    headers = {'Authorization': 'Bearer ' + mltoken}
    response = requests.post(url, json=data, headers=header).json()
    prediction = response['predictions'][0]['values'][0][0]
    
    if prediction == 1 and flag==1: 
        return render_template('submit.html', result='Congrats '+Applicant_Name+'! You are eligible for the loan!')
    else:
        return render_template('submit.html', result='Sorry '+Applicant_Name+', you are not eligible for a loan!')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True)
