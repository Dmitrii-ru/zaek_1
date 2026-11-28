from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from zaek.views import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('zaek/', include('zaek.urls', namespace='zaek_app')),
    path('todo_session/', include('todo.urls',namespace='todo_session_app')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)