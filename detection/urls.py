from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update', views.update_room, name='update'),
    path('detail/<int:room_id>/', views.detail, name='detail'),
    path('', include('django.contrib.auth.urls')),    
]