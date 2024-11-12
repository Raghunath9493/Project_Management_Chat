import os
from pymongo import MongoClient

# Initialize MongoDB connection
client = MongoClient("mongodb+srv://saich019:sai12345@cluster0.rb7etho.mongodb.net/personal_budget?retryWrites=true&w=majority&appName=Cluster0")
db = client.get_database("personal_budget")

def get_user_by_email(email):
    """Retrieve a user document by email."""
    return db.users.find_one({"email": email})

def save_reset_token(email, token):
    """Save or update a password reset token."""
    db.password_resets.update_one(
        {"email": email},
        {"$set": {"token": token}},
        upsert=True
    )

def save_messaged_user(user_email, messaged_user_email):
    """Add a user to the 'messaged users' list if not already present."""
    if not db.messaged_users.find_one({"user_email": user_email, "messaged_user_email": messaged_user_email}):
        db.messaged_users.insert_one({
            "user_email": user_email,
            "messaged_user_email": messaged_user_email
        })
