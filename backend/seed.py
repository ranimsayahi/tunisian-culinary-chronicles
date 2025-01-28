from db import db
from Models import Season, CelebrationModel, EthnicityModel

SEASONS = [
    {"Season": "Spring", "Description": "A season for fresh herbs and vibrant salads, celebrating the bounty of local vegetables."},
    {"Season": "Summer", "Description": "Time for refreshing dishes that are perfect for combatting the heat."},
    {"Season": "Autumn", "Description": "A harvest season rich in flavors, featuring the warmth of spices in traditional dishes."},
    {"Season": "Winter", "Description": "Comforting meals and warming spices, ideal for cozy gatherings."},
]

CELEBRATIONS = [
    {"Name": "Eid", "Description": "A major Islamic holiday celebrating the end of Ramadan."},
    {"Name": "Ramadan", "Description": "The holy month of fasting for Muslims."},
    {"Name": "Eid el-Adha", "Description": "A major Islamic holiday that begins with a prayer, followed by the sacrifice of an animal, symbolizing devotion and faith."},
    {"Name": "Weddings", "Description": "Ceremonial meals to celebrate weddings."},
]

ETHNICITIES = [
    {"Name": "Tunisian", "Description": "Ethnicity native to Tunisia."},
    {"Name": "Berber", "Description": "Indigenous North African ethnicity."},
    {"Name": "Arab", "Description": "Ethnic group native to the Arab world."},
    {"Name": "Jewish", "Description": "Ethnic and religious group originating from the Hebrews."},
]

def seed_data():
    for season in SEASONS:
        if not Season.query.filter_by(Season=season["Season"]).first():  
            db.session.add(Season(**season))

    for celebration in CELEBRATIONS:
        if not CelebrationModel.query.filter_by(Name=celebration["Name"]).first():  
            db.session.add(CelebrationModel(**celebration, Status="Approved"))  

    for ethnicity in ETHNICITIES:
        if not EthnicityModel.query.filter_by(Name=ethnicity["Name"]).first():  
            db.session.add(EthnicityModel(**ethnicity,Status="Approved")) 

    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
