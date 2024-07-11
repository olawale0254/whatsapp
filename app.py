import os
from flask import Flask, request, jsonify
from helperfunction.waSendMessage import sendMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize context storage
session_context = {}

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
            session_context[senderId] = {"state": "initial"}

        # Handle the message based on the current state
        response_message = handle_message(senderId, message)
        res = sendMessage(senderId=senderId, message=response_message)

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
            return (f"We see it's your first time staying with us, {context['name'].strip()}. Welcome again! "
                    "You are now checked in online and can enjoy our app services and hotel amenities. "
                    "Guests are welcome to enjoy the pool, café, and gym. For entertainment, we have a bar & restaurant on the 16th floor. "
                    "For Room Service, you can press 1 for the menu and order here. "
                    "For Room Amenities, you can press 2. "
                    "For Fixes and Repairs, you can press 3. "
                    "Enjoy your stay! And don't forget to rate our services for a better experience!")
        else:
            return "Please provide your full name and room number in the format: Your Name #RoomNumber"

    return "Something went wrong. Please try again."

if __name__ == "__main__":
    app.run(port=5000, debug=True)
