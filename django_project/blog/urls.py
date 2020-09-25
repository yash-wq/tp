from django.urls import path
from .views import  PostListView,PostDetailView, PostCreateView, PostUpdateView, PostDeleteView
from . import views

urlpatterns = [
    path('welcome/', views.Welcome, name='blog-welcome'),
    path('project/', PostListView.as_view(), name='blog-home'),
    path('lead/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('/lead/test/', views.test, name='test'),
    path('about/', views.about, name='blog-about'),
    path('lead/', views.lead, name='blog-lead'),
    path('lead/tasks', views.lead_tasks, name='lead-tasks'),
    path('profile/', views.profile, name='blog-profile'),
    path('logout/', views.logoutUser, name='blog-logout'),
    path('resource/', views.resource, name='blog-resource'),
    path('login/', views.loginPage, name='blog-login'),
    path('', views.loginPage, name='blog-login'),
    path('register/', views.registerPage, name='blog-register'),
    path('manager/', views.manager, name='manager'),
]
