from django.urls import include,path
from . import views
urlpatterns=[
    path("",views.home,name='home'),
    path("upload/",views.upload,name='upload'),
    path("result/",views.result,name='result'),
    path("show_all/",views.show_all,name='show_all'),
    path("trivia/",views.trivia,name='trivia'),
    path('move-image/<int:id>/', views.move_image, name='move_image'),

    path('quiz/', views.run_quiz, name='run_quiz'),
    path('quiz_home/', views.quiz_home, name='quiz_home'),
    path('quiz/results/', views.process_quiz, name='process_quiz'),
    ]