import os
import threading
from flask import Flask, request, jsonify
from helperfunction.waSendMessage import sendMessage
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize context storage
session_context = {}
timeout_threads = {}

@app.route('/')
def index():
    return "Welcome to The Curve at the Park chatbot service!"

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        message = request.form['Body'].strip()
        senderId = request.form['From'].split('+')[1]

        # Check if there's an existing context for the user
        if senderId not in session_context:
            session_context[senderId] = {"state": "initial", "last_active": datetime.now()}

        # Reset the timeout timer
        if senderId in timeout_threads:
            timeout_threads[senderId].cancel()
        timeout_threads[senderId] = threading.Timer(200.0, timeout_user, args=[senderId])
        timeout_threads[senderId].start()

        # Handle the message based on the current state
        response_message = handle_message(senderId, message)
        res = sendMessage(senderId=senderId, message=response_message)

        # Update last active time
        session_context[senderId]["last_active"] = datetime.now()

        # Return a JSON response
        return jsonify({
            'status': 'success',
            'message_sid': res.sid,
            'response_message': response_message
        }), 200

    except Exception as e:
        print(f'Error --> {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def timeout_user(senderId):
    if senderId in session_context:
        del session_context[senderId]
    if senderId in timeout_threads:
        del timeout_threads[senderId]
    response_message = "Session timed out due to inactivity. Please start again by saying 'Hello'."
    sendMessage(senderId=senderId, message=response_message)

def handle_message(senderId, message):
    context = session_context[senderId]

    if context["state"] == "initial":
        if message.lower() == "hello":
            context["state"] = "awaiting_name_room"
            return ("Welcome to The Curve at the Park, we are excited to have you stay with us! "
                    "To check in Online, please share your full name and #Room number.")
        else:
            return "Please start the conversation with 'Hello'."

    elif context["state"] == "awaiting_name_room":
        if "#" in message:
            context["name"], context["room_number"] = message.split("#")
            context["state"] = "checked_in"
            return (
                f"We see it's your first time staying with us, {context['name'].strip()}. Welcome again!\n\n"
                "You are now checked in online and can enjoy our app services and hotel amenities.\n\n"
                "Guests are welcome to enjoy the pool, café, and gym. For entertainment, we have a bar & restaurant on the 16th floor.\n\n"
                "For Room Service, you can press 1 for the menu and order here.\n"
                "For Room Amenities, you can press 2.\n"
                "For Fixes and Repairs, you can press 3.\n\n"
                "Enjoy your stay! And don't forget to rate our services for a better experience!"
            )
        else:
            return "Please provide your full name and room number in the format: Your Name #RoomNumber"

    elif context["state"] == "checked_in":
        if message == "1":
            context["state"] = "ordering_food"
            return (
                "The Curve Kitchen Menu:\n"
                "1. Fried Fish - KSH 2,000 (Served with Ugali)\n"
                "2. English Breakfast - KSH 1,000 (Extras available)\n"
                "3. Pancakes - KSH 500 (served with fruits and syrup)\n\n"
                "Please type your order."
            )
        elif message == "2":
            context["state"] = "requesting_amenities"
            return (
                "Our complimentary room amenities include:\n"
                "Blow dryer, towels, soap, bottled water, toilet paper.\n\n"
                "Please state the extra items required and our team will be happy to deliver!"
            )
        elif message == "3":
            context["state"] = "reporting_issues"
            return "Please describe the issue you are experiencing."
        else:
            return "Invalid option. Please press 1 for Room Service, 2 for Room Amenities, or 3 for Fixes and Repairs."

    elif context["state"] == "ordering_food":
        context["order"] = message
        context["state"] = "confirming_food_order"
        return (
            "Would you like anything to drink? Here are the available options:\n"
            "1. Water\n"
            "2. Soda\n"
            "3. Juice\n"
            "4. No drink\n\n"
            "Please type the number of your choice."
        )

    elif context["state"] == "confirming_food_order":
        drinks = {"1": "Water", "2": "Soda", "3": "Juice", "4": "No drink"}
        if message in drinks:
            context["drink"] = drinks[message]
            context["state"] = "food_order_confirmed"
            return "Your order is now being processed."
        else:
            return (
                "Invalid option. Would you like anything to drink? Here are the available options:\n"
                "1. Water\n"
                "2. Soda\n"
                "3. Juice\n"
                "4. No drink\n\n"
                "Please type the number of your choice."
            )

    elif context["state"] == "requesting_amenities":
        context["amenities_request"] = message
        context["state"] = "amenities_requested"
        return "Your request for extra amenities is being processed."

    elif context["state"] == "reporting_issues":
        context["issue"] = message
        context["state"] = "issue_reported"
        return "Your issue has been reported and our team will address it shortly."

    return "Something went wrong. Please try again."

if __name__ == "__main__":
    app.run(port=5000, debug=True)
