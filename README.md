# Book Haven WhatsApp Bot

## Overview

Book Haven is an online bookstore that allows customers to browse and order books directly via WhatsApp. This chatbot, built with Flask, offers a simple interface for users to explore different book categories, search for specific titles, and place orders. The bot manages user sessions to provide a personalized and seamless shopping experience.

## Features

- **Browsing Categories**: Users can browse different book categories.
- **Searching for Books**: Users can search for specific books by title or author.
- **Placing Orders**: Users can select books and confirm their orders.
- **Session Management**: The bot maintains the context of each user's session and handles timeouts due to inactivity.

## Prerequisites

- Python 3.7+
- Flask
- Flask-JSONIFY
- Python-dotenv
- A WhatsApp API service for sending messages (e.g., Twilio)

## Project Structure

```plaintext
.
├── app.py                   # Main application file
├── helperfunction
│   └── waSendMessage.py     # Helper function for sending WhatsApp messages
├── .env                     # Environment variables
└── README.md                # Project documentation
```

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/book-haven-whatsapp-bot.git
cd book-haven-whatsapp-bot
```
### 2. Install Dependencies
Make sure you have Python installed. Then, install the necessary Python packages:

```bash
pip install flask python-dotenv
```

### 3. Environment Variables
Create a .env file in the root directory and add the following environment variables:
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### 4. Run the Application
Start the Flask server:
```bash
python app.py
```
The application will be running on `http://localhost:5000`

## API Endpoints
`/`
- Method: GET
- Description: Returns a welcome message.

`/whatsapp`
- Method: POST
- Description: Main endpoint for receiving WhatsApp messages. It processes the messages and responds based on the current state of the conversation.



