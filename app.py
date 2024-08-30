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
    return "Welcome to Book Haven!"

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
            context["state"] = "browsing_books"
            return ("Welcome to Book Haven, your one-stop shop for the best books! "
                    "To get started, type 'Browse' to see our categories or 'Search' to find a specific book.")
        else:
            return "Please start the conversation with 'Hello'."

    elif context["state"] == "browsing_books":
        if message.lower() == "browse":
            context["state"] = "viewing_categories"
            return (
                "Here are our categories:\n"
                "1. Fiction\n"
                "2. Non-fiction\n"
                "3. Science Fiction\n"
                "4. Mystery\n"
                "5. Children's Books\n\n"
                "Please type the number of the category you want to explore."
            )
        elif message.lower() == "search":
            context["state"] = "searching_books"
            return "Please enter the title or author of the book you're looking for."
        else:
            return "Invalid option. Please type 'Browse' or 'Search'."

    elif context["state"] == "viewing_categories":
        categories = {"1": "Fiction", "2": "Non-fiction", "3": "Science Fiction", "4": "Mystery", "5": "Children's Books"}
        if message in categories:
            context["category"] = categories[message]
            context["state"] = "selecting_books"
            return (
                f"Here are some popular books in the {context['category']} category:\n"
                "1. Book A\n"
                "2. Book B\n"
                "3. Book C\n\n"
                "Please type the number of the book you'd like to order, or type 'Back' to view categories again."
            )
        else:
            return "Invalid option. Please type the number of the category you want to explore."

    elif context["state"] == "selecting_books":
        if message.lower() == "back":
            context["state"] = "browsing_books"
            return ("Here are our categories:\n"
                    "1. Fiction\n"
                    "2. Non-fiction\n"
                    "3. Science Fiction\n"
                    "4. Mystery\n"
                    "5. Children's Books\n\n"
                    "Please type the number of the category you want to explore.")
        elif message in ["1", "2", "3"]:
            context["selected_book"] = f"Book {message}"
            context["state"] = "confirming_order"
            return (
                f"You have selected {context['selected_book']}. Would you like to place the order? (Yes/No)"
            )
        else:
            return "Invalid option. Please type the number of the book you'd like to order, or type 'Back' to view categories again."

    elif context["state"] == "confirming_order":
        if message.lower() == "yes":
            context["state"] = "order_placed"
            return (
                f"Your order for {context['selected_book']} has been placed successfully! "
                "Thank you for shopping with Book Haven. Your book will be delivered soon."
            )
        elif message.lower() == "no":
            context["state"] = "browsing_books"
            return "Order canceled. Type 'Browse' to view categories or 'Search' to find a specific book."
        else:
            return "Please respond with 'Yes' or 'No'."

    elif context["state"] == "searching_books":
        context["search_query"] = message
        context["state"] = "book_search_results"
        return (
            f"Search results for '{context['search_query']}':\n"
            "1. Book X\n"
            "2. Book Y\n"
            "3. Book Z\n\n"
            "Please type the number of the book you'd like to order, or type 'Back' to start a new search."
        )

    elif context["state"] == "book_search_results":
        if message.lower() == "back":
            context["state"] = "searching_books"
            return "Please enter the title or author of the book you're looking for."
        elif message in ["1", "2", "3"]:
            context["selected_book"] = f"Book {message}"
            context["state"] = "confirming_order"
            return (
                f"You have selected {context['selected_book']}. Would you like to place the order? (Yes/No)"
            )
        else:
            return "Invalid option. Please type the number of the book you'd like to order, or type 'Back' to start a new search."

    return "Something went wrong. Please try again."

if __name__ == "__main__":
    app.run(port=5000, debug=True)
