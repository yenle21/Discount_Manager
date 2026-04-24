from locust import HttpUser, task, wait_time, between

class Myuser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def get_courses(self):
        self.client.get('/courses/')

    @task(1)
    def get_lessons(self):
        self.client.get('/courses/1/lessons/')