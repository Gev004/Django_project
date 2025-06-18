from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from shopapp.models import Order, Product

class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

        self.product = Product.objects.create(
            name="Test Product",
            price=100,
            created_by=self.user
        )

        self.order = Order.objects.create(
            user=self.user,
            promocode="DISCOUNT10",
            delivery_address="123 Main Street"
        )
        self.order.products.add(self.product)

    def tearDown(self):
        self.order.delete()
        self.product.delete()

    def test_order_details(self):
        url = reverse('shopapp:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123 Main Street")
        self.assertContains(response, "DISCOUNT10")

        context_order = response.context['order']
        self.assertEqual(context_order.pk, self.order.pk)

class OrdersExportTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = User.objects.create_user(
            username='staffuser',
            password='pass1234',
            is_staff=True
        )
        cls.normal_user = User.objects.create_user(
            username='normaluser',
            password='pass1234',
            is_staff=False
        )

    @classmethod
    def tearDownClass(cls):
        cls.staff_user.delete()
        cls.normal_user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username='staffuser', password='pass1234')

        self.product1 = Product.objects.create(name="Product 1", price=10, created_by=self.staff_user)
        self.product2 = Product.objects.create(name="Product 2", price=20, created_by=self.staff_user)

        self.order1 = Order.objects.create(
            user=self.staff_user,
            delivery_address="Address 1",
            promocode="PROMO1"
        )
        self.order1.products.add(self.product1, self.product2)

        self.order2 = Order.objects.create(
            user=self.normal_user,
            delivery_address="Address 2",
            promocode="PROMO2"
        )
        self.order2.products.add(self.product2)

    def tearDown(self):
        self.order1.delete()
        self.order2.delete()
        self.product1.delete()
        self.product2.delete()

    def test_orders_export_accessible_for_staff(self):
        url = reverse('shopapp:orders_export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()

        self.assertIn("orders", json_data)
        self.assertEqual(len(json_data["orders"]), 2)

        order_ids = [order["id"] for order in json_data["orders"]]
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)

        order1_data = next(o for o in json_data["orders"] if o["id"] == self.order1.id)
        self.assertEqual(order1_data["delivery_address"], "Address 1")
        self.assertEqual(order1_data["promocode"], "PROMO1")
        self.assertEqual(order1_data["user_id"], self.staff_user.id)
        self.assertCountEqual(order1_data["product_ids"], [self.product1.id, self.product2.id])

    def test_orders_export_forbidden_for_non_staff(self):
        self.client.logout()
        self.client.login(username='normaluser', password='pass1234')
        url = reverse('shopapp:orders_export')
        try:
            print(url)
        except NoReverseMatch as e:
            print(e)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


