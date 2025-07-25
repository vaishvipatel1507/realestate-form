from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///realestate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define table structure
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    mobile = db.Column(db.String(10))
    location = db.Column(db.String(100))

# Route for form (insert record)
@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()
        mobile = request.form["mobile"].strip()
        location = request.form["location"].strip()

        # ✅ Server-side validations
        if not (first_name and last_name and email and mobile and location):
            error = "All fields are required."
        elif any(char.isdigit() for char in first_name):
            error = "First name should not contain numbers."
        elif any(char.isdigit() for char in last_name):
            error = "Last name should not contain numbers."
        elif not mobile.isdigit() or len(mobile) != 10:
            error = "Mobile number must be exactly 10 digits."
        elif '@' not in email or '.' not in email:
            error = "Invalid email format."
        else:
            contact = Contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                location=location
            )
            db.session.add(contact)
            db.session.commit()
            return redirect(url_for("show_data"))

    return render_template("form.html", error=error)


# Route to fetch and show all records
@app.route("/data", methods=["GET", "POST"])
def show_data():
    query = request.args.get("search")  # Get search term from URL
    if query:
        contacts = Contact.query.filter(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%")) |
            (Contact.location.ilike(f"%{query}%"))
        ).all()
    else:
        contacts = Contact.query.all()

    return render_template("data.html", contacts=contacts, search=query)


# Create the database the first time
if __name__ == "__main__":
    if not os.path.exists("realestate.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
