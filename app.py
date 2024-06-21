from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:jokkachan77@localhost/prescriber'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'j4o4k4k4u'

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age= db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor_name = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    patient_name = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    qr_code = db.Column(db.LargeBinary)

    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))


# @app.route('/')
# def hello():
#     return 'Hello, World!'


@app.route('/', methods=['GET'])
def show_registration_options():
    return render_template('registration_options.html')

@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        # Extract data from the registration form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Create a new Doctor object with the extracted data
        new_doctor = Doctor(name=name, email=email, password=password)

        # Add the new doctor to the database session
        db.session.add(new_doctor)
        
        # Commit the session to save the changes to the database
        db.session.commit()

        return render_template('return_to_login.html')
    
    # If GET request, render registration form
    return render_template('register_doctor.html')

@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        # Extract data from the registration form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']

        # Create a new Patient object with the extracted data
        new_patient = Patient(name=name, email=email, password=password, age=age, gender=gender)

        # Add the new patient to the database session
        db.session.add(new_patient)
        
        # Commit the session to save the changes to the database
        db.session.commit()

        return render_template('return_to_login.html')
    
    # If GET request, render registration form
    return render_template('register_patient.html')

@app.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to find the doctor with the provided email
        doctor = Doctor.query.filter_by(email=email).first()

        # Inside the doctor login route
        if doctor and doctor.password == password:
            # Set doctor ID and name in session
            session['doctor_id'] = doctor.id
            session['doctor_name'] = doctor.name
            # Redirect to doctor dashboard
            return redirect(url_for('doctor_dashboard'))
        else:
            # Invalid credentials, show login form again with error message
            error_message = "Invalid email or password. Please try again."
            return render_template('login_doctor.html', error=error_message)

    # If GET request, render login form
    return render_template('login_doctor.html')

@app.route('/logout')
def logout():
    # Clear the doctor's ID from session upon logout
    session.pop('doctor_id', None)
    return redirect(url_for('login'))

@app.route('/doctor_dashboard')
def doctor_dashboard():
    # Check if doctor is logged in
    if 'doctor_id' not in session:
        return redirect(url_for('login_doctor'))  # Redirect to login page if not logged in

    # Get the logged-in doctor's ID from session
    doctor_id = session['doctor_id']

    # Query the database to get the logged-in doctor's information
    doctor = Doctor.query.get(doctor_id)

    # Query the database to get prescriptions associated with the logged-in doctor
    prescriptions = Prescription.query.filter_by(doctor_id=doctor_id).all()
    print(prescriptions)

    return render_template('doctor_dashboard.html', doctor=doctor, prescriptions=prescriptions)

# Define routes for registration, prescription management, etc.

from sqlalchemy.orm.exc import NoResultFound

@app.route('/create_prescription', methods=['POST'])
def create_prescription():
    # Retrieve the logged-in doctor's ID and name from the session
    doctor_id = session.get('doctor_id')
    doctor_name = session.get('doctor_name')

    # Retrieve other form fields
    patient_id = request.form['patient_id']
    details = request.form['details']

    try:
        # Query the database to get the patient's name based on the ID
        patient = Patient.query.filter_by(id=patient_id).one()
        patient_name = patient.name

        # Create a new prescription
        new_prescription = Prescription(
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            patient_id=patient_id,
            patient_name=patient_name,
            details=details
        )

        # Add the new prescription to the database session
        db.session.add(new_prescription)
        db.session.commit()

        return redirect(url_for('doctor_dashboard'))
    except NoResultFound:
        # Handle case where patient ID does not exist
        error_message = "Invalid patient ID. Please enter a valid patient ID."
        return render_template('error.html', error=error_message)


@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to find the patient with the provided email
        patient = Patient.query.filter_by(email=email).first()

        if patient and patient.password == password:
            # Patient is authenticated, redirect to patient dashboard
            session['patient_id'] = patient.id
            session['patient_name'] = patient.name
            # return render_template('', patient=patient)
            return redirect(url_for('patient_dashboard'))
        
        else:
            # Invalid credentials, show login form again with error message
            error_message = "Invalid email or password. Please try again."
            return render_template('login_patient.html', error=error_message)

    # If GET request, render patient login form
    return render_template('login_patient.html')


# @app.route('/patient_dashboard')
# def patient_dashboard():
#     # Check if patient is logged in
#     if 'patient_id' not in session:
#         return redirect(url_for('login'))  # Redirect to login page if not logged in

#     # Get the logged-in patient's ID from session
#     patient_id = session['patient_id']

#     # Query the database to get the logged-in patient's prescriptions
#     prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()

#     return render_template('patient_dashboard.html', prescriptions=prescriptions)


@app.route('/patient_dashboard')
def patient_dashboard():
    # Check if patient is logged in
    if 'patient_id' not in session:
        return redirect(url_for('login_patient'))  # Redirect to login page if not logged in

    # Get the logged-in patient's ID from session
    patient_id = session['patient_id']

    # Query the database to get the logged-in patient's information
    patient = Patient.query.get(patient_id)

    # Query the database to get prescriptions associated with the logged-in patient
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    print(prescriptions)

    return render_template('patient_dashboard.html', patient=patient, prescriptions=prescriptions)


if __name__ == '__main__':
    with app.app_context():
            db.create_all()
    app.run(debug=True)