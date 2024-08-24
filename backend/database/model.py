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

def generateCompanyAverages(company_name):
    usrs = users.find({"company": company_name})
    count = 0
    issues = {}
    all_traits = {}
    
    for user in usrs:
        reps = user["reports"]
        if reps != []:
            latest_report = max(reps, key=lambda reps: reps["report_id"])
            traits = latest_report["traits"]
            for trait in traits:
                if trait not in all_traits:
                    all_traits[trait] = []
                all_traits[trait].append(traits[trait])
    
    company_averages = {}
    
    for trait, scores in all_traits.items():
        
        if scores:
            mean = np.mean(scores)        
            lower_bound = mean - 0.4
            upper_bound = mean + 0.4
            outliers = [score for score in scores if score < lower_bound or score > upper_bound]
        
            company_averages[trait] = mean
            if len(outliers)/len(scores) > 0.4:
                issues[trait] = 'Yes'
            else:
                issues[trait] = 'No'
    
    return company_averages, issues
print(generateCompanyAverages("Apple, Inc."))
def createNewEmployee(employee_name, employee_email, employee_password, employee_company, linkedin_url):
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

print(assign_cookie("tim.cook@apple.com"))
