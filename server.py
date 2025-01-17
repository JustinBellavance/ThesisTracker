from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.io as pio
import os
from datetime import datetime
from docx import Document
import csv


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Path for CSV file to save data
CSV_FILE = "uploads_data.csv"

# Ensure the CSV file exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Upload Date", "Word Count"])


@app.route("/", methods=["GET", "POST"])
def index():
    plot_div = None

    if request.method == "POST":
        file = request.files["docx_file"]
        if file and file.filename.endswith(".docx"):
            # Read .docx file content directly
            doc = Document(file)
            text_content = "\n".join([para.text for para in doc.paragraphs])

            # Calculate word count
            word_count = len(text_content.split())

            # Save upload date and word count to CSV
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(CSV_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([upload_date, word_count])

            # Create a Plotly visualization
            labels = ["Word Count"]
            values = [word_count]
            fig = go.Figure(data=[go.Bar(x=labels, y=values)])

            # Convert Plotly figure to HTML
            plot_div = pio.to_html(fig, full_html=False)

    return render_template("index.html", plot_div=plot_div)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
