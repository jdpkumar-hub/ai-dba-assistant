# awr_parser.py

import re
from bs4 import BeautifulSoup


# ===============================
# HTML CLEANER
# ===============================
def parse_html(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()


# ===============================
# METRIC EXTRACTION
# ===============================
def extract_metrics(text):

    metrics = {
        "db_time": None,
        "db_cpu": None,
        "cpu_pct": None,
        "top_waits": [],
        "top_sql": []
    }

    # -------- DB Time / CPU --------
    for line in text.split("\n"):
        if "DB Time" in line:
            nums = re.findall(r"\d+\.\d+|\d+", line)
            if nums:
                metrics["db_time"] = float(nums[0])

        if "DB CPU" in line:
            nums = re.findall(r"\d+\.\d+|\d+", line)
            if nums:
                metrics["db_cpu"] = float(nums[0])

    # -------- CPU % --------
    if metrics["db_time"] and metrics["db_cpu"]:
        metrics["cpu_pct"] = round(
            (metrics["db_cpu"] / metrics["db_time"]) * 100, 2
        )

    # -------- WAIT EVENTS --------
    capture = False
    for line in text.split("\n"):

        if "Top 10 Foreground Events" in line:
            capture = True
            continue

        if capture:
            if line.strip() == "":
                break

            parts = line.split()
            if len(parts) > 3:
                metrics["top_waits"].append(line)

    # -------- TOP SQL --------
    capture = False
    for line in text.split("\n"):

        if "SQL ordered by Elapsed Time" in line:
            capture = True
            continue

        if capture:
            if line.strip() == "":
                break

            if len(line) > 30:
                metrics["top_sql"].append(line)

    return metrics


# ===============================
# BOTTLENECK DETECTION
# ===============================
def classify_bottleneck(metrics):

    if metrics["cpu_pct"] is None:
        return "UNKNOWN"

    if metrics["cpu_pct"] > 70:
        return "CPU_BOUND"

    # Check waits
    wait_text = " ".join(metrics["top_waits"]).lower()

    if "db file sequential read" in wait_text:
        return "IO_BOUND (Index Reads)"

    if "db file scattered read" in wait_text:
        return "IO_BOUND (Full Scan)"

    if "log file sync" in wait_text:
        return "COMMIT_BOTTLENECK"

    if "latch" in wait_text or "mutex" in wait_text:
        return "CONCURRENCY"

    return "MIXED"


# ===============================
# BUILD AI INPUT (SMART)
# ===============================
def build_awr_prompt(metrics):

    return f"""
Oracle AWR Analysis

DB Time: {metrics['db_time']}
DB CPU: {metrics['db_cpu']}
CPU Usage %: {metrics['cpu_pct']}

Top Wait Events:
{chr(10).join(metrics['top_waits'][:5])}

Top SQL:
{chr(10).join(metrics['top_sql'][:5])}

Tasks:

1. Identify primary bottleneck
2. Explain root cause using metrics
3. Provide DBA-level fixes
4. Highlight risks
5. Suggest tuning actions
"""