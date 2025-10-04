from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Vendor, Field, Booking


class VendorModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner1", password="pass12345")

    def test_create_vendor_minimal(self):
        v = Vendor.objects.create(
            owner=self.owner,
            name="GOR UI",
            contact="08123456789",
            email="gor@example.com",
            address="Depok"
        )
        self.assertEqual(str(v), "GOR UI")
        self.assertEqual(v.owner, self.owner)

    def test_delete_owner_cascade_vendor(self):
        v = Vendor.objects.create(owner=self.owner, name="Champion Futsal")
        self.owner.delete()
        self.assertFalse(Vendor.objects.filter(id=v.id).exists())


class FieldModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner2", password="pass12345")
        self.vendor = Vendor.objects.create(owner=self.owner, name="Champion Futsal", address="Depok")

    def test_field_creation_with_vendor(self):
        f = Field.objects.create(
            vendor=self.vendor,
            name="Lapangan A",
            sport_type="futsal",
            location="Depok",
            price_per_hour=150000,
            is_available=True,
        )
        self.assertIn("Lapangan A", str(f))
        self.assertIn("Futsal", str(f))  # label dari choices
        self.assertEqual(f.vendor, self.vendor)
        self.assertEqual(f.price_per_hour, 150000)
        self.assertTrue(f.is_available)

    def test_field_creation_without_vendor_is_allowed(self):
        f = Field.objects.create(
            vendor=None,
            name="Lapangan Tanpa Vendor",
            sport_type="badminton",
            location="Jakarta",
        )
        self.assertIsNone(f.vendor)
        self.assertEqual(f.price_per_hour, 0)  # default
        self.assertTrue(f.is_available)        # default

    def test_invalid_sport_type_raises_on_full_clean(self):
        f = Field(
            vendor=self.vendor,
            name="Lapangan X",
            sport_type="pingpong_tidak_terdaftar",
            location="Bandung",
        )
        with self.assertRaises(ValidationError):
            f.full_clean()

    def test_delete_vendor_cascade_field(self):
        f = Field.objects.create(
            vendor=self.vendor,
            name="Lapangan B",
            sport_type="tennis",
            location="Depok",
        )
        self.vendor.delete()
        self.assertFalse(Field.objects.filter(id=f.id).exists())


class BookingModelTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner3", password="pass12345")
        vendor = Vendor.objects.create(owner=owner, name="Sport Hall", address="Jakarta")
        self.field = Field.objects.create(
            vendor=vendor,
            name="Court 1",
            sport_type="basket",
            location="Jakarta",
            price_per_hour=100000,
        )

    def test_booking_creation_basic(self):
        start = timezone.now()
        end = start + timedelta(hours=2)
        b = Booking.objects.create(
            field=self.field,
            customer_name="Burhan",
            start_time=start,
            end_time=end,
            total_price=200000,
        )
        self.assertEqual(b.field, self.field)
        self.assertEqual(b.customer_name, "Burhan")
        self.assertEqual(b.total_price, 200000)
        self.assertIn("Booking Burhan - Court 1", str(b))

    def test_duration_hours_property(self):
        start = timezone.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1, minutes=30)
        b = Booking.objects.create(
            field=self.field,
            customer_name="Marcello",
            start_time=start,
            end_time=end,
            total_price=0,
        )
        self.assertAlmostEqual(b.duration_hours, 1.5, places=5)

    def test_delete_field_cascade_booking(self):
        start = timezone.now()
        end = start + timedelta(hours=1)
        b = Booking.objects.create(
            field=self.field,
            customer_name="Sofita",
            start_time=start,
            end_time=end,
            total_price=100000,
        )
        self.field.delete()
        self.assertFalse(Booking.objects.filter(id=b.id).exists())
