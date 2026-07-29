import os
import subprocess
import psycopg2


def main(resultsPath):
    database_name = os.environ.get("NETSPION_MSF_DB_NAME", "msf")
    database_user = os.environ.get("NETSPION_MSF_DB_USER", "msf")
    database_host = os.environ.get("NETSPION_MSF_DB_HOST", "127.0.0.1")
    database_password = os.environ.get("NETSPION_MSF_DB_PASSWORD")
    database_port = int(os.environ.get("NETSPION_MSF_DB_PORT", "5432"))

    conn = psycopg2.connect(
        database=database_name,
        user=database_user,
        password=database_password,
        host=database_host,
        port=database_port,
    )

    print("Running SQL Query")

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT r.name, v.name, h.address FROM hosts h, refs r, vulns v, "
                "vulns_refs vr WHERE vr.ref_id=r.id AND vr.vuln_id=v.id "
                "AND v.host_id=h.id"
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    tempstr = ""

    print("Generating internal CVE search string")

    for row in rows:
        tempcve = row[0].split("-")
        if tempcve[0] == "CVE":
            tempstr += " cve:" + row[0]

    print("Running msfconsole command")

    subprocess.run(
        [
            "msfconsole",
            "-q",
            "-x",
            "search" + tempstr + ";exit",
            "-o",
            resultsPath + "searchVulns.txt",
        ]
    )

    print("Done\n")
