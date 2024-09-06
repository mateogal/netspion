import subprocess
import psycopg2


def main(resultsPath):
    DATABASE_NAME = "msf"
    DATABASE_USER = "msf"
    DATABASE_HOST = "127.0.0.1"
    DATABASE_PASSWORD = "+94gjzozqC1I99QmNyJVqzRb7JQsdC4LnN2FTHnp4fE="
    DATABASE_PORT = 5432

    conn = psycopg2.connect(
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
    )

    print("Running SQL Query")

    cur = conn.cursor()
    cur.execute(
        "SELECT r.name, v.name, h.address FROM hosts h, refs r, vulns v, vulns_refs vr WHERE vr.ref_id=r.id AND vr.vuln_id=v.id AND v.host_id=h.id"
    )
    rows = cur.fetchall()
    conn.commit()
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
