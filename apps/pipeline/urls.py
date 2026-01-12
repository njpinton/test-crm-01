from django.urls import path
from . import views

app_name = 'pipeline'

urlpatterns = [
    # Main views
    path('', views.KanbanBoardView.as_view(), name='kanban'),
    path('list/', views.DealListView.as_view(), name='list'),

    # Deal CRUD
    path('deals/create/', views.DealCreateView.as_view(), name='deal_create'),
    path('deals/<uuid:pk>/', views.DealDetailView.as_view(), name='deal_detail'),
    path('deals/<uuid:pk>/edit/', views.DealUpdateView.as_view(), name='deal_edit'),
    path('deals/<uuid:pk>/delete/', views.DealDeleteView.as_view(), name='deal_delete'),

    # HTMX endpoints for Kanban interactions
    path('htmx/move-deal/', views.MoveDealView.as_view(), name='move_deal'),
    path('htmx/close-deal/<uuid:pk>/', views.CloseDealView.as_view(), name='close_deal'),
    path('htmx/search/', views.DealSearchView.as_view(), name='search'),

    # File management
    path('deals/<uuid:deal_pk>/files/', views.DealFileListView.as_view(), name='deal_files'),
    path('deals/<uuid:deal_pk>/files/upload/', views.DealFileUploadView.as_view(), name='file_upload'),
    path('files/<uuid:pk>/delete/', views.DealFileDeleteView.as_view(), name='file_delete'),
]
