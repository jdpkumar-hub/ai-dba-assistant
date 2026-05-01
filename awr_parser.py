import re

# ================= METRICS EXTRACTION =================
def extract_metrics(text):
    metrics = {}

    cpu = re.search(r"DB CPU\s+(\d+\.\d+|\d+)", text)
    if cpu:
        metrics["cpu_pct"] = float(cpu.group(1))

    db_time = re.search(r"DB Time\s+(\d+\.\d+|\d+)", text)
    if db_time:
        metrics["db_time"] = float(db_time.group(1))

    hit = re.search(r"Buffer Cache Hit Ratio\s+(\d+\.\d+|\d+)", text)
    if hit:
        metrics["cache_hit"] = float(hit.group(1))

    waits = re.findall(r"(\w+\s+\w+)\s+(\d+\.\d+)%", text)
    metrics["top_waits"] = waits[:5]

    return metrics


# ================= STEP 2 =================
def classify_bottleneck(metrics):
    cpu = metrics.get("cpu_pct", 0)
    cache = metrics.get("cache_hit", 100)

    if cpu > 80:
        return "CPU Bottleneck"
    elif cache < 90:
        return "Memory Bottleneck"
    elif "db file sequential read" in str(metrics.get("top_waits", [])):
        return "I/O Bottleneck"
    else:
        return "Balanced / Unknown"


# ================= STEP 3 =================
def build_awr_prompt(metrics, bottleneck):
    return f"""
You are a senior Oracle DBA.

Analyze the following structured AWR metrics:

Metrics:
{metrics}

Detected Bottleneck:
{bottleneck}

Tasks:
1. Explain root cause clearly
2. Identify exact problem area
3. Provide specific tuning actions
4. Avoid generic advice

Be precise.
"""


# ================= STEP 5 =================
def calculate_health_score(metrics):
    score = 100

    if metrics.get("cpu_pct", 0) > 80:
        score -= 20
    if metrics.get("cache_hit", 100) < 90:
        score -= 20

    return score