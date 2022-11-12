from flask import render_template, Flask, request
import numpy as np
import pickle
import os

app = Flask(__name__, template_folder='templates')
model = pickle.load(open('rdf.pkl', 'rb'))
scale = pickle.load(open('scalar.pkl', 'rb'))

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
    appname, gender, married, depend, education, self_emp, applicant_income, co_income, loan_amount, loan_term, credit_history, property_area = [x for x in request.form.values()]

    if gender == 'Male':
        gender = 1
    else:
        gender = 0

    if married == 'Yes':
        married = 1
    else:
        married = 0

    if education == 'Graduate':
        education = 0
    else:
        education = 1

    if self_emp == 'Yes':
        self_emp = 1
    else:
        self_emp = 0

    if depend == '3+':
        depend = 3

    applicant_income = int(applicant_income)
    applicant_income = np.log(applicant_income)
    loan_amount = int(loan_amount)
    loan_amount = np.log(loan_amount)

    if credit_history == 'Yes':
        credit_history = 1
    else:
        credit_history = 0

    if property_area == 'Urban':
        property_area = 2
    elif property_area == 'Rural':
        property_area = 0
    else:
        property_area = 1

    features = [gender, married, depend, education, self_emp, applicant_income,
                co_income, loan_amount, loan_term, credit_history, property_area]
    con_features = [np.array(features)]

    scale_features = scale.fit_transform(con_features)
    prediction = model.predict(scale_features)
    print(prediction)

    if prediction == 0:
        return render_template('submit.html', result='You are eligible for the loan!')
    else:
        return render_template('submit.html', result='Sorry, you are not eligible for a loan!')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False)
