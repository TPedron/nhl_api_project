from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('goalie_pp_support/', include('goalie_pp_support.urls')),
    path('admin/', admin.site.urls),
]