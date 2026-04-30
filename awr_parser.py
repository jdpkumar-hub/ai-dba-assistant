# awr_parser.py

from bs4 import BeautifulSoup


# ===============================
# PARSE HTML (if needed)
# ===============================
def parse_html(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()


# ===============================
# EXTRACT AWR SECTIONS
# ===============================
def extract_awr_sections(content):
    lines = content.split("\n")

    sections = {
        "load_profile": [],
        "wait_events": [],
        "top_sql": [],
        "io_stats": []
    }

    current = None

    for line in lines:

        if "Load Profile" in line:
            current = "load_profile"

        elif "Top 10 Foreground Events" in line:
            current = "wait_events"

        elif "SQL ordered by Elapsed Time" in line:
            current = "top_sql"

        elif "IOStat" in line or "Tablespace IO Stats" in line:
            current = "io_stats"

        if current:
            sections[current].append(line)

    # Limit size (important for token control)
    return {
        k: "\n".join(v[:80]) for k, v in sections.items()
    }


# ===============================
# BUILD AI INPUT
# ===============================
def build_awr_prompt(sections):
    return f"""
Analyze Oracle AWR Report.

LOAD PROFILE:
{sections['load_profile']}

WAIT EVENTS:
{sections['wait_events']}

TOP SQL:
{sections['top_sql']}

IO STATS:
{sections['io_stats']}

Provide:

1. Top Bottlenecks (ranked)
2. CPU vs IO diagnosis
3. Problematic SQL summary
4. Root Cause
5. Fix Steps (DBA actionable)
6. Risk if ignored
"""