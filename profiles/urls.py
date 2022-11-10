from django.urls import path
from profiles import views

# ...........................users . urls
urlpatterns = [
    path('my-profile', views.myprofile, name='my-profile'),
    path('newaddr', views.newaddress, name='newaddr'),
    path('dlt_add/<int:id>', views.dltaddress, name='dlt_add'),
    path('password', views.password, name='password'),
    path('pass-update', views.passupdate, name='pass-update'),

]
