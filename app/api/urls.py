from rest_framework.routers import DefaultRouter
from django.urls import path
from api.mailing import views as views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

v1_router = DefaultRouter()
v1_router.register('tags', views.TagViewSet)
v1_router.register('operators', views.OperatorViewSet)
v1_router.register('clients', views.ClientViewSet)
v1_router.register('mailings', views.MailingViewSet)


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html",
            url_name="schema",
        ),
        name="swagger-ui",
    ),
]+v1_router.urls
