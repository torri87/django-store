from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Product


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