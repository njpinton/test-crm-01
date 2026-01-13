from django.urls import path
from . import views

app_name = 'pipeline'

urlpatterns = [
    # Main views
    path('', views.KanbanBoardView.as_view(), name='kanban'),
    path('schedules/', views.ScheduleKanbanView.as_view(), name='schedule_kanban'),
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
    path('htmx/move-schedule/', views.MoveScheduleView.as_view(), name='move_schedule'),
    path('htmx/assign-schedule/<uuid:pk>/', views.AssignScheduleView.as_view(), name='assign_schedule'),

    # File management
    path('deals/<uuid:deal_pk>/files/', views.DealFileListView.as_view(), name='deal_files'),
    path('deals/<uuid:deal_pk>/files/upload/', views.DealFileUploadView.as_view(), name='file_upload'),
    path('files/<uuid:pk>/delete/', views.DealFileDeleteView.as_view(), name='file_delete'),

    # Schedule management
    path('deals/<uuid:deal_pk>/schedules/', views.DealScheduleListView.as_view(), name='schedule_list'),
    path('deals/<uuid:deal_pk>/schedules/add/', views.DealScheduleCreateView.as_view(), name='schedule_add'),
    path('schedules/<uuid:pk>/edit/', views.DealScheduleUpdateView.as_view(), name='schedule_edit'),
    path('schedules/<uuid:pk>/delete/', views.DealScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedules/<uuid:pk>/complete/', views.DealScheduleCompleteView.as_view(), name='schedule_complete'),
    path('schedules/<uuid:pk>/status/', views.DealScheduleStatusUpdateView.as_view(), name='schedule_status'),

    # Comment management
    path('deals/<uuid:deal_pk>/comments/add/', views.DealCommentCreateView.as_view(), name='comment_add'),
    path('comments/<uuid:pk>/delete/', views.DealCommentDeleteView.as_view(), name='comment_delete'),
]
