from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
	path('admin/', admin.site.urls),

	# PWA: sw.js debe responder en la raiz para controlar todo el sitio,
	# por eso no se sirve como archivo estatico.
	path(
		'sw.js',
		TemplateView.as_view(
			template_name='sw.js',
			content_type='application/javascript'
		),
		name='service_worker'
	),
	path(
		'manifest.json',
		TemplateView.as_view(
			template_name='manifest.json',
			content_type='application/manifest+json'
		),
		name='manifest'
	),
	path(
		'sin-conexion/',
		TemplateView.as_view(template_name='sin_conexion.html'),
		name='sin_conexion'
	),

	path('', include('pedidos.urls')),
]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
