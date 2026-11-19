from django.test import TestCase
from django.urls import reverse

from .models import Client, Company, Interaction, User


class ClientAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. Usuarios
        cls.rep1 = User.objects.create_user("rep1", password="test1234")
        cls.rep2 = User.objects.create_user("rep2", password="test1234")
        cls.manager = User.objects.create_user(
            "boss", password="test1234", is_manager=True
        )

        # 2. Empresa
        cls.company = Company.objects.create(name="Juguetes Test")

        # 3. Clientes (usan los usuarios y la empresa de arriba)
        cls.client_rep1 = Client.objects.create(
            first_name="Ana", last_name="López",
            email="ana@test.com", sales_rep=cls.rep1, company=cls.company,
        )
        cls.client_rep2 = Client.objects.create(
            first_name="Bruno", last_name="Gil",
            email="bruno@test.com", sales_rep=cls.rep2, company=cls.company,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("crm:client_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_sales_rep_only_sees_own_clients(self):
        self.client.force_login(self.rep1)
        response = self.client.get(reverse("crm:client_list"))
        self.assertContains(response, "ana@test.com")
        self.assertNotContains(response, "bruno@test.com")

    def test_sales_rep_gets_404_on_other_client(self):
        self.client.force_login(self.rep1)
        url = reverse("crm:client_detail", args=[self.client_rep2.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_sales_rep_cannot_delete_clients(self):
        self.client.force_login(self.rep1)
        url = reverse("crm:client_delete", args=[self.client_rep1.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Client.objects.filter(pk=self.client_rep1.pk).exists())

    def test_manager_sees_all_clients(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("crm:client_list"))
        self.assertContains(response, "ana@test.com")
        self.assertContains(response, "bruno@test.com")

    def test_new_client_is_assigned_to_sales_rep(self):
        self.client.force_login(self.rep1)
        self.client.post(
            reverse("crm:client_create"),
            {
                "first_name": "Carla",
                "last_name": "Ruiz",
                "email": "carla@test.com",
                "company": self.company.pk,
                "sales_rep": self.rep2.pk,
            },
        )
        new_client = Client.objects.get(email="carla@test.com")
        self.assertEqual(new_client.sales_rep, self.rep1)

    def test_search_filters_by_email(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("crm:client_list"), {"q": "bruno"})
        self.assertContains(response, "bruno@test.com")
        self.assertNotContains(response, "ana@test.com")

    def test_sales_rep_can_create_interaction_for_own_client(self):
        self.client.force_login(self.rep1)
        response = self.client.post(
            reverse("crm:interaction_create", args=[self.client_rep1.pk]),
            {
                "kind": Interaction.Kind.CALL,
                "date": "2026-11-19T10:00",
                "summary": "Llamada de seguimiento",
                "notes": "El cliente solicita una propuesta.",
            },
        )

        self.assertEqual(response.status_code, 302)
        interaction = Interaction.objects.get(summary="Llamada de seguimiento")
        self.assertEqual(interaction.client, self.client_rep1)
        self.assertEqual(interaction.user, self.rep1)

    def test_sales_rep_can_edit_interaction_of_own_client(self):
        interaction = Interaction.objects.create(
            client=self.client_rep1,
            user=self.manager,
            kind=Interaction.Kind.EMAIL,
            summary="Primer correo",
        )
        self.client.force_login(self.rep1)
        response = self.client.post(
            reverse("crm:interaction_update", args=[interaction.pk]),
            {
                "kind": Interaction.Kind.EMAIL,
                "date": "2026-11-19T11:00",
                "summary": "Correo actualizado",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        interaction.refresh_from_db()
        self.assertEqual(interaction.summary, "Correo actualizado")

    def test_sales_rep_cannot_delete_interaction(self):
        interaction = Interaction.objects.create(
            client=self.client_rep1,
            user=self.rep1,
            kind=Interaction.Kind.MEETING,
            summary="Reunión pendiente",
        )
        self.client.force_login(self.rep1)
        response = self.client.post(
            reverse("crm:interaction_delete", args=[interaction.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Interaction.objects.filter(pk=interaction.pk).exists())

        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("crm:interaction_delete", args=[interaction.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())
