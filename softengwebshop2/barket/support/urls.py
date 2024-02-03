from django.urls import path
from . import views

app_name = "support"
urlpatterns = [
    path('create/', views.create_ticket, name='create_ticket'),
    path('ticket/', views.ticket_list, name='ticket'),
    path('respond/<int:ticket_id>/', views.respond_to_ticket, name='respond_to_ticket'),
    path('resolve/<int:ticket_id>/', views.resolve_ticket, name='resolve_ticket')

]