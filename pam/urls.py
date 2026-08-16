from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include(("account.urls", 'account'), namespace='account')),
    path('', include(("core.urls", 'core'), namespace='core')),
    path('planner/', include(("planner.urls", 'planner'), namespace='planner')),
    path('health/', include(("health.urls", 'health'), namespace='health')),
    path('knowledge/', include(("knowledgebase.urls", 'knowledge'), namespace='knowledge')),
]
