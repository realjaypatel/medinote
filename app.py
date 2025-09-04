import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

PATIENTS_FILE = "patients.json"
REPORTS_FILE = "reports.json"

# Utility functions
def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    reports = load_data(REPORTS_FILE)
    patients = {p["id"]: p for p in load_data(PATIENTS_FILE)}
    return render_template("index.html", reports=reports, patients=patients)

@app.route("/reports")
def reports():
    reports = load_data(REPORTS_FILE)
    patients = {p["id"]: p for p in load_data(PATIENTS_FILE)}
    return render_template("reports.html", reports=reports, patients=patients)

@app.route("/report/<int:report_id>")
def report_detail(report_id):
    reports = load_data(REPORTS_FILE)
    patients = {p["id"]: p for p in load_data(PATIENTS_FILE)}
    report = next((r for r in reports if r["id"] == report_id), None)
    if not report:
        return "Report not found", 404
    patient = patients.get(report["patient_id"])
    return render_template("report_detail.html", report=report, patient=patient)

@app.route("/patient/<int:patient_id>")
def patient_profile(patient_id):
    patients = load_data(PATIENTS_FILE)
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return "Patient not found", 404
    reports = [r for r in load_data(REPORTS_FILE) if r["patient_id"] == patient_id]
    return render_template("patient_profile.html", patient=patient, reports=reports)

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        patients = load_data(PATIENTS_FILE)
        new_id = len(patients) + 1
        name = request.form["name"]
        age = request.form["age"]
        phone = request.form["phone"]
        patients.append({"id": new_id, "name": name, "age": age, "phone": phone})
        save_data(PATIENTS_FILE, patients)
        return redirect(url_for("index"))
    return render_template("add_patient.html")

@app.route("/add_report", methods=["GET", "POST"])
def add_report():
    patients = load_data(PATIENTS_FILE)
    if request.method == "POST":
        reports = load_data(REPORTS_FILE)
        new_id = len(reports) + 1
        patient_id = int(request.form["patient_id"])
        title = request.form["title"]
        report_text = request.form["report_text"]
        reports.append({
            "id": new_id,
            "patient_id": patient_id,
            "title": title,
            "report_text": report_text
        })
        save_data(REPORTS_FILE, reports)
        return redirect(url_for("index"))
    return render_template("add_report.html", patients=patients)

if __name__ == "__main__":
    for file in [PATIENTS_FILE, REPORTS_FILE]:
        if not os.path.exists(file):
            save_data(file, [])
    app.run(debug=True)
