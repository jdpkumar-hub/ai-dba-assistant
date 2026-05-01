import re

# ================= PARSE HTML =================
def parse_html(content):
    return content


# ================= METRICS =================
def extract_metrics(content):
    metrics = {}

    try:
        db_time = re.search(r"DB Time.*?(\d+)", content)
        cpu_time = re.search(r"DB CPU.*?(\d+)", content)

        metrics["db_time"] = int(db_time.group(1)) if db_time else 0
        metrics["cpu_time"] = int(cpu_time.group(1)) if cpu_time else 0

    except Exception:
        metrics["db_time"] = 0
        metrics["cpu_time"] = 0

    return metrics


# ================= BOTTLENECK =================
def classify_bottleneck(metrics):
    try:
        if metrics["cpu_time"] > metrics["db_time"] * 0.7:
            return "CPU Bottleneck"
        else:
            return "IO Bottleneck"
    except Exception:
        return "Unknown"


# ================= PROMPT =================
def build_awr_prompt(metrics, bottleneck):
    return f"""
Analyze Oracle AWR Report.

Metrics:
{metrics}

Detected Bottleneck: {bottleneck}

Give tuning recommendations.
"""


# ================= HEALTH =================
def calculate_health_score(metrics):
    try:
        score = 100

        if metrics["cpu_time"] > metrics["db_time"] * 0.8:
            score -= 30

        return max(score, 0)
    except Exception:
        return 50