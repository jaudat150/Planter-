from django.urls import path
from . import views

urlpatterns = [
    path('',views.blogs,name='blogs'),
    path('post list/', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('like/<int:pk>/', views.like_post, name='like_post'),
    path('comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('new/', views.create_post, name='create_post'),
    path('delete_confirm/<int:id>/',views.del_confirm,name="del_confirm"),
    path('delete/<int:id>/',views.del_post,name="del_post"),
    path('comment/delete/<int:id>/', views.del_comment, name='del_comment'),
    path('edit_post/<int:id>/',views.edit_post,name="edit_post"),
    path('post/<int:pk>/report/', views.report_post, name='report_post'),
    path('comment/<int:comment_id>/report/', views.report_comment, name='report_comment'),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/', views.mark_all_read, name='mark_all_read'),

    path('reports/', views.view_reports, name='view_reports'),
    path('reports/send/<int:report_id>/', views.send_report, name='send_report'),
    path('reports/ignore/<int:report_id>/', views.ignore_report, name='ignore_report'),

    

]