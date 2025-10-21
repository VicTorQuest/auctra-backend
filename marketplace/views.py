from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import ListingImage, Listing, Order, Escrow, EscrowEvent, Dispute
from django.db.models import Q
from .serializers import ListingImageSerializer, ListingSerializer, OrderSerializer, EscrowSerializer, EscrowEventSerializer, DisputeSerializer, DisputeUpdateSerializer


@extend_schema(
    summary="List and upload listing images",
    description=(
        "Retrieve all images for listings or upload a new image associated "
        "with a particular listing. Each image has an order number to determine display priority."
    ),
    examples=[
        OpenApiExample(
            'Example Listing Image Response',
            value={
                "id": 1,
                "image": "https://example.com/media/listings/image1.jpg",
                "order": 1
            },
            response_only=True,
        ),
        OpenApiExample(
            'Example Listing Image Upload Request',
            value={
                "image": "listing_photo.jpg",
                "order": 1
            },
            request_only=True,
        ),
    ]
)
class ListingImageListCreateView(generics.ListCreateAPIView):
    """
    Handles retrieval of all listing images and uploading new ones.
    """
    queryset = ListingImage.objects.all()
    serializer_class = ListingImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()
        return Response(
            {"message": "Listing image uploaded successfully"},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Retrieve, update, or delete a specific listing image",
    description="Perform detail operations on a single listing image using its ID.",
    examples=[
        OpenApiExample(
            'Example Listing Image Detail',
            value={
                "id": 1,
                "image": "https://example.com/media/listings/image1.jpg",
                "order": 1
            },
            response_only=True,
        ),
    ]
)
class ListingImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting individual listing images.
    """
    queryset = ListingImage.objects.all()
    serializer_class = ListingImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@extend_schema(
    summary="List and create product listings",
    description=(
        "Retrieve all product listings or create a new listing. "
        "Authenticated users (sellers) can add listings with optional images."
    ),
    examples=[
        OpenApiExample(
            'Example Listing Creation Request',
            value={
                "title": "Apple MacBook Pro M1",
                "description": "Lightly used MacBook Pro M1 in perfect condition.",
                "price": "1200.00",
                "category": "Laptops",
                "image": "macbook.jpg"
            },
            request_only=True,
        ),
        OpenApiExample(
            'Example Listing Response',
            value={
                "id": 12,
                "seller": {
                    "id": 3,
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile": {
                        "wallet_address": "0xabc123...",
                        "category": "electronics",
                        "location_city": "Lagos",
                        "location_country": "Nigeria",
                        "description": "Seller of high-quality gadgets",
                        "farcaster_fid": None,
                        "bio": "Tech enthusiast and trader",
                        "avatar": "https://example.com/media/avatars/johndoe.jpg",
                        "is_seller": True,
                        "created_at": "2025-10-11T09:00:00Z"
                    }
                },
                "title": "Apple MacBook Pro M1",
                "description": "Lightly used MacBook Pro M1 in perfect condition.",
                "price": "1200.00",
                "category": "Laptops",
                "image": "https://example.com/media/listings/macbook.jpg",
                "created_at": "2025-10-11T09:00:00Z",
                "updated_at": "2025-10-11T09:30:00Z"
            },
            response_only=True,
        ),
    ]
)
class ListingListCreateView(generics.ListCreateAPIView):
    """
    Handles retrieving all product listings and creating new ones.
    """
    queryset = Listing.objects.all().select_related("seller__profile")
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
        return Response(
            {"message": "Listing created successfully"},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Retrieve, update, or delete a specific product listing",
    description="Allows sellers to manage their listings by ID.",
    examples=[
        OpenApiExample(
            'Example Listing Detail Response',
            value={
                "id": 12,
                "seller": {
                    "id": 3,
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile": {
                        "wallet_address": "0xabc123...",
                        "category": "electronics",
                        "location_city": "Lagos",
                        "location_country": "Nigeria",
                        "description": "Seller of high-quality gadgets",
                        "farcaster_fid": None,
                        "bio": "Tech enthusiast and trader",
                        "avatar": "https://example.com/media/avatars/johndoe.jpg",
                        "is_seller": True,
                        "created_at": "2025-10-11T09:00:00Z"
                    }
                },
                "title": "Apple MacBook Pro M1",
                "description": "Lightly used MacBook Pro M1 in perfect condition.",
                "price": "1200.00",
                "category": "Laptops",
                "image": "https://example.com/media/listings/macbook.jpg",
                "created_at": "2025-10-11T09:00:00Z",
                "updated_at": "2025-10-11T09:30:00Z"
            },
            response_only=True,
        ),
    ]
)
class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single listing.
    """
    queryset = Listing.objects.all().select_related("seller__profile")
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()
        return Response(
            {"message": "Listing updated successfully"},
            status=status.HTTP_200_OK
        )
    

