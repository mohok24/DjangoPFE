import os
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from whitenoise.middleware import WhiteNoiseMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoWebProject1.settings")
django_application = get_asgi_application()

# Optional: Enable debug mode if needed
settings.DEBUG = True

from datetime import datetime
from django.urls import path
from django.contrib import admin
from app import forms, views
from django.conf import settings
from django.conf.urls.static import static
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('patients/', views.patients, name='patients'),
    path('patients/details/<int:id>', views.details, name='details'),
    path('details/<int:id>', views.details, name='details'),
    path('reports/', views.reports, name='reports'),
    path('reports/rdetails/<int:id>', views.rdetails, name='rdetails'),
    path('rdetails/<int:id>', views.rdetails, name='rdetails'),
    path('reports/search/', views.report_search, name='report_search'),
    path('patients/search/', views.patient_search, name='patient_search'),
    path('send_message/', views.send_message, name='send_message'),
    path('restricted/', views.restricted_view, name='restricted'),
    path('messages/', views.receive_message, name='messages'),
    path('delete_message/', views.delete_message, name='delete_message'),
    path('statistics',views.statistics,name='statistics'),
    path('message/<int:message_id>/', views.message_details, name='message_details'),
    path('statistics',views.statistics,name='statistics'),
    path('all_reports',views.all_reports,name='all_reports'),
    path('all_patients',views.all_patients,name='all_patients'),
    path('profile/<int:user_id>/',views.profile,name='profile'),
    path('add_report/',views.add_report,name='add_report'),
    path('add_report/predict',views.predict,name='predict'),
    path('logout/',views.logout_view,name='logout'),
    path('homeres/',views.homeres,name='homeres'),
    path('homerad/',views.homerad,name='homerad'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/',views.upload,name='upload')

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




