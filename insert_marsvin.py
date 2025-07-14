import sqlite3

# Forbind til databasen
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Liste over marsvin: navn, køn, fødselsdato
marsvin = [
    ("Thyria", "F", "2024-03-20"),
    ("Thorne", "M", "2024-03-20"),
    ("Nyx", "F", "2024-03-20"),
    ("Aegon", "M", "2023-12-01"),
    ("Luna", "F", "2023-11-15")
]

# Indsæt dem i databasen
cursor.executemany("INSERT INTO guinea_pig (name, gender, birth_date) VALUES (?, ?, ?)", marsvin)

conn.commit()
conn.close()

print("Marsvin tilføjet.")
