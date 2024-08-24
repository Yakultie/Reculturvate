import os
import pymongo
from datetime import datetime

mongo_client = pymongo.MongoClient(os.environ["MONGODB_CONNECTION_STRING"])
mongo_db = mongo_client["brij"]
companies = mongo_db["companies"]
question_bank = mongo_db["question_bank"]
users = mongo_db["users"]

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
            "reports": []
        }
    )

    return True

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
            "reports": []
        }
    )   
    return True

print(createNewEmployee("Yanney OU","yaedb@gmail.com","meowmeow","ABC Inc.", "yabsdjhb"))
