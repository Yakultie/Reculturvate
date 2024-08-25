import os
import random
import pymongo
import string
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import numpy as np

mongo_client = pymongo.MongoClient(os.environ["MONGODB_CONNECTION_STRING"])
mongo_db = mongo_client["brij"]
companies = mongo_db["companies"]
question_bank = mongo_db["question_bank"]
users = mongo_db["users"]

def gpt4(question, temperature=0.0):
    llm = ChatOpenAI(temperature=temperature, model_name="gpt-4-0613")
    
    prompt = PromptTemplate(template="{question}", input_variables=["question"])

    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    response = llm_chain.invoke({"question": question})
    
    return response["text"]

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
                # Append the score directly
                all_traits[trait].append(score_data)

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

    companies.update_one(
        {"company_name": company_name},
        {"$set": {"note": issues}}
    )
    
    return company_averages, issues

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
print(assign_cookie("tim.cook@apple.com"))

def writeIndividualReportDescription(email, report_id):
    found_user = users.find_one({"email": email})
    if not found_user:
        return None
        
    reports = found_user.get("reports", [])
    report = next((r for r in reports if int(r["report_id"]) == int(report_id)), None)
    if not report:
        return None
    
    report["description"] = gpt4("""{{
    "system_message": "Each trait is measured on a scale from 0 to 1, where 0 and 1 do not directly suggest the absence or presence of any trait.",
    "trait_descriptions": {{
        "time_management": "This trait, when assigned a value closer to 0, suggests a preference for a relaxed, casual and spontaneous attitude, whereas a value closer to 1 would suggest a preference for strict order and planning.",
        "communication": "This trait, when assigned a value closer to 0, suggests a passive communication style whereas a value closer to 1 would suggest a more active communication style.",
        "adaptability": "This trait, when assigned a value closer to 0, suggests an attitude where an established plan should be followed to the letter as much as possible whereas a value closer to 1 would suggest a more spontaneous and readily changing attitude.",
        "teamwork": "This trait, when assigned a value closer to 0, suggests individuality, self-sufficiency and the independent completion of tasks whereas a value closer to 1 would suggest an inter-dependent culture where work is delegated and shared.",
        "leadership_structure": "This trait, when assigned a value closer to 0, suggests a top-down, hierarchical leadership structure whereas a value closer to 1 would suggest a flat structure."
    }}
}}

{{
    "traits": {{
        "time_management": 0.8,
        "communication": 0.9,
        "adaptability": 0.3,
        "teamwork": 0.6,
        "leadership_structure": 1
    }},
    "instructions": "Given the above traits and measurements, please provide a description of the traits possessed by this person with an action plan for each trait.",
    "description": "Based on the provided traits and measurements, this person demonstrates a strong preference for order and planning, suggesting they are well-organised and prefer structured environments. Their communication style is active, indicating they are likely to be assertive, clear, and proactive in expressing ideas and expectations. However, they exhibit a tendency to adhere to established plans and a potential discomfort with sudden changes or ambiguity. They display a moderate preference for teamwork, balancing between working independently and collaboratively. Lastly, they strongly prefer a flat leadership structure, which implies a preference for egalitarianism and decentralised decision-making. \n\nContinue leveraging your strong preference for order and planning by implementing detailed schedules and clear goals to maintain productivity and reduce stress. Utilise your active communication style to foster an environment where ideas and expectations are clearly communicated. Promote regular feedback sessions to enhance transparency and ensure everyone is on the same page. Introduce gradual changes and provide ample notice when shifts are needed. Build resilience in handling unexpected situations or alterations to established plans. Continue to balance independent and collaborative work by assigning tasks that allow for both personal accountability and team interaction. Support a flat leadership approach by encouraging open dialogue and inclusive decision-making processes. Empower all team members to contribute ideas and participate in leadership roles, fostering a sense of ownership and mutual respect."
}}

{{
    "traits": {{
        "time_management": 0.0,
        "communication": 0.0,
        "adaptability": 0.0,
        "teamwork": 0.0,
        "leadership_structure": 0.0
    }},
    "instructions": "Given the above traits and measurements, please provide a description of the traits possessed by this person with an action plan for each trait.",
    "description": "Based on the provided traits and measurements, this person demonstrates a preference for a relaxed, casual, and spontaneous attitude towards time management, suggesting they may not be overly concerned with strict order and planning. Their communication style is passive, indicating they may be more reserved and less assertive in expressing ideas and expectations. They exhibit a strong tendency to adhere to established plans and may be uncomfortable with sudden changes or ambiguity. They display a strong preference for individuality, self-sufficiency, and the independent completion of tasks, suggesting they may prefer working alone rather than in a team. Lastly, they strongly prefer a top-down, hierarchical leadership structure, which implies a preference for clear lines of authority and decision-making. \n\nConsider implementing some level of structure and planning to your daily routine to improve productivity and reduce potential stress. Work on improving your communication skills by being more proactive in expressing your ideas and expectations. Try to be more open to changes and adapt to new situations as this can be a valuable skill in today's fast-paced world. While it's good to be self-sufficient, remember that teamwork can also be beneficial in achieving larger goals. Try to involve yourself more in team activities and learn to delegate tasks when necessary. Lastly, while a hierarchical structure has its benefits, it's also important to encourage open communication and feedback from all levels of the team. This can lead to more informed decision-making and a more engaged and motivated team.",
}}

{{
    "traits": {0},
    "instructions": "Given the above traits and measurements, please provide a description of the traits possessed by this person with an action plan for each trait.",
    "description": "
    """.format(report["traits"])).rstrip('"')

    users.update_one({"email": email}, {"$set": {"reports": reports}})
    return True
