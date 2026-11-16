from django.urls import path
from .views import HomeView, ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, ClientDeleteView, InteractionCreateView, InteractionUpdateView, InteractionDeleteView


app_name = 'crm'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/new/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:client_pk>/interactions/new/', InteractionCreateView.as_view(), name='interaction_create'),
    path('interactions/<int:pk>/edit/', InteractionUpdateView.as_view(), name='interaction_update'),
    path('interactions/<int:pk>/delete/', InteractionDeleteView.as_view(), name='interaction_delete'),
]