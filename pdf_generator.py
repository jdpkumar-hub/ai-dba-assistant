import io
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt


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


def generate_awr_pdf(result, metrics, score, level):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # ===== TITLE =====
    content.append(Paragraph("AI DBA AWR REPORT", styles["Title"]))
    content.append(Spacer(1, 15))

    # ===== SUMMARY =====
    content.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    content.append(Spacer(1, 8))

    content.append(Paragraph(f"CPU Usage: {metrics.get('cpu_pct')}%", styles["Normal"]))
    content.append(Paragraph(f"Health Score: {score} ({level})", styles["Normal"]))
    content.append(Spacer(1, 15))

    # ===== CHART =====
    content.append(Paragraph("<b>CPU vs IO</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))

    chart = generate_cpu_io_chart(metrics)
    content.append(Image(chart, width=400, height=200))
    content.append(Spacer(1, 20))

    # ===== ANALYSIS =====
    content.append(Paragraph("<b>Analysis</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))

    for line in result.split("\n"):
        if line.strip():
            content.append(Paragraph(line, styles["Normal"]))
            content.append(Spacer(1, 6))

    doc.build(content)
    buffer.seek(0)

    return buffer