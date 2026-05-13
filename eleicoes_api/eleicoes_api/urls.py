from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


from backend.views import EleitorViewSet, EleicaoViewSet, CandidatoViewSet, VotoViewSet


schema_view = get_schema_view(
   openapi.Info(
      title="Sistema de Eleições API",
      default_version='v1',
      description="Documentação da API de Eleições",
   ),
   public=True,
)

router = routers.DefaultRouter()
router.register(r'eleitores', EleitorViewSet)
router.register(r'eleicoes', EleicaoViewSet)
router.register(r'candidatos', CandidatoViewSet)
router.register(r'votos', VotoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]