import random
import os
import datetime
from flask import Flask, render_template, request, make_response, url_for, send_from_directory, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('company-sign-up.html')

@app.route('/company_signup', methods=['GET'])
def company_signup_get():
    return render_template('company-sign-up.html')

@app.route('/company_signup', methods=['POST'])
def company_signup_post():
    # do logic
    return render_template('company-sign-up.html', msg="Company signed up successfully!")

@app.route('/employee_onboard', methods=['GET'])
def employee_onboard_get():
    return render_template('employee-onboarding.html')

@app.route('/employee_onboard', methods=['POST'])
def employee_onboard_post():
    email = request.form['email']
    # validate email exists in unactivated users list
    # do logic
    return render_template('employee-onboarding.html', email=email)

@app.route('/employee_signup', methods=['POST'])
def employee_signup_post():
    email = request.form['email']
    password = request.form['password']
    linkedin_url = request.form['linkedin_url']
    pronouns = request.form['pronouns']
    # do logic
    return render_template('employee-onboarding.html', msg="Employee signed up successfully!")

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    # do logic
    return render_template('dashboard.html')

@app.route('/answer_question', methods=['POST'])
def answer_question_post():
    # do logic
    question, answer_options = get_next_question()
    if not question:
        generated_report_id = generate_individual_report()
        return redirect("/retrieve_individual_report/{0}".format(generated_report_id))
    else:
        return render_template('questions.html', question=question, answer_options = [])

@app.route('/retrieve_individual_report/<report_id>', methods=['GET'])
def retrieve_individual_report_get(report_id):
    # do logic
    return render_template('individual_report.html')

@app.route('/generate_company_report', methods=["POST"])
def generate_company_report_post():
    # do logic
    generated_company_report_id = generate_company_report()
    return redirect("/retrieve_company_report/{0}".format(generated_company_report_id))

@app.route('/retrieve_company_report/<report_id>', methods=['GET'])
def retrieve_company_report_get(report_id):
    # do logic
    return render_template('company_report.html')

@app.route('/generate_collaborative_report', methods=["POST"])
def generate_collaborative_report_post():
    # do logic
    generated_collaborative_report_id = generate_collaborative_report()
    return redirect("/retrieve_collaborative_report/{0}".format(generated_collaborative_report_id))

@app.route('/retrieve_collaborative_report/<report_id>', methods=['GET'])
def collaborative_report_get(collaborative_report_id):
    # do logic
    return render_template('collaborative_report.html')

if __name__ == "__main__":
    app.run(debug=True)
