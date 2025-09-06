from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
MONGO_URI = "mongodb+srv://user:user@cluster0.u3fdtma.mongodb.net/mn"
client = MongoClient(MONGO_URI)
db = client["mn"]  # database name
patients_col = db["patients"]
reports_col = db["reports"]


# --- Utilities: Convert MongoDB docs into dicts with string ids ---
def serialize_patient(patient):
    return {
        "id": str(patient["_id"]),
        "name": patient.get("name"),
        "age": patient.get("age"),
        "phone": patient.get("phone"),
    }


def serialize_report(report):
    return {
        "id": str(report["_id"]),
        "patient_id": report.get("patient_id", ""),  # ensure always string
        "title": report.get("title"),
        "report_text": report.get("report_text"),
    }


# --- Routes ---
@app.route("/")
def index():
    reports = [serialize_report(r) for r in reports_col.find()]
    patients = {str(p["_id"]): serialize_patient(p) for p in patients_col.find()}
    return render_template("index.html", reports=reports, patients=patients)


@app.route("/reports")
def reports():
    reports = [serialize_report(r) for r in reports_col.find()]
    patients = {str(p["_id"]): serialize_patient(p) for p in patients_col.find()}
    return render_template("reports.html", reports=reports, patients=patients)


@app.route("/report/<report_id>")
def report_detail(report_id):
    report = reports_col.find_one({"_id": ObjectId(report_id)})
    if not report:
        return "Report not found", 404

    patient = None
    if report.get("patient_id"):
        patient = patients_col.find_one({"_id": ObjectId(report["patient_id"])})
    return render_template(
        "report_detail.html",
        report=serialize_report(report),
        patient=serialize_patient(patient) if patient else None,
    )


@app.route("/patient/<patient_id>")
def patient_profile(patient_id):
    patient = patients_col.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        return "Patient not found", 404

    reports = [
        serialize_report(r) for r in reports_col.find({"patient_id": patient_id})
    ]
    return render_template(
        "patient_profile.html", patient=serialize_patient(patient), reports=reports
    )


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        phone = request.form["phone"]
        patients_col.insert_one({"name": name, "age": age, "phone": phone})
        return redirect(url_for("index"))
    return render_template("add_patient.html")


@app.route("/add_report", methods=["GET", "POST"])
def add_report():
    patients = [serialize_patient(p) for p in patients_col.find()]
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        if not patient_id:  # prevent empty selection
            return "You must select a patient", 400

        title = request.form["title"]
        report_text = request.form["report_text"]

        reports_col.insert_one(
            {
                "patient_id": patient_id,  # stored as string
                "title": title,
                "report_text": report_text,
            }
        )
        return redirect(url_for("index"))
    return render_template("add_report.html", patients=patients)


if __name__ == "__main__":
    app.run(debug=True)
