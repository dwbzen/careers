import unittest
import requests

class GameTests(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_create_user(self):
        api = "http://localhost:9000/user"
        player = {"email": "t@u.com", "initials": "111", "name": "unit-test-user"}
        response = requests.put(api, json=player)
        self.user_data = response.json()
        self.assertTrue(response.status_code == 200)        

        api = f"http://localhost:9000/user/{self.user_data['_id']}"
        response = requests.delete(api)
        self.assertTrue(response.status_code == 200)


    def test_create_game(self):
        api = "http://localhost:9000/user"
        player = {"email": "t@u.com", "initials": "111", "name": "unit-test-user"}
        response = requests.put(api, json=player)
        self.user_data = response.json()
    
        api = f"http://localhost:9000/game/{self.user_data['_id']}/200"
        game = {"name": "test_user", "initials": "bdb", "email": "abc123"}
        response = requests.put(api, json=game)
        self.assertTrue(response.status_code == 201)
