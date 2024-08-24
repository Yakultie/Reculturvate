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

def generate_company_averages(company_name):
    usrs = users.find({"company": company_name})
    count = 0
    company_total = {}
    for user in usrs:
        reps = user["reports"]
        if reps != []:
            latest_report = max(reps, key=lambda reps: reps["report_id"])
            traits = latest_report["traits"]
            for trait in traits:
                company_total[trait] = company_total.setdefault(trait, 0) + traits[trait]
            count += 1
    company_averages = {key: value / count for key, value in company_total.items()}
    return company_averages

# print(createNewCompany("BERNARDINO Inc.", "BERNADINO Admin", "BERNADINO@.com", "password"))
print(generate_company_averages("Apple, Inc."))
