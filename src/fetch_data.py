import requests
import psycopg2

def fetch_data_from_api(url):
    """
    Fetch data from the given URL and return the JSON response
    """
    data = []
    while url is not None:
        response = requests.get(url)
        response_json = response.json()
        if "result" in response_json:
            data.extend(response_json.get("result"))
            url = None
        elif "results" in response_json:
            data.extend(response_json.get("results"))
            url = response_json.get("next")
    print("Length of data:", len(data))
    return data


def fetch_people_details(raw_data):
    detailed_data = []

    for item in raw_data:
        url = item.get("url")
        response = requests.get(url)
        response_json = response.json()
        detailed_data.append(response_json.get("result"))

    return detailed_data


def save_people_data_to_db(people_data):
    """
    Save the fetched data to the specified PostgreSQL table
    """
    conn = psycopg2.connect(
        dbname="nerd_facts_db",
        user="nerd_user",
        password="nerd_password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS people (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        gender VARCHAR(50),
        height VARCHAR(50)
        )
    """)

    for person in people_data:
        properties = person.get("properties")
        cur.execute("""
            INSERT INTO people (name, gender, height)
            VALUES (%s, %s, %s)
        """,
        (properties.get("name"), properties.get("gender"), properties.get("height"))
        )
    
    conn.commit()
    cur.close()
    conn.close()

## TA BORT SEN
def print_people_from_db():
    conn = psycopg2.connect(
        dbname="nerd_facts_db",
        user="nerd_user",
        password="nerd_password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM people LIMIT 10;")  # ändra LIMIT om du vill se fler
    rows = cur.fetchall()
    
    for row in rows:
        print(row)
    
    cur.close()
    conn.close()





def main():
    url_people = "https://swapi.tech/api/people/"
    url_films = "https://swapi.tech/api/films/"
    raw_people_data = fetch_data_from_api(url_people)
    people_data = fetch_people_details(raw_people_data)
    films_data = fetch_data_from_api(url_films)

    print("EX people data:", people_data[0])
    print("EX films data:", films_data[0])
    save_people_data_to_db(people_data)
    print_people_from_db()

if __name__ == "__main__":
    main()