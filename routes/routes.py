# routes/routes.py

import sys
import os
import uuid
from flask import render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from email_utils import send_email  # Import the send_email function
from datetime import timedelta, datetime
import json
from bson import ObjectId
from database import save_messaged_user
from better_profanity import profanity
import logging

def register_routes(app):
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    client = MongoClient(app.config['MONGO_URI'])
    db = client.get_database("personal_budget")

    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')

    @app.route('/register', methods=["POST"])
    def register():
        email = request.form.get("email")
        password = request.form.get("password")
        nickname = request.form.get("nickname")
        favorite_food = request.form.get("favorite_food")
        favorite_movie = request.form.get("favorite_movie")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})
        if user:
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = {"email": email, "password": hashed_password, "nickname": nickname,
                "favorite_food": favorite_food, "favorite_movie": favorite_movie}

        db.users.insert_one(user)

        return jsonify({"message": "Registration successful"}), 201

    @app.route('/login', methods=["POST"])
    def login():
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            access_token = create_access_token(identity={"email": email})
            session['email'] = email
            response = jsonify({"message": "Login successful"})
            response.headers["Authorization"] = f"Bearer {access_token}"
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    @app.route('/dashboard', methods=['GET'])
    @jwt_required(optional=True)
    def dashboard():
        if 'email' not in session:
            return redirect(url_for('home'))
        return render_template('dashboard.html')

    @app.route('/logout', methods=['GET'])
    def logout():
        session.clear()
        return jsonify({"message": "Logged out successfully"})

    @app.route('/budgetform', methods=['GET', 'POST'])
    def budget_form():
        if 'email' not in session:
            return redirect(url_for('home'))
        return render_template('budgetform.html')
    
    @app.route('/api/budget_data', methods=['GET'])
    def get_budget_data():
        if 'email' not in session:
            return jsonify({"error": "Unauthorized"}), 401

        email = session['email']
        try:
            budget_data = db.budgets.find_one({"email": email}, {"_id": 0})
            if budget_data:
                return jsonify(budget_data)
            else:
                return redirect(url_for('budget_form'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/budget_data', methods=['POST'])
    def post_budget_data():
        if 'email' not in session:
            return jsonify({"error": "Unauthorized"}), 401

        email = session['email']
        form_data = request.get_json()
        if not form_data:
            return jsonify({"error": "No data provided"}), 400

        # Extract and save form data
        try:
            db.budgets.update_one(
                {'email': email},
                {
                    '$set': form_data
                },
                upsert=True
            )
            return jsonify({"message": "Budget data saved successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'email' not in session:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            form_data = request.get_json()
            if not form_data:
                return jsonify({"error": "No data provided"}), 400

            first_name = form_data.get('firstName')
            last_name = form_data.get('lastName')
            email = form_data.get('email')
            phone_number = form_data.get('phoneNumber')

            # Ensure email from form data matches the session email
            if email != session['email']:
                return jsonify({"error": "Email mismatch"}), 400

            try:
                # Update or insert the profile data
                db.profiles.update_one(
                    {'email': email},
                    {'$set': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone_number': phone_number
                    }},
                    upsert=True
                )
                return jsonify({"message": "Profile data saved successfully"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return render_template('profile.html')

    @app.route('/get_profile', methods=['GET'])
    def get_profile():
        if 'email' not in session:
            return redirect(url_for('home'))

        email = session['email']
        profile = db.profiles.find_one({"email": email})

        if profile:
            return jsonify({
                "firstName": profile.get('first_name', ''),
                "lastName": profile.get('last_name', ''),
                "email": profile.get('email', ''),
                "phoneNumber": profile.get('phone_number', '')
            })
        else:
            return jsonify({
                "firstName": "",
                "lastName": "",
                "email": "",
                "phoneNumber": ""
            })

    @app.route('/transactions', methods=['GET', 'POST'])
    def transactions():
        if 'email' not in session:
            return redirect(url_for('home'))

        if request.method == 'POST':
            form_data = request.get_json()
            event_name = form_data.get('event_name')
            event_date = form_data.get('event_date')
            category = form_data.get('category')
            description = form_data.get('description', '')  # Optional field
            price = form_data.get('price')

            if not event_name or not event_date or not category or not price:
                return jsonify({"error": "All required fields must be filled out"}), 400

            try:
                db.transactions.insert_one({
                    'email': session['email'],
                    'event_name': event_name,
                    'event_date': event_date,
                    'category': category,
                    'description': description,
                    'price': float(price)
                })
                return jsonify({"message": "Transaction saved successfully"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return render_template('transactions.html')

    @app.route('/get_transactions', methods=['GET'])
    def get_transactions():
        logged_in_user = session.get('email')  # Get the logged-in user
        if not logged_in_user:
            return jsonify({'error': 'User not logged in'}), 401

        try:
            # Fetch transactions from the database for the logged-in user
            user_transactions = list(db.transactions.find({'email': logged_in_user}))
            
            # Calculate the total amount
            total_amount = sum(transaction['price'] for transaction in user_transactions)

            # Format transactions for the frontend
            formatted_transactions = [
                {
                    '_id': str(transaction['_id']),  # Convert ObjectId to string
                    'event_name': transaction['event_name'],
                    'event_date': transaction['event_date'],
                    'category': transaction['category'],
                    'description': transaction.get('description', ''),  # Optional field
                    'price': transaction['price']
                }
                for transaction in user_transactions
            ]

            return jsonify({'transactions': formatted_transactions, 'total': total_amount}), 200
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return jsonify({'error': 'Unable to fetch transactions'}), 500

    # @app.route('/forgot_password', methods=['POST'])
    # def forgot_password():
    #     print("here at forgot")
    #     data = request.get_json()  # Get JSON data
    #     email = data.get('email')  # Extract email from JSON data

    #     if not email:
    #         return jsonify({"error": "Email is required"}), 400

    #     user = db.users.find_one({"email": email})
    #     print("user found", user)
    #     if not user:
    #         return jsonify({"error": "User not found"}), 404
    #     print("passw",user["password"])
        
    #     subject = "Password Reset Request"
    #     body = f"Your password is: {user["password"]}"
        
    #     try:
    #         send_email(subject, body, email)
    #         return jsonify({"message": "Password reset email sent"}), 200
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500

    @app.route('/forgot_password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        nickname = data['nickname']
        favorite_food = data['favorite_food']
        favorite_movie = data['favorite_movie']

        # Find user by security answers
        user = db.users.find_one({
            'nickname': nickname,
            'favorite_food': favorite_food,
            'favorite_movie': favorite_movie
        })

        if user:
            # Generate a token (can be a random string)
            token = str(uuid.uuid4())
            db.password_resets.insert_one({"email": user['email'], "token": token})

            return jsonify({'message': 'Security answers verified', 'token': token}), 200
        else:
            return jsonify({'error': 'Incorrect security answers'}), 400


    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        token = request.args.get('token')
        if request.method == 'POST':
            data = request.get_json()
            new_password = data.get('password')

            if not new_password:
                return jsonify({"error": "Password is required"}), 400

            reset_entry = db.password_resets.find_one({"token": token})
            if not reset_entry:
                return jsonify({"error": "Invalid or expired token"}), 400

            email = reset_entry['email']
            user = db.users.find_one({"email": email})

            # Check if the new password matches the old password
            if bcrypt.check_password_hash(user['password'], new_password):
                return jsonify({"error": "New password is the same as the old password. Please choose a different password."}), 400

            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Update user's password
            db.users.update_one(
                {"email": email},
                {"$set": {"password": hashed_password}}
            )

            # Remove the token entry after successful password reset
            db.password_resets.delete_one({"token": token})

            return jsonify({"message": "Password has been reset successfully"}), 200

        return render_template('reset_password.html', token=token)

   

    @app.route('/delete_transaction', methods=['DELETE'])
    def delete_transaction():
        if 'email' not in session:
            return jsonify({"error": "Unauthorized"}), 401

        email = session['email']
        transaction_id = request.args.get('transaction_id')

        if not transaction_id:
            return jsonify({"error": "Transaction ID is required"}), 400

        try:
            result = db.transactions.delete_one({"_id": ObjectId(transaction_id), "email": email})
            if result.deleted_count == 1:
                return jsonify({"message": "Transaction deleted successfully"}), 200
            else:
                return jsonify({"error": "Transaction not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/chats')
    def chats():
        user_email = session.get('user_email')  # Get the logged-in user's email
        chat_users = db.chats.find({"participants": user_email})  # Fetch chat members for the user

        # Extract unique users from the chat history
        users = set()
        for chat in chat_users:
            users.update(chat['participants'])  # Assuming 'participants' is a list of email addresses

        # Fetch user details from the database
        user_details = []
        for email in users:
            user_info = db.users.find_one({"email": email})
            if user_info:
                user_details.append(user_info)

        return render_template('chats.html', users=user_details)

    
    # Initialize logging
    logging.basicConfig(level=logging.INFO)

    # Load the default list of profane words
    custom_harmful_words = ["bomb", "bombs", "drug", "drugs", "terrorist", "terrorists", "attack", "attacks", "weapon", "weapons"]
    profanity.add_censor_words(custom_harmful_words)

    @app.route('/api/send_message', methods=['POST'])
    def send_message():
        try:
            data = request.json
            sender = data.get('sender')
            recipient = data.get('recipient')
            content = data.get('message')

            if not sender or not recipient or not content:
                return jsonify({'error': 'Sender, recipient, and message content are required'}), 400

            # Check if the message contains any profane or harmful words
            if profanity.contains_profanity(content):
                return jsonify({'error': 'Message contains prohibited content and cannot be sent'}), 403

            # Save the message to the database if it does not contain profane words
            db.messages.insert_one({
                "sender": sender,
                "recipient": recipient,
                "content": content,
                "timestamp": datetime.now()
            })

            return jsonify({'message': 'Message sent successfully'})
        
        except Exception as e:
            # Log the error
            logging.error(f"Error in send_message: {e}")
            return jsonify({'error': 'An internal error occurred'}), 500
    
    @app.route('/api/get_messages', methods=['GET'])
    def get_messages():
        logged_in_user = session.get('email')
        if not logged_in_user:
            return jsonify({'error': 'User not logged in'}), 401

        sender = request.args.get('sender')
        recipient = request.args.get('recipient')

        if not sender or not recipient:
            return jsonify({'error': 'Missing sender or recipient'}), 400

        try:
            # Query messages from MongoDB
            user_messages = list(db.messages.find({
                '$or': [
                    {'sender': sender, 'recipient': recipient},
                    {'sender': recipient, 'recipient': sender}
                ]
            }).sort('timestamp', 1))  # Sort by timestamp in ascending order

            # Format messages for JSON response
            formatted_messages = [
                {
                    '_id': str(message['_id']),
                    'sender': message['sender'],
                    'recipient': message['recipient'],
                    'content': message['content'],
                    'timestamp': message['timestamp']
                }
                for message in user_messages
            ]

            return jsonify(formatted_messages), 200

        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return jsonify({'error': 'Unable to retrieve messages'}), 500



    @app.route('/api/search_users', methods=['GET'])
    @jwt_required(optional=True)
    def search_users():
        """Search for users matching the query parameter."""
        query = request.args.get('query', '')
        if not query:
            return jsonify([])  # If no query, return empty array

        try:
            users = list(db.users.find({"$or": [
                {"nickname": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]}).limit(10))

            # Return only the required fields
            return jsonify([{"nickname": user["nickname"], "email": user["email"]} for user in users])
        except Exception as e:
            return jsonify({"error": "An error occurred while searching for users", "details": str(e)}), 500

    MESSAGED_USERS = {}  # Keep in-memory storage

    @app.route('/api/add_chat', methods=['POST'])
    def add_chat():
        logged_in_user = session.get('email')
        if not logged_in_user:
            return jsonify({'error': 'User not logged in'}), 401

        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        email = data['email']

        # Initialize messaged users for the logged-in user if not present
        if logged_in_user not in MESSAGED_USERS:
            MESSAGED_USERS[logged_in_user] = []

        # Add the new user if not already in the list
        if email not in [user['email'] for user in MESSAGED_USERS[logged_in_user]]:
            MESSAGED_USERS[logged_in_user].append({'email': email})

        return jsonify({'success': True}), 200


    @app.route('/api/get_messaged_users', methods=['GET'])
    def get_messaged_users():
        logged_in_user = session.get('email')
        if not logged_in_user:
            return jsonify({'error': 'User not logged in'}), 401

        # Return the list of messaged users for the logged-in user
        messaged_users = MESSAGED_USERS.get(logged_in_user, [])
        return jsonify(messaged_users), 200
   
    
    @app.route('/api/delete_message', methods=['DELETE'])
    def delete_message():
        logged_in_user = session.get('email')
        if not logged_in_user:
            return jsonify({'error': 'User not logged in'}), 401

        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        try:
            message_id = data['id']

            # Ensure the ID is a valid ObjectId
            if not ObjectId.is_valid(message_id):
                return jsonify({'error': 'Invalid message ID'}), 400

            # Delete the message if the sender matches the logged-in user
            result = db.messages.delete_one({
                '_id': ObjectId(message_id),
                'sender': logged_in_user
            })

            if result.deleted_count == 1:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Message not found or not authorized'}), 404

        except Exception as e:
            print(f"Error deleting message: {e}")
            return jsonify({'error': 'Failed to delete the message'}), 500
