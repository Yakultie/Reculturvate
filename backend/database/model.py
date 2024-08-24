import os
import random
import pymongo
import string
from datetime import datetime
import numpy as np

mongo_client = pymongo.MongoClient(os.environ["MONGODB_CONNECTION_STRING"])
mongo_db = mongo_client["brij"]
companies = mongo_db["companies"]
question_bank = mongo_db["question_bank"]
users = mongo_db["users"]

def generate_secure_cookie():
    """Generates a secure random cookie."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))

def assign_cookie(email):
    found_user = users.find_one({"email": email})
    if not found_user:
        return None
    
    new_cookie = generate_secure_cookie()
    users.update_one({"email": email}, {"$set": {"cookie": new_cookie}})

    return new_cookie

def login_with_cookie(cookie):
    found_user = users.find_one({"cookie": cookie})
    if not found_user:
        return None

    return found_user["email"]

def login(email, password):
    found_user = users.find_one({"email": email})
    if not found_user:
        return None
    
    if found_user["password"] == password:
        return email

def createNewCompany(company_name, admin_full_name, admin_email, password):
    found_company = companies.find_one({"company_name": company_name})
    found_user = users.find_one({"email": admin_email})

    if found_company:
        #company already exists
        return False
    
    if found_user:
        #user with admin email address already exists
        return False
    
    companies.insert_one(
        {
            "company_name": company_name,
            "power_users": [
                {
                    "name": admin_full_name,
                    "email": admin_email
                }
            ],
            "employees": [],
            "internal_reports": [],
            "collaborative_reports": []
        }
    )

    users.insert_one(
        {
            "name": admin_full_name,
            "company": company_name,
            "email": admin_email,
            "password": password,
            "linkedin_url": None,
            "pronouns": None,
            "cookie": None,
            "reports": []
        }
    )

    return True

def generateCompanyAverages(email):
    found_user = users.find_one({"email": email})
    if not found_user:
        return False
    
    company_name = found_user["company"]
    found_company = companies.find_one({"company_name": company_name})
    power_users = found_company["power_users"]
    
    is_power_user = any(entry['email'] == email for entry in power_users)
    if not is_power_user:
        return False
    
    usrs = users.find({"company": company_name})
    all_traits = {}
    issues = {}
    
    for user in usrs:
        reps = user.get("reports", [])
        if reps:
            latest_report = max(reps, key=lambda report: report["report_id"])
            traits = latest_report["traits"]
            for trait, score_data in traits.items():
                if trait not in all_traits:
                    all_traits[trait] = []
                # Append the score directly if it's a float
                if isinstance(score_data, dict):
                    all_traits[trait].append(score_data.get("score", 0.0))
                else:
                    all_traits[trait].append(score_data)
                    
    company_averages = {}
    
    for trait, scores in all_traits.items():
        if scores:
            mean = np.mean(scores)
            lower_bound = mean - 0.4
            upper_bound = mean + 0.4
            outliers = [score for score in scores if score < lower_bound or score > upper_bound]
        
            company_averages[trait] = mean
            if len(outliers) / len(scores) > 0.4:
                issues[trait] = 'Yes'
            else:
                issues[trait] = 'No'

    # Create a new report
    new_report_id = max([report["report_id"] for report in found_company.get("internal_reports", [])], default=-1) + 1
    new_report = {
        "report_id": new_report_id,
        "company_name": company_name,
        "report_averages": company_averages,
        "issues": issues,
        "description": "Generated company report based on user data",
        "work_culture_type": ""
    }
    

    companies.update_one(
        {"company_name": company_name},
        {"$push": {"internal_reports": new_report}}
    )
    
    return company_averages, issues, new_report_id

def createNewEmployee(employee_name, employee_email, employee_password, employee_company, linkedin_url, pronouns):
    found_employee_email = users.find_one({"email": employee_email})
    found_employee_company = companies.find_one({"company_name": employee_company})
    
    if found_employee_email:
        print(employee_email + " is an existing email")
        return False

    if not found_employee_company:
        print(employee_company + " is not an existing company")
        return False
    
    users.insert_one(
        {
            "name": employee_name,
            "company": employee_company,
            "email": employee_email,
            "password": employee_password,
            "linkedin_url": linkedin_url,
            "pronouns": pronouns,
            "cookie": None,
            "reports": []
        }
    )   
    return True

def retrieveCompanyReportFromEmail(email, report_id):
    found_user = users.find_one({"email": email})
    if not found_user:
        return False
    company_name = found_user["company"]
    found_company = companies.find_one({"company_name": company_name})
    power_users = found_company["power_users"]
    for entry in power_users:
        if entry['email'] == email:
            reports = found_company['internal_reports']
            print(reports)
            for report in reports:
                if int(report["report_id"]) == int(report_id):
                    return report
    else:
        return False
    
def retrieveValidCompanyReports(email):
    companies_with_reports = companies.find({
        "internal_reports": {"$exists": True, "$ne": []},
        "$nor": [  
            {"power_users.email": email},
            {"employees.email": email}
        ]
    })
    company_names = [company.get("company_name") for company in companies_with_reports]
    return company_names

def getIndividualReport(email, report_id):
    found_user = users.find_one({"email": email})
    if not found_user:
        return None
    reports = found_user.get("reports", [])
    report = next((r for r in reports if int(r["report_id"]) == int(report_id)), None)
    return report

def retrieveCompanyReport(email, report_id):
    user = users.find_one({"email": email})
    if not user:
        return False
    company_name = user.get("company")
    
    if not company_name:
        return False
    company = companies.find_one({"company_name": company_name})
    if not company or not any(user['email'] == email for user in company.get("power_users", [])):
        return False
    reports = company.get("internal_reports", [])
    for report in reports:
        if int(report["report_id"]) == int(report_id):
            return report
    return False

def getQuestion(n):
    found_question = question_bank.find_one({"question_id": n})
    question = found_question["question"]
    answer_options = [x["answer"] for x in found_question["mappings"]]
    return question, answer_options