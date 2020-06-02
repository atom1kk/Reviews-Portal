from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),  # post views  
    # path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'), 
    # Принимаем в качестве параметров год, месяц, день и тэг в виде целых числ "int" и букв+цифр+символы "post"  
    path('<int:post_id>/share/', views.post_share, name='post_share'),
]