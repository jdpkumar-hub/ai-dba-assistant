# pdf_generator.py

import io
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt


# ===============================
# 📊 CHART GENERATOR
# ===============================
def generate_cpu_io_chart(metrics):
    cpu = metrics.get("cpu_pct") or 0
    io_val = 100 - cpu

    fig = plt.figure()
    plt.bar(["CPU", "IO"], [cpu, io_val])

    buffer = io.BytesIO()
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)

    return buffer


# ===============================
# 📄 PDF GENERATOR
# ===============================
def generate_awr_pdf(result, metrics, score, level):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph("AI DBA AWR Report", styles["Title"]))
    content.append(Spacer(1, 10))

    # Metrics
    content.append(Paragraph(f"CPU Usage: {metrics.get('cpu_pct')}%", styles["Normal"]))
    content.append(Paragraph(f"Health Score: {score} ({level})", styles["Normal"]))
    content.append(Spacer(1, 10))

    # Chart
    chart = generate_cpu_io_chart(metrics)
    content.append(Image(chart, width=400, height=200))
    content.append(Spacer(1, 20))

    # Analysis text
    for line in result.split("\n"):
        if line.strip():
            content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    buffer.seek(0)

    return buffer