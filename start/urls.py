from django.contrib import admin
from django.urls import path
from start import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('auth/',views.auth,name="auth"),
    path("mri/",views.report_check,name="mri"),
    path("auth/",views.report_check,name="auth"),
    path("cell/",views.cell,name="cell")
]