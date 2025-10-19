# app: marketplace/models.py
from django.conf import settings
from django.db import models

# USER = settings.AUTH_USER_MODEL
USER = settings.AUTH_USER_MODEL



# -------------------
# USER PROFILE
# -------------------
class Profile(models.Model):
    CATEGORY_CHOICES = [
        ("gadgets", "Gadgets"),
        ("fashion", "Fashion"),
        ("sports", "Sports"),
        ("books", "Books"),
        ("home", "Home"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(USER, on_delete=models.CASCADE, related_name="profile")
    is_seller = models.BooleanField(default=False)

    # Seller details
    wallet_address = models.CharField(max_length=42, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Farcaster & appearance
    farcaster_fid = models.CharField(max_length=128, blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"


# -------------------
# Listings (Products)
# -------------------
class Listing(models.Model):
    seller = models.ForeignKey(USER, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=36, decimal_places=18)
    token_address = models.CharField(max_length=42, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.seller.username}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listing_images/")  
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]



# -------------------
# Order
# -------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='orders')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    escrow = models.OneToOneField('Escrow', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.listing.title} ({self.status})"



# -------------------
# ESCROW
# -------------------
class Escrow(models.Model):
    STATUS_AWAITING = "AWAITING_PAYMENT"
    STATUS_FUNDED = "FUNDED"
    STATUS_SHIPPED = "SHIPPED"
    STATUS_COMPLETE = "COMPLETE"
    STATUS_DISPUTE = "DISPUTE"
    STATUS_REFUNDED = "REFUNDED"

    STATUS_CHOICES = [
        (STATUS_AWAITING, "Awaiting Payment"),
        (STATUS_FUNDED, "Funded"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_COMPLETE, "Complete"),
        (STATUS_DISPUTE, "Dispute"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    # on-chain identifiers
    onchain_id = models.CharField(max_length=100, blank=True, null=True)
    contract_address = models.CharField(max_length=42)
    chain = models.CharField(max_length=32, default="arbitrum_one")

    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True)
    buyer = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True, related_name="purchases")
    seller = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True, related_name="sales")

    amount = models.DecimalField(max_digits=36, decimal_places=18)
    raw_amount = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AWAITING)

    tx_create = models.CharField(max_length=100, blank=True, null=True)
    tx_fund = models.CharField(max_length=100, blank=True, null=True)
    tx_release = models.CharField(max_length=100, blank=True, null=True)
    tx_refund = models.CharField(max_length=100, blank=True, null=True)

    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["onchain_id"]),
            models.Index(fields=["contract_address"]),
        ]

    def __str__(self):
        return f"Escrow {self.onchain_id or self.pk} ({self.status})"

    # helper lifecycle methods
    def mark_funded(self, tx_hash: str, raw_amount: str = None):
        self.status = self.STATUS_FUNDED
        self.tx_fund = tx_hash
        if raw_amount:
            self.raw_amount = raw_amount
        self.save(update_fields=["status", "tx_fund", "raw_amount", "updated_at"])

    def mark_released(self, tx_hash: str):
        self.status = self.STATUS_COMPLETE
        self.tx_release = tx_hash
        self.save(update_fields=["status", "tx_release", "updated_at"])

    def mark_refunded(self, tx_hash: str):
        self.status = self.STATUS_REFUNDED
        self.tx_refund = tx_hash
        self.save(update_fields=["status", "tx_refund", "updated_at"])


class EscrowEvent(models.Model):
    EVENT_TYPES = [
        ("payment_secured", "Payment Secured"),
        ("item_shipped", "Item Shipped"),
        ("delivered", "Item Delivered"),
        ("released", "Funds Released"),
        ("refunded", "Funds Refunded"),
        ("dispute_opened", "Dispute Opened"),
        ("dispute_resolved", "Dispute Resolved"),
    ]


    escrow = models.ForeignKey(Escrow, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default="payment_secured")
    tx_hash = models.CharField(max_length=100, blank=True, null=True)
    block_number = models.PositiveBigIntegerField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_event_type_display()} - Escrow #{self.escrow.id}"


# -------------------
# DISPUTES
# -------------------
class Dispute(models.Model):
    escrow = models.OneToOneField(Escrow, on_delete=models.CASCADE, related_name="dispute")
    raised_by = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    evidence = models.JSONField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    resolution_note = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        USER, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_disputes"
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.escrow
