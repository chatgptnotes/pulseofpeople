"""
Locust Load Testing Configuration
Performance and load testing for Pulse of People API

Run with: locust -f locustfile.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class AuthenticatedUser(SequentialTaskSet):
    """Sequence of tasks for an authenticated user"""

    def on_start(self):
        """Login before starting tasks"""
        # Login to get JWT token
        response = self.client.post('/api/auth/login/', json={
            'email': f'user{random.randint(1, 100)}@example.com',
            'password': 'testpass123'
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(1)
    def view_dashboard(self):
        """View dashboard analytics"""
        self.client.get('/api/analytics/dashboard/')

    @task(3)
    def list_feedback(self):
        """List direct feedback"""
        self.client.get('/api/feedback/')

    @task(2)
    def search_feedback(self):
        """Search feedback by ward"""
        self.client.get(f'/api/feedback/?ward=Ward{random.randint(1, 10)}')

    @task(1)
    def view_sentiment_analytics(self):
        """View sentiment analytics"""
        self.client.get('/api/analytics/sentiment/')

    @task(1)
    def view_field_reports(self):
        """View field reports"""
        self.client.get('/api/field-reports/')


class AdminUser(SequentialTaskSet):
    """Sequence of tasks for admin users"""

    def on_start(self):
        """Login as admin"""
        response = self.client.post('/api/auth/login/', json={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(2)
    def list_users(self):
        """List all users"""
        self.client.get('/api/admin/users/')

    @task(1)
    def view_user(self):
        """View single user"""
        user_id = random.randint(1, 100)
        self.client.get(f'/api/admin/users/{user_id}/')

    @task(1)
    def view_analytics(self):
        """View admin analytics"""
        self.client.get('/api/admin/analytics/')

    @task(1)
    def view_audit_logs(self):
        """View audit logs"""
        self.client.get('/api/admin/audit-logs/')


class PulseOfPeopleUser(HttpUser):
    """
    Simulated user for load testing
    Mix of regular users and admins
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    # 80% regular users, 20% admins
    tasks = {
        AuthenticatedUser: 8,
        AdminUser: 2
    }


class AnonymousUser(HttpUser):
    """Unauthenticated user (for public endpoints)"""
    wait_time = between(2, 5)

    @task(5)
    def view_homepage(self):
        """View homepage/API root"""
        self.client.get('/api/')

    @task(1)
    def attempt_login(self):
        """Attempt to login"""
        self.client.post('/api/auth/login/', json={
            'email': f'user{random.randint(1, 1000)}@example.com',
            'password': 'somepassword'
        })


class BulkOperationUser(HttpUser):
    """User performing bulk operations"""
    wait_time = between(5, 10)

    def on_start(self):
        """Login"""
        response = self.client.post('/api/auth/login/', json={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })

        if response.status_code == 200:
            data = response.json()
            token = data.get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {token}'})

    @task(1)
    def bulk_feedback_create(self):
        """Simulate bulk feedback creation"""
        feedback_items = []

        for i in range(10):
            feedback_items.append({
                'citizen_name': f'Citizen {i}',
                'citizen_age': random.randint(18, 80),
                'ward': f'Ward {random.randint(1, 20)}',
                'message_text': f'This is test feedback number {i}',
                'issue_category_id': random.randint(1, 5)
            })

        self.client.post('/api/feedback/bulk-create/', json={
            'items': feedback_items
        })

    @task(1)
    def export_data(self):
        """Export analytics data"""
        self.client.get('/api/analytics/export/?format=csv')


class SearchUser(HttpUser):
    """User performing searches"""
    wait_time = between(0.5, 2)

    def on_start(self):
        """Login"""
        response = self.client.post('/api/auth/login/', json={
            'email': f'user{random.randint(1, 50)}@example.com',
            'password': 'testpass123'
        })

        if response.status_code == 200:
            data = response.json()
            token = data.get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {token}'})

    @task(5)
    def search_feedback(self):
        """Search feedback"""
        search_terms = ['education', 'health', 'water', 'electricity', 'roads']
        term = random.choice(search_terms)
        self.client.get(f'/api/feedback/?search={term}')

    @task(3)
    def filter_by_ward(self):
        """Filter by ward"""
        ward = f'Ward {random.randint(1, 20)}'
        self.client.get(f'/api/feedback/?ward={ward}')

    @task(2)
    def filter_by_sentiment(self):
        """Filter by sentiment"""
        sentiments = ['positive', 'negative', 'neutral']
        sentiment = random.choice(sentiments)
        self.client.get(f'/api/sentiment/?polarity={sentiment}')


# Custom load test scenarios

class StressTest(HttpUser):
    """
    Stress test scenario - High load
    Run with: locust -f locustfile.py --users 1000 --spawn-rate 50 StressTest
    """
    wait_time = between(0.1, 0.5)  # Very short wait time

    def on_start(self):
        response = self.client.post('/api/auth/login/', json={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })
        if response.status_code == 200:
            token = response.json().get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {token}'})

    @task(10)
    def rapid_api_calls(self):
        """Rapid API calls"""
        self.client.get('/api/feedback/')

    @task(5)
    def rapid_analytics(self):
        """Rapid analytics requests"""
        self.client.get('/api/analytics/dashboard/')


class SpikeTest(HttpUser):
    """
    Spike test scenario - Sudden burst of traffic
    Run with: locust -f locustfile.py --users 500 --spawn-rate 100 SpikeTest
    """
    wait_time = between(0, 1)

    @task
    def burst_requests(self):
        """Burst of requests"""
        self.client.get('/api/')
        self.client.get('/api/feedback/')
        self.client.get('/api/analytics/dashboard/')


class EnduranceTest(HttpUser):
    """
    Endurance test scenario - Sustained load over time
    Run with: locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 1h EnduranceTest
    """
    wait_time = between(2, 5)

    def on_start(self):
        response = self.client.post('/api/auth/login/', json={
            'email': f'user{random.randint(1, 100)}@example.com',
            'password': 'testpass123'
        })
        if response.status_code == 200:
            token = response.json().get('access', '')
            self.client.headers.update({'Authorization': f'Bearer {token}'})

    @task(5)
    def normal_usage(self):
        """Simulate normal usage patterns"""
        self.client.get('/api/feedback/')

    @task(3)
    def view_analytics(self):
        """View analytics"""
        self.client.get('/api/analytics/dashboard/')

    @task(2)
    def search(self):
        """Perform searches"""
        self.client.get(f'/api/feedback/?search=test')

    @task(1)
    def create_feedback(self):
        """Create feedback"""
        self.client.post('/api/feedback/', json={
            'citizen_name': 'Test Citizen',
            'citizen_age': 30,
            'ward': 'Ward 1',
            'message_text': 'Test feedback message',
            'issue_category_id': 1
        })
