from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminDashboardTests(TestCase):
	def setUp(self):
		from shopping.models import Register

		self.customer = Register.objects.create(
			name="Asha Patel",
			email="asha@example.com",
			password="customer-secret",
			mobile="9876543210",
		)

	def test_dashboard_redirects_anonymous_visitors_to_admin_login(self):
		response = self.client.get(reverse("admin_dashboard"))

		self.assertRedirects(
			response,
			f"{reverse('admin:login')}?next={reverse('admin_dashboard')}",
		)

	def test_staff_can_view_dashboard_without_customer_passwords(self):
		staff_user = get_user_model().objects.create_user(
			username="store-admin",
			password="staff-secret",
			is_staff=True,
		)
		self.client.force_login(staff_user)

		response = self.client.get(reverse("admin_dashboard"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Asha Patel")
		self.assertContains(response, "asha@example.com")
		self.assertContains(response, "Registered customers")
		self.assertNotContains(response, "customer-secret")
