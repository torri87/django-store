from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Product, User


class ProductApiTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Одяг')
        self.visible = Product.objects.create(
            category=self.category, name='Футболка', price=500, stock=11
        )
        self.hidden = Product.objects.create(
            category=self.category, name='Прихований', price=340, is_active=False
        )

    def test_list_returns_200(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hidden_product_not_in_list(self):
        response = self.client.get('/api/products/')
        names = [item['name'] for item in response.data]
        self.assertIn('Футболка', names)
        self.assertNotIn('Прихований', names)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_visible_and_hidden(self):
        response = self.client.get(f'/api/products/{self.visible.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/api/products/{self.hidden.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserRegisterApiTest(APITestCase):
    def setUp(self):
        self.data = {
            'username': 'double_mail',
            'email': 'email@mail.com',
            'password': 'Str0ng_Pas21swo..rd@!',
        }
        self.user = User.objects.create_user(**self.data)

    def test_register(self):
        data = {
            'username': 'new_user',
            'email': 'new_user@test.com',
            'password': 'Str0ng_Pas21swo..rd@!',
        }

        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 2)

        user = User.objects.get(username='new_user')
        self.assertEqual(user.username, 'new_user')

        self.assertNotIn('password', response.data)

    def test_register_double_mail(self):
        data = {
            'username': 'new_user2',
            'email': 'email@mail.com',
            'password': 'Str0ng_Pas21swo..rd@!!',
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = {
            'username': 'new_user2',
            'password': '123',
            'email': 'test@mail.com',
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileApiTest(APITestCase):
    def setUp(self):
        data = {
            'username': 'new_user',
            'email': 'new_user@test.com',
            'password': 'Str0ng_Pas21swo..rd@!',
        }
        self.user = User.objects.create_user(**data)

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'new_user')
        self.assertEqual(response.data['email'], 'new_user@test.com')

    def test_get_profile_not_authenticated(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)

        old_password_hashed = self.user.password
        update_data = {
            'username': 'update_username',
            'email': 'update_email@mail.com',
            'phone': '+380954127941',
            'password': 'new_hack_pass123!@#',
        }

        response = self.client.patch('/api/auth/me/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.username, 'new_user')
        self.assertEqual(self.user.email, 'update_email@mail.com')
        self.assertEqual(self.user.phone, '+380954127941')
        self.assertEqual(self.user.password, old_password_hashed)
        self.assertTrue(self.user.check_password('Str0ng_Pas21swo..rd@!'))


class UserLoginApiTest(APITestCase):
    def setUp(self):
        self.data = {
            'username': 'ivan',
            'password': 'Str0ng_Pas21swo..rd@!',
        }
        self.user = User.objects.create_user(**self.data)

    def test_login_returns_token(self):
        response = self.client.post('/api/auth/token/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        data = {
            'username': 'ivan',
            'password': '123',
        }
        response = self.client.post('/api/auth/token/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class OrderApiTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name="Laptop", price=1000.00, stock=10, category=self.category)
        self.product2 = Product.objects.create(name="Mouse", price=50.00, stock=5, category=self.category)
        self.product3 = Product.objects.create(name="Keyboard", price=75.00, stock=3, is_active=False, category=self.category)

        self.data = {
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 2}
            ]
        }

        self.data_user = {
            'username': 'new_user',
            'email': 'new_user@test.com',
            'password': 'Str0ng_Pas21swo..rd@!',
        }

        self.user = User.objects.create_user(**self.data_user)

    def test_order_not_authenticated(self):
        response = self.client.post('/api/orders/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_not_active(self):
        data = {
            'items': [
                {"product": self.product3.id, "quantity": 2},
            ]
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_not_enough_stock(self):
        data = {
            'items': [
                {"product": self.product1.id, "quantity": 11},
            ]
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_change_stock(self):
        data = {
            'items': [
                {'product': self.product1.id,
                'quantity': 2}
            ]
        }
        self.client.force_authenticate(user=self.user)
        before_stock = self.product1.stock
        response = self.client.post('/api/orders/', data, format='json')
        self.product1.refresh_from_db()
        after_stock = self.product1.stock
        self.assertNotEqual(after_stock, before_stock)