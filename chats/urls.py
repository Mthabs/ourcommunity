from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('add/', views.PostCreate.as_view(), name='post_add'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('<slug:slug>/like/', views.PostLike.as_view(), name='post_like'),
    path('<slug:slug>/edit/', views.PostEdit.as_view(), name='post_edit'),
    path('<slug:slug>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('<slug:post_slug>/comment/<int:comment_id>/edit/', views.CommentEdit.as_view(), name='comment_edit'),
    path('<slug:post_slug>/comment/<int:comment_id>/delete/', views.CommentDelete.as_view(), name='comment_delete'),
]