import os
import sys
import tempfile

# Use a throw-away database file so tests never touch real data
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

# Let the tests find app.py in the project folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import app, get_db, init_db


@pytest.fixture
def client():
    """A fresh, empty app for every test."""
    app.config["TESTING"] = True
    init_db()
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM employees")
        db.commit()
    with app.test_client() as test_client:
        yield test_client


def add_person(client, name="Asha", email="asha@example.com",
               department="Design", role="Designer"):
    return client.post(
        "/add",
        data={"name": name, "email": email, "department": department, "role": role},
        follow_redirects=True,
    )


def first_id():
    with app.app_context():
        return get_db().execute("SELECT id FROM employees").fetchone()["id"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_page_shows_empty_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"It's quiet in here" in response.data


def test_add_employee(client):
    response = add_person(client)
    assert response.status_code == 200
    assert b"Asha" in response.data
    assert b"asha@example.com" in response.data


def test_add_rejects_empty_name(client):
    response = add_person(client, name="")
    assert b"Please enter a name." in response.data


def test_add_rejects_bad_email(client):
    response = add_person(client, email="not-an-email")
    assert b"Please enter a valid email." in response.data


def test_add_rejects_unknown_department(client):
    response = add_person(client, department="Wizardry")
    assert b"Please pick a department." in response.data


def test_edit_employee(client):
    add_person(client)
    response = client.post(
        f"/edit/{first_id()}",
        data={"name": "Asha", "email": "asha@example.com",
              "department": "Design", "role": "Senior Designer"},
        follow_redirects=True,
    )
    assert b"Senior Designer" in response.data


def test_edit_missing_employee_gives_404(client):
    assert client.get("/edit/9999").status_code == 404


def test_delete_employee(client):
    add_person(client)
    response = client.post(f"/delete/{first_id()}", follow_redirects=True)
    assert b"It's quiet in here" in response.data


def test_search_finds_the_right_person(client):
    add_person(client, name="Asha", department="Design")
    add_person(client, name="Ravi", email="ravi@example.com",
               department="Finance", role="Accountant")
    response = client.get("/?q=Design")
    assert b"Asha" in response.data
    assert b"Ravi" not in response.data
