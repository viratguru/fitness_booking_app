from flask import Flask, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
import logging
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

IST = ZoneInfo("Asia/Kolkata")

# In-memory databases
classes_db = []
bookings_db = []

# Sample data
classes_db.extend([
    {
        "id": str(uuid.uuid4()),
        "name": "Yoga",
        "datetime": datetime(2025, 6, 21, 7, 0, tzinfo=IST),
        "instructor": "Alice",
        "total_slots": 10,
        "available_slots": 10
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Zumba",
        "datetime": datetime(2025, 6, 21, 9, 0, tzinfo=IST),
        "instructor": "Bob",
        "total_slots": 15,
        "available_slots": 15
    },
    {
        "id": str(uuid.uuid4()),
        "name": "HIIT",
        "datetime": datetime(2025, 6, 21, 18, 0, tzinfo=IST),
        "instructor": "Charlie",
        "total_slots": 12,
        "available_slots": 12
    }
])

# GET /classes
@app.route('/classes', methods=['GET'])
def get_classes():
    timezone = request.args.get('timezone', 'Asia/Kolkata')
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        return jsonify({"error": "Invalid timezone"}), 400

    result = []
    for cls in classes_db:
        result.append({
            "id": cls["id"],
            "name": cls["name"],
            "datetime": cls["datetime"].astimezone(tz).isoformat(),
            "instructor": cls["instructor"],
            "available_slots": cls["available_slots"]
        })
    return jsonify(result), 200

# POST /book
@app.route('/book', methods=['POST'])
def book_class():
    data = request.get_json()
    class_id = data.get("class_id")
    client_name = data.get("client_name")
    client_email = data.get("client_email")

    if not class_id or not client_name or not client_email:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        validate_email(client_email)
    except EmailNotValidError:
        return jsonify({"error": "Invalid email address"}), 400

    cls = next((c for c in classes_db if c["id"] == class_id), None)
    if not cls:
        return jsonify({"error": "Class not found"}), 404

    if cls["available_slots"] <= 0:
        return jsonify({"error": "No slots available"}), 400

    cls["available_slots"] -= 1
    booking = {
        "id": str(uuid.uuid4()),
        "class_id": class_id,
        "client_name": client_name,
        "client_email": client_email,
        "booked_at": datetime.now(IST).isoformat()
    }
    bookings_db.append(booking)
    logging.info(f"Booking successful: {booking}")
    return jsonify(booking), 201

# GET /bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({"error": "Invalid email"}), 400

    user_bookings = [b for b in bookings_db if b["client_email"] == email]
    return jsonify(user_bookings), 200

if __name__ == '__main__':
    app.run(debug=True)