@extend_schema(
    summary="List and create orders",
    description=(
        "Retrieve all orders or create a new order for a listing. "
        "Authenticated users (buyers) can place orders for available listings."
    ),
    examples=[
        OpenApiExample(
            "Example Order Creation Request",
            value={
                "listing_id": 101,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example Order Response",
            value={
                "id": 45,
                "buyer": {
                    "id": 3,
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile": {
                        "wallet_address": "0xabc123...",
                        "category": "electronics",
                        "location_city": "Lagos",
                        "location_country": "Nigeria",
                        "description": "Trusted gadget seller",
                        "farcaster_fid": None,
                        "bio": "Tech enthusiast and trader",
                        "avatar": "https://example.com/media/avatars/victor.jpg",
                        "is_seller": True,
                        "created_at": "2025-10-11T09:00:00Z"
                    }
                },
                "listing": {
                    "id": 101,
                    "seller": {
                        "id": 5,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "profile": {
                            "wallet_address": "0xdef456...",
                            "category": "laptops",
                            "location_city": "Abuja",
                            "location_country": "Nigeria",
                            "description": "MacBooks and accessories",
                            "farcaster_fid": None,
                            "bio": "Verified seller",
                            "avatar": "https://example.com/media/avatars/john.jpg",
                            "is_seller": True,
                            "created_at": "2025-10-10T10:00:00Z"
                        }
                    },
                    "title": "MacBook Air M2",
                    "description": "Brand new MacBook Air M2, 8GB RAM, 256GB SSD.",
                    "price": "1500.00",
                    "category": "Laptops",
                    "image": "https://example.com/media/listings/macbook_air.jpg",
                    "created_at": "2025-10-11T09:00:00Z",
                    "updated_at": "2025-10-11T09:30:00Z"
                },
                "status": "pending",
                "created_at": "2025-10-11T12:00:00Z",
                "updated_at": "2025-10-11T12:00:00Z"
            },
            response_only=True,
        ),
    ]
)
class OrderListCreateView(generics.ListCreateAPIView):
    """
    Handles retrieving all orders and creating new ones.
    Buyers can create orders for listings, while sellers can view their received orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Buyers see their orders, sellers see orders for their listings
        return Order.objects.filter(
            Q(buyer=user) | Q(listing__seller=user)
        ).select_related("buyer__profile", "listing__seller__profile")

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)
        return Response(
            {"message": "Order placed successfully"},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Retrieve, update, or delete a specific order",
    description="Allows authenticated users to view, update, or cancel a specific order by ID.",
    examples=[
        OpenApiExample(
            "Example Order Detail Response",
            value={
                "id": 45,
                "buyer": {
                    "id": 3,
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile": {
                        "wallet_address": "0xabc123...",
                        "category": "electronics",
                        "location_city": "Lagos",
                        "location_country": "Nigeria",
                        "description": "Trusted gadget seller",
                        "farcaster_fid": None,
                        "bio": "Tech enthusiast and trader",
                        "avatar": "https://example.com/media/avatars/victor.jpg",
                        "is_seller": True,
                        "created_at": "2025-10-11T09:00:00Z"
                    }
                },
                "listing": {
                    "id": 101,
                    "seller": {
                        "id": 5,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "profile": {
                            "wallet_address": "0xdef456...",
                            "category": "laptops",
                            "location_city": "Abuja",
                            "location_country": "Nigeria",
                            "description": "MacBooks and accessories",
                            "farcaster_fid": None,
                            "bio": "Verified seller",
                            "avatar": "https://example.com/media/avatars/john.jpg",
                            "is_seller": True,
                            "created_at": "2025-10-10T10:00:00Z"
                        }
                    },
                    "title": "MacBook Air M2",
                    "description": "Brand new MacBook Air M2, 8GB RAM, 256GB SSD.",
                    "price": "1500.00",
                    "category": "Laptops",
                    "image": "https://example.com/media/listings/macbook_air.jpg",
                    "created_at": "2025-10-11T09:00:00Z",
                    "updated_at": "2025-10-11T09:30:00Z"
                },
                "status": "pending",
                "created_at": "2025-10-11T12:00:00Z",
                "updated_at": "2025-10-11T12:00:00Z"
            },
            response_only=True,
        ),
    ]
)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single order.
    Only the buyer or the seller involved can access this order.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all().select_related("buyer__profile", "listing__seller__profile")

    def perform_update(self, serializer):
        serializer.save()
        return Response(
            {"message": "Order updated successfully"},
            status=status.HTTP_200_OK
        )
    

@extend_schema(
    summary="List and create escrows",
    description=(
        "Retrieve all escrow records where the user is involved (as buyer or seller), "
        "or create a new escrow when a buyer purchases a listing."
    ),
    examples=[
        OpenApiExample(
            "Example Escrow Creation Request",
            value={"listing_id": 101, "onchain_id": "escrow_0x45a9"},
            request_only=True,
        ),
        OpenApiExample(
            "Example Escrow Response",
            value={
                "id": 12,
                "onchain_id": "escrow_0x45a9",
                "contract_address": "0xAbC123EfF789...",
                "chain": "arbitrum",
                "listing": {
                    "id": 101,
                    "title": "MacBook Air M2",
                    "price": "1500.00",
                    "category": "Laptops",
                    "seller": {
                        "id": 5,
                        "username": "john_doe",
                        "email": "john@example.com"
                    }
                },
                "buyer": {
                    "id": 3,
                    "username": "jane_doe",
                    "email": "jane@example.com"
                },
                "amount": "1500.00",
                "raw_amount": "1500000000000000000",
                "status": "funded",
                "tx_create": "0x98abcd12345...",
                "tx_fund": "0x1122ffcc...",
                "tx_release": None,
                "tx_refund": None,
                "metadata": {"notes": "Funds locked until delivery confirmation"},
                "created_at": "2025-10-11T12:00:00Z",
                "updated_at": "2025-10-11T13:00:00Z"
            },
            response_only=True,
        ),
    ]
)
class EscrowListCreateView(generics.ListCreateAPIView):
    """
    Handles retrieving all escrow records and creating new ones.
    Buyers can initiate escrow for listings they purchase, and both buyers and sellers can view their escrows.
    """
    serializer_class = EscrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Escrow.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related("buyer__profile", "seller__profile", "listing__seller__profile")

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)
        return Response(
            {"message": "Escrow created successfully"},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Retrieve a specific escrow",
    description=(
        "Fetch details of a specific escrow record by its ID. "
        "Only participants of the escrow (buyer or seller) can access it."
    ),
    examples=[
        OpenApiExample(
            "Example Escrow Detail Response",
            value={
                "id": 12,
                "onchain_id": "escrow_0x45a9",
                "contract_address": "0xAbC123EfF789...",
                "chain": "arbitrum",
                "listing": {
                    "id": 101,
                    "title": "MacBook Air M2",
                    "price": "1500.00",
                    "category": "Laptops",
                    "seller": {
                        "id": 5,
                        "username": "john_doe",
                        "email": "john@example.com"
                    }
                },
                "buyer": {
                    "id": 3,
                    "username": "jane_doe",
                    "email": "jane@example.com"
                },
                "amount": "1500.00",
                "raw_amount": "1500000000000000000",
                "status": "funded",
                "tx_create": "0x98abcd12345...",
                "tx_fund": "0x1122ffcc...",
                "tx_release": None,
                "tx_refund": None,
                "metadata": {"notes": "Funds locked until delivery confirmation"},
                "created_at": "2025-10-11T12:00:00Z",
                "updated_at": "2025-10-11T13:00:00Z"
            },
            response_only=True,
        ),
    ]
)
class EscrowDetailView(generics.RetrieveAPIView):
    """
    Handles retrieving a single escrow record by ID.
    Ensures that only the buyer or seller involved in the escrow can access its details.
    """
    serializer_class = EscrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Escrow.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related("buyer__profile", "seller__profile", "listing__seller__profile")
    

# ---------------------- Escrow Events ---------------------- #
@extend_schema(
    summary="List escrow events",
    description="List blockchain events associated with escrows. Optionally filter in the view using query params.",
    responses={200: EscrowEventSerializer(many=True)},
    examples=[
        OpenApiExample("Escrow Event Resp", response_only=True, value=[{
            "id": 1,
            "escrow": 42,
            "event_type": "payment_secured",
            "event_type_display": "Payment Secured",
            "tx_hash": "0x123abc...",
            "block_number": 19827391,
            "payload": {"from": "0xabc...", "to": "0xdef...", "amount": "2.5"},
            "created_at": "2025-10-11T15:24:30Z",
        }]),
    ],
    tags=["Marketplace"],
)
class EscrowEventListView(generics.ListAPIView):
    """
    List escrow-related blockchain events. Supports optional filtering by authenticated user's escrows.
    Use query param `user_only=true` to restrict to current user's escrows.
    """
    serializer_class = EscrowEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = EscrowEvent.objects.select_related("escrow")

    def get_queryset(self):
        queryset = super().get_queryset()
        user_only = self.request.query_params.get("user_only")
        if user_only and user_only.lower() == "true":
            user = self.request.user
            queryset = queryset.filter(Q(escrow__buyer=user) | Q(escrow__seller=user))
        return queryset.order_by("-created_at")


# ---------------------- Disputes ---------------------- #
@extend_schema(
    summary="Create disputes",
    description="Authenticated buyers can create disputes associated with an order/escrow.",
    request=DisputeSerializer,
    responses={201: DisputeSerializer},
    examples=[
        OpenApiExample("Dispute Create Req", request_only=True, value={
            "escrow": 12,
            "reason": "Item not delivered",
            "description": "Hasn't arrived after 10 days."
        }),
        OpenApiExample("Dispute Create Resp", response_only=True, value={
            "id": 45,
            "buyer": {"id": 3, "username": "john_doe"},
            "escrow": 12,
            "reason": "Item not delivered",
            "status": "open",
            "created_at": "2025-10-11T14:45:00Z"
        }),
    ],
    tags=["Marketplace"],
)
class DisputeCreateView(generics.CreateAPIView):
    """
    Create a dispute for an escrow/order. The buyer field is automatically set from the authenticated user.
    """
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


@extend_schema(
    summary="Update/resolve a dispute",
    description="Admins or moderators can update a dispute's status and resolution notes. When status is set to 'resolved', resolved_at is auto-filled.",
    request=DisputeUpdateSerializer,
    responses={200: DisputeUpdateSerializer},
    examples=[
        OpenApiExample("Dispute Update Req", request_only=True, value={
            "status": "resolved",
            "resolution_notes": "Refund approved, buyer compensated."
        }),
        OpenApiExample("Dispute Update Resp", response_only=True, value={
            "status": "resolved",
            "resolution_notes": "Refund approved, buyer compensated.",
            "resolved_at": "2025-10-11T20:12:45Z"
        }),
    ],
    tags=["Marketplace"],
)
class DisputeUpdateView(generics.UpdateAPIView):
    """
    Update dispute status and resolution notes. Restricted to admin users.
    """
    queryset = Dispute.objects.all()
    serializer_class = DisputeUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
