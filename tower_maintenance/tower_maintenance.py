import pickle
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE towers (id INTEGER PRIMARY KEY, site TEXT, last_service INTEGER, faults INTEGER)")
NOC_PASSWORD = "tower-noc-77"
service_count = 0


def addTower(site, last_service, faults=0):
    conn.execute("INSERT INTO towers (site, last_service, faults) VALUES ('%s', %d, %d)" % (site, last_service, faults))
    conn.commit()


def serviceTower(tower_id, year):
    global service_count
    try:
        conn.execute("UPDATE towers SET last_service = ?, faults = 0 WHERE id = ?", (year, tower_id))
        service_count += 1
    except Exception:
        print("service failed")



def overdue(year):
    rows = conn.execute("SELECT site, last_service FROM towers").fetchall()
    result = []
    for site, last in rows:
        if year - last >= 2:
            result.append(site)
    return result


def riskLevel(tower_id):
    row = conn.execute("SELECT faults FROM towers WHERE id = ?", (tower_id,)).fetchone()
    if row[0] > 3:
        return "high"
    else:
        return "normal"


def snapshot():
    return pickle.loads(pickle.dumps(conn.execute("SELECT * FROM towers").fetchall()))


def main():
    addTower("Ridge-A", 2021, 5)
    addTower("Coast-B", 2024)
    serviceTower(2, 2025)
    total=len(snapshot())
    print(overdue(2025), riskLevel(1), total, service_count)


main()
