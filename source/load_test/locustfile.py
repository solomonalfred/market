import random
from locust import HttpUser, task, between


class APIUser(HttpUser):
    wait_time = between(1, 2)
    token = None
    admin_token = None
    user_login = ""
    items = {"item1": 1,
             "item2": 2,
             "item3": 3}
    user_number = 10

    def on_start(self):
        response = self.client.post("/api/auth", data={
            "username": "admin",
            "password": "123456"
        })
        if response.status_code == 200:
            self.admin_token = response.json().get("access_token")
        else:
            print("Не удалось получить токен авторизации!")

        item_name = list(self.items.keys())
        item = {item_name[0], self.items[item_name[0]]}
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.client.post("/api/addMerch", json=item, headers=headers)

        item = {item_name[1], self.items[item_name[1]]}
        self.client.post("/api/addMerch", json=item, headers=headers)

        item = {item_name[2], self.items[item_name[2]]}
        self.client.post("/api/addMerch", json=item, headers=headers)

        random_part = random.randint(1, self.user_number)
        self.user_login = f"testuser{random_part}"
        payload = {
            "login": self.user_login,
            "password": "password123",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        self.client.post("/api/signup", json=payload)

        update_user = {
            "login": self.user_login,
            "coin_amount": random.randint(1, self.user_number * 5)
        }

        self.client.post("/api/addMerch", json=update_user, headers=headers)


    @task(2)
    def ping(self):
        self.client.get("/ping")

    @task(1)
    def signup(self):
        response = self.client.post("/api/auth", data={
            "username": self.user_login,
            "password": "password123"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            print("Не удалось получить токен авторизации!")

    @task(1)
    def info(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/info", headers=headers)

    @task(3)
    def send_coin(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/sendCoin", json = {
            "toUser": f"testuser{random.randint(1, self.user_number)}",
            "amount": random.randint(1, self.user_number)
        }, headers=headers)

    @task(10)
    def buy(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        item = random.choice(list(self.items.keys()))
        response = self.client.get(f"/api/buy/{item}", params={
            "item": item
        }, headers=headers)
