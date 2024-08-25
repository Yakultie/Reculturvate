import random
import os
import datetime
from flask import Flask, render_template, request, make_response, url_for, send_from_directory, redirect
from werkzeug.utils import secure_filename
import model

app = Flask(__name__, template_folder='../../frontend/templates')

@app.route('/')
def index():
    return render_template('company-sign-up.html')

@app.route('/company_signup', methods=['GET'])
def company_signup_get():
    return render_template('company-sign-up.html')

@app.route('/company_signup', methods=['POST'])
def company_signup_post():
    company_name = request.form['company_name']
    company_rep_name = request.form['company_rep_name']
    company_email = request.form['company_email']
    password = request.form['password']
    company_created = model.createNewCompany(company_name, company_rep_name, company_email, password)
    if company_created:
        return render_template('company-sign-up.html', msg="Company signed up successfully!")
    else:
        return render_template('company-sign-up.html', msg="Company creation failed, please try again!")

@app.route('/employee_onboard', methods=['GET'])
def employee_onboard_get():
    return render_template('employee-onboarding.html')

@app.route('/employee_onboard', methods=['POST'])
def employee_onboard_post():

    email = request.form['email']
    # validate email exists in unactivated users list
    # not sure what the unactivated usersl ist mean, only has email idk???
    # do logic
    cookie = request.cookies.get("cookie")
    cookie_email = model.login_with_cookie(cookie)
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
    cookie = request.cookies.get("cookie")

    if cookie:
        email_returned = model.login_with_cookie(cookie)
        if email_returned:
            return render_template('dashboard.html', email=email_returned)

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    email_returned = model.login(email, password)
    if email_returned:
        cookie = model.assign_cookie(email)
        resp = make_response(render_template('dashboard.html', email=email))
        resp.set_cookie("cookie", cookie)
        if not is_superuser(email):
            return redirect("/answer_question")
        return resp
    else:
        resp = make_response(render_template('login.html', msg="Unable to login. Please try again!"))
        resp.delete_cookie("cookie")
        return resp
    
@app.route('/logout', methods=['GET'])
def logout_get():
    resp = make_response(redirect('/login'))
    resp.delete_cookie("cookie")
    return resp

@app.route('/answer_question', methods=['GET'])
def answer_question_get():
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    if not email:
        return redirect('/')
    model.resetValue(email)
    question, answer_options = model.getQuestion(0)
    return render_template('questions.html', question=question, answer_options=answer_options, question_id=0)
    
@app.route('/answer_question/<question_id>/<answer_index>', methods=['GET'])
def answer_question_get_next(question_id, answer_index):
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    if not email:
        return redirect('/')
    question, answer_options = model.getQuestion(int(question_id))
    answer_index = int(answer_index)  
    
    question, category = model.getCategory(question_id)
    if category != "section":
        value = question['mappings'][answer_index-1]['value']
    
        cookie = request.cookies.get("cookie")
        email = model.login_with_cookie(cookie)
        model.updateValue(email, category, value)

    new_question_id = int(question_id) + 1
    next_question, next_answer_options = model.getQuestion(new_question_id)

    
    if not next_question:
        generated_report_id = model.generateIndividualReport(email)
        return redirect("/retrieve_individual_report/{0}".format(generated_report_id))
    else:
        return render_template('questions.html', question=next_question, answer_options=next_answer_options, question_id=new_question_id)

@app.route('/retrieve_individual_report/<report_id>', methods=['GET'])
def retrieve_individual_report_get(report_id):
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    report = model.getIndividualReport(email, report_id)
    traits = report["traits"]
    description = report["description"]
    return render_template('individual-report.html', description=description, leadership=(traits["leadership"] * 100), time_management=(traits["time_management"] * 100), communication=(traits["communication"] * 100), adaptability=(traits["adaptability"] * 100), emotional_intelligence=(traits["emotional_intelligence"] * 100), conflict_management=(traits["conflict_management"] * 100))

@app.route('/generate_company_report', methods=["POST"])
def generate_company_report_post():
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    report_averages, issues, report_id = model.generateCompanyAverages(email)
    return redirect("/retrieve_company_report/{0}".format(report_id))

@app.route('/retrieve_company_report/<report_id>', methods=['GET'])
def retrieve_company_report_get(report_id):
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    report = model.retrieveCompanyReport(email, report_id)
    if report != False:
        traits = report["traits"]
        return render_template('report.html', leadership=(traits["leadership"]["score"] * 100), time_management=(traits["time_management"]["score"] * 100), communication=(traits["communication"]["score"] * 100), adaptability=(traits["adaptability"]["score"] * 100), emotional_intelligence=(traits["emotional_intelligence"]["score"] * 100), conflict_management=(traits["conflict_management"]["score"] * 100))
    else:
        return render_template('error.html')

@app.route('/generate_collaborative_report', methods=["POST"])
def generate_collaborative_report_post():
    # do logic
    generated_collaborative_report_id = model.generateCollaborativeReport()
    return redirect("/retrieve_collaborative_report/{0}".format(generated_collaborative_report_id))

@app.route('/retrieve_collaborative_report/<collaborative_report_id>', methods=['GET'])
def collaborative_report_get(collaborative_report_id):
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    report = model.retrieveCompanyReport(email, collaborative_report_id)
    other_company_report = model.retrieveCompanyReport("sergey.brin@google.com", 0)
    if report != False:
        traits_a = report["traits"]
        traits_b = other_company_report["traits"]
        company_a = model.retrieveCompanyNameFromEmail(email),
        company_b = model.retrieveCompanyNameFromEmail("sergey.brin@google.com")
        return render_template('collaborative-report.html', 
                                company_a=company_a,
                                company_b=company_b,
                                leadership_a=(traits_a["leadership"]["score"] * 100), 
                                time_management_a=(traits_a["time_management"]["score"] * 100), 
                                communication_a=(traits_a["communication"]["score"] * 100), 
                                adaptability=(traits_a["adaptability"]["score"] * 100),
                                emotional_intelligence=(traits_a["emotional_intelligence"]["score"] * 100), 
                                conflict_management=(traits_a["conflict_management"]["score"] * 100),
                                leadership_b=(traits_b["leadership"]["score"] * 100),
                                time_management_b=(traits_b["time_management"]["score"] * 100),
                                communication_b=(traits_b["communication"]["score"] * 100),
                                adaptability_b=(traits_b["adaptability"]["score"] * 100),
                                emotional_intelligence_b=(traits_b["emotional_intelligence"]["score"] * 100),
                                conflict_management_b=(traits_b["conflict_management"]["score"] * 100))
    else:
        return render_template('error.html')

# can change int oa post request from dashboard    
@app.route('/retrieve_report_ids', methods=['GET'])
def retrieve_report_ids():
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    report_ids = model.retrieveCompanyReportIdsFromEmail(email)
    if report_ids != False:
        #send it to template somewhere
        # print(report_ids)
        return render_template('collaborative_report.html', report_ids=report_ids)
    else:
        return render_template('error.html')
       
@app.route('/retrieve_valid_company_collaboration_report', methods=['GET'])
def retrieve_valid_company_collaboration_report():
    cookie = request.cookies.get("cookie")
    email = model.login_with_cookie(cookie)
    valid_companies = model.retrieveValidCompanyReports(email)
    # print(valid_companies)
    return render_template('dashboard.html', valid_companies=valid_companies)

if __name__ == "__main__":
    app.run(debug=True)
