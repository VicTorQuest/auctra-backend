from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from.models import Listing, ListingImage, Order, Escrow, EscrowEvent, Dispute
from accounts.serializers import UserSerializer


User = get_user_model()



@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Listing Image Example',
            summary='Example of a listing image',
            value={
                "id": 1,
                "image": "https://example.com/media/listings/image1.jpg",
                "order": 1
            },
        )
    ]
) 
class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "image", "order"]
        read_only_fields = ["id"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Listing Example',
            summary='Example of a product listing',
            description='Represents an item for sale by a seller.',
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
        )
    ]
)
class ListingSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    images = ListingImageSerializer(many=True, required=False)

    class Meta:
        model = Listing
        fields = [
            "id",
            "seller",
            "title",
            "description",
            "price",
            "category",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        images_data = validated_data.pop("images", [])
        validated_data["seller"] = request.user
        listing = super().create(validated_data)

        for image_data in images_data:
            ListingImage.objects.create(listing=listing, **image_data)

        return listing


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Order Example',
            summary='Example of an order placed by a buyer',
            description='Represents a purchase made by a buyer for a specific listing.',
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
        )
    ]
)
class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source="listing", write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "buyer",
            "listing",
            "listing_id",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["buyer"] = request.user
        return super().create(validated_data)
    

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Escrow Example',
            summary='Example escrow record',
            description='Represents an escrow created when a buyer purchases an item.',
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
                "metadata": {
                    "notes": "Funds locked until delivery confirmation"
                },
                "created_at": "2025-10-11T12:00:00Z",
                "updated_at": "2025-10-11T13:00:00Z"
            },
        )
    ]
)
class EscrowSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source="listing", write_only=True
    )

    class Meta:
        model = Escrow
        fields = [
            "id",
            "onchain_id",
            "contract_address",
            "chain",
            "listing",
            "listing_id",
            "buyer",
            "seller",
            "amount",
            "raw_amount",
            "status",
            "tx_create",
            "tx_fund",
            "tx_release",
            "tx_refund",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "buyer",
            "seller",
            "status",
            "tx_create",
            "tx_fund",
            "tx_release",
            "tx_refund",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        listing = validated_data.get("listing")

        # Automatically assign buyer and seller
        validated_data["buyer"] = request.user
        validated_data["seller"] = listing.seller

        return super().create(validated_data)
    

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Create Dispute Example",
            summary="Example payload for creating a dispute",
            description=(
                "A buyer raises a dispute related to a specific escrow transaction "
                "if the item was not delivered or arrived damaged."
            ),
            value={
                "escrow": 12,
                "reason": "Item not delivered",
                "description": "The seller marked the item as shipped 10 days ago, but it hasn’t arrived yet.",
            },
        ),
        OpenApiExample(
            name="Response Example",
            summary="Example response when dispute is created successfully",
            value={
                "id": 45,
                "buyer": {
                    "id": 3,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile": {
                        "wallet_address": "0xAbCdEf1234567890",
                        "category": "gadgets",
                        "location_city": "Lagos",
                        "location_country": "Nigeria",
                        "bio": "Verified buyer on Auctify",
                        "avatar": "/media/avatars/john.png",
                        "is_seller": False,
                        "created_at": "2025-10-11T14:32:10Z",
                    },
                },
                "escrow": 12,
                "reason": "Item not delivered",
                "description": "The seller marked the item as shipped 10 days ago, but it hasn’t arrived yet.",
                "status": "open",
                "created_at": "2025-10-11T14:45:00Z",
                "resolved_at": None,
            },
        ),
    ]
)
class DisputeSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Dispute
        fields = [
            "id",
            "buyer",
            "order",
            "reason",
            "description",
            "status",
            "created_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "buyer", "created_at", "resolved_at", "status"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["buyer"] = request.user
        return super().create(validated_data)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Example Escrow Event',
            summary='Example blockchain event record',
            description='Represents a single escrow transaction event synced from the blockchain or backend actions.',
            value={
                "id": 1,
                "escrow": 42,
                "event_type": "payment_secured",
                "event_type_display": "Payment Secured",
                "tx_hash": "0x123abc...",
                "block_number": 19827391,
                "payload": {"from": "0xabc...", "to": "0xdef...", "amount": "2.5"},
                "created_at": "2025-10-11T15:24:30Z",
            },
        )
    ]
)
class EscrowEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(
        source="get_event_type_display", 
        read_only=True,
        help_text="Human-readable version of the event type, e.g. 'Payment Secured'."
    )

    class Meta:
        model = EscrowEvent
        fields = [
            "id",
            "escrow",
            "event_type",
            "event_type_display",
            "tx_hash",
            "block_number",
            "payload",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "event_type_display"]

        extra_kwargs = {
            "escrow": {"help_text": "Reference ID of the escrow this event belongs to."},
            "event_type": {"help_text": "Type of event, e.g., 'payment_secured', 'item_shipped'."},
            "tx_hash": {"help_text": "Blockchain transaction hash for this event (if available)."},
            "block_number": {"help_text": "Block number in which the event was confirmed."},
            "payload": {"help_text": "Additional event data captured from the blockchain."},
            "created_at": {"help_text": "Timestamp when the event was recorded."},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Update Dispute Example",
            summary="Example payload for resolving a dispute",
            description=(
                "Used by an admin or moderator to mark a dispute as resolved. "
                "When the status is set to 'resolved', the `resolved_at` field is "
                "automatically updated to the current timestamp."
            ),
            value={
                "status": "resolved",
                "resolution_notes": "Refund approved, buyer compensated.",
            },
        ),
        OpenApiExample(
            name="Response Example",
            summary="Example response after dispute is resolved",
            value={
                "status": "resolved",
                "resolution_notes": "Refund approved, buyer compensated.",
                "resolved_at": "2025-10-11T20:12:45Z",
            },
        ),
    ]
)
class DisputeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ["status", "resolution_notes", "resolved_at"]
        read_only_fields = ["resolved_at"]

    def update(self, instance, validated_data):
        # Mark resolved_at automatically when status changes to "resolved"
        if validated_data.get("status") == "resolved":
            from django.utils import timezone
            instance.resolved_at = timezone.now()

        return super().update(instance, validated_data)