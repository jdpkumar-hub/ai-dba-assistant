# awr_pdf.py

import io
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# ===============================
# CHART GENERATOR
# ===============================
def create_cpu_chart(metrics):
    cpu = metrics.get("cpu_pct") or 0

    fig, ax = plt.subplots()
    ax.bar(["CPU Usage"], [cpu])
    ax.set_ylabel("Percentage")
    ax.set_title("CPU Usage Overview")

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png")
    plt.close(fig)
    img_buffer.seek(0)

    return img_buffer


# ===============================
# PDF GENERATOR
# ===============================
def generate_awr_pdf(result, metrics, score, level):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # ================= TITLE =================
    elements.append(Paragraph("AI DBA Assistant - AWR Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # ================= HEALTH BADGE =================
    color = colors.green
    if level == "Warning":
        color = colors.orange
    elif level == "Critical":
        color = colors.red

    health_table = Table([
        ["Health Score", f"{score} ({level})"]
    ])

    health_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(health_table)
    elements.append(Spacer(1, 12))

    # ================= METRICS TABLE =================
    metrics_data = [
        ["Metric", "Value"],
        ["DB Time", str(metrics.get("db_time"))],
        ["DB CPU", str(metrics.get("db_cpu"))],
        ["CPU %", str(metrics.get("cpu_pct"))],
    ]

    table = Table(metrics_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    elements.append(Paragraph("<b>Key Metrics</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # ================= CHART =================
    chart_buffer = create_cpu_chart(metrics)
    elements.append(Paragraph("<b>CPU Usage Chart</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Image(chart_buffer, width=400, height=200))
    elements.append(Spacer(1, 12))

    # ================= WAITS =================
    elements.append(Paragraph("<b>Top Wait Events</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    for wait in metrics.get("top_waits", [])[:5]:
        elements.append(Paragraph(wait, styles["Normal"]))

    elements.append(Spacer(1, 12))

    # ================= SQL =================
    elements.append(Paragraph("<b>Top SQL</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    for sql in metrics.get("top_sql", [])[:5]:
        elements.append(Paragraph(sql, styles["Normal"]))

    elements.append(Spacer(1, 12))

    # ================= AI RESULT =================
    elements.append(Paragraph("<b>AI Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    for line in result.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer