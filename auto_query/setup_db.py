# setup_db.py
import sqlite3

conn = sqlite3.connect("tableau_sim.db")
cur = conn.cursor()

# Drop old tables if exist
cur.execute("DROP TABLE IF EXISTS Orders")
cur.execute("DROP TABLE IF EXISTS Customers")

# Create Customers table
cur.execute("""
CREATE TABLE Customers (
    ID INTEGER PRIMARY KEY,
    CustomerName TEXT,
    Country TEXT
)
""")

# Create Orders table
cur.execute("""
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    Amount REAL,
    Region TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(ID)
)
""")

# Insert sample data
cur.executemany("INSERT INTO Customers (ID, CustomerName, Country) VALUES (?, ?, ?)", [
    (1, 'Alice', 'USA'),
    (2, 'Bob', 'UK'),
    (3, 'Charlie', 'India'),
])

cur.executemany("INSERT INTO Orders (OrderID, CustomerID, Amount, Region) VALUES (?, ?, ?, ?)", [
    (101, 1, 250.0, 'North'),
    (102, 2, 450.5, 'South'),
    (103, 1, 300.0, 'North'),
    (104, 3, 500.0, 'West'),
])

conn.commit()
conn.close()
