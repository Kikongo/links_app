from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_and_use_short_link(self):
        original_url = "https://example.com"
        response = self.client.post("/link/links/shorten", json={"original_url": original_url})
        if response.status_code == 200:
            short_code = response.json()["short_url"].split("/")[-1]
            self.client.get(f"/link/{short_code}")
