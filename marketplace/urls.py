from django.urls import path
from .import views


urlpatterns = [
    path("listing-images/", views.ListingImageListCreateView.as_view(), name="listing-image-list-create"),
    path("listing-images/<int:pk>/", views.ListingImageDetailView.as_view(), name="listing-image-detail"),
    path("listings/", views.ListingListCreateView.as_view(), name="listing-list-create"),
    path("listings/<int:pk>/", views.ListingDetailView.as_view(), name="listing-detail"),
    path("orders/", views.OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path('escrows/', views.EscrowListCreateView.as_view(), name='escrow-list-create'),
    path('escrows/<int:pk>/', views.EscrowDetailView.as_view(), name='escrow-detail'),
    path('dispute/', views.DisputeCreateView.as_view(), name='dispute-create'),
    path("disputes/<int:pk>/", views.DisputeCreateView.as_view(), name="dispute-detail-update"),
    path("escrow-events/", views.EscrowEventListView.as_view(), name="escrow-event-list"),
    path("escrow-events/<int:pk>/", views.EscrowDetailView.as_view(), name="escrow-event-detail"),
]





# urlpatterns = [
#     # Listings
#     path("listings/", views.ListingListCreateView.as_view(), name="listing-list-create"),   # GET list, POST create
#     path("listings/<int:pk>/", views.ListingRetrieveUpdateDeleteView.as_view(), name="listing-detail"),

#     # Listing images (upload)
#     path("listings/<int:listing_pk>/images/", views.ListingImageCreateView.as_view(), name="listing-image-create"),
#     path("listings/<int:listing_pk>/images/<int:pk>/", views.ListingImageDeleteView.as_view(), name="listing-image-delete"),

#     # Orders
#     path("orders/", views.OrderListCreateView.as_view(), name="order-list-create"),
#     path("orders/<int:pk>/", views.OrderRetrieveView.as_view(), name="order-detail"),

#     # Escrows (on-chain tracking)
#     path("escrows/", views.EscrowListCreateView.as_view(), name="escrow-list-create"),
#     path("escrows/<int:pk>/", views.EscrowRetrieveView.as_view(), name="escrow-detail"),

#     # Disputes
#     path("disputes/", views.DisputeCreateListView.as_view(), name="dispute-list-create"),
#     path("disputes/<int:pk>/", views.DisputeRetrieveUpdateView.as_view(), name="dispute-detail-update"),

#     # Escrow events (optionally filter ?user_only=true)
#     path("escrow-events/", views.EscrowEventListView.as_view(), name="escrow-event-list"),
#     path("escrow-events/<int:pk>/", views.EscrowEventRetrieveView.as_view(), name="escrow-event-detail"),
# ]