from django.urls import path
from.import views
app_name='category'

urlpatterns = [
    path('category',views.category_management,name='category_management'),
    path('create/',views.newcategory,name='new_category'),
    path('edit/<int:category_id>/', views.edit_category, name='edit-category'),
    path('delete/<int:category_id>/',views.category_is_available,name='available-category'),
]
