# helper_function.py
def login_mechanic(client, email, password):
    credentials = {"email": email, "password": password}
    response = client.post("/mechanics/login", json=credentials)
    assert response.status_code == 200
    return response.get_json()["auth_token"]


def login_customer(client, email, password):
    credentials = {"email": email, "password": password}
    response = client.post("/customers/login", json=credentials)
    assert response.status_code == 200
    return response.get_json()["auth_token"]
