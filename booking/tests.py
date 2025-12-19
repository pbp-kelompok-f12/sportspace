from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, time, timedelta
import json
import uuid

from .models import Venue, Booking
from .forms import BookingForm, BookingUpdateForm


class VenueModelTest(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address",
            description="Test Description"
        )

    def test_venue_creation(self):
        self.assertEqual(self.venue.name, "Test Venue")
        self.assertEqual(self.venue.location, "Test Location")
        self.assertEqual(self.venue.address, "Test Address")
        self.assertEqual(self.venue.description, "Test Description")
        self.assertIsNotNone(self.venue.id)
        self.assertIsNotNone(self.venue.created_at)

    def test_venue_str_representation(self):
        self.assertEqual(str(self.venue), "Test Venue")

    def test_venue_uuid_primary_key(self):
        self.assertIsInstance(self.venue.id, uuid.UUID)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )
        self.booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Test Customer",
            customer_email="customer@example.com",
            customer_phone="+1234567890"
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.venue, self.venue)
        self.assertEqual(self.booking.customer_name, "Test Customer")
        self.assertEqual(self.booking.customer_email, "customer@example.com")
        self.assertEqual(self.booking.customer_phone, "+1234567890")
        self.assertIsNotNone(self.booking.id)
        self.assertIsNotNone(self.booking.created_at)
        self.assertIsNotNone(self.booking.updated_at)

    def test_booking_str_representation(self):
        expected_str = f"{self.venue.name} - {self.booking.booking_date} {self.booking.start_time}"
        self.assertEqual(str(self.booking), expected_str)

    def test_booking_uuid_primary_key(self):
        self.assertIsInstance(self.booking.id, uuid.UUID)

    def test_booking_unique_together_constraint(self):
        # Try to create another booking with same venue, date, and start_time
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                venue=self.venue,
                booking_date=self.booking.booking_date,
                start_time=self.booking.start_time,
                end_time=time(12, 0),
                customer_name="Another Customer",
                customer_email="another@example.com",
                customer_phone="+0987654321"
            )


class BookingFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )

    def test_booking_form_valid_data(self):
        form_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'customer@example.com',
            'customer_phone': '+1234567890',
            'booking_date': date.today() + timedelta(days=1),
            'start_time': time(10, 0),
            'end_time': time(11, 0)
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_booking_form_invalid_data(self):
        form_data = {
            'customer_name': '',  # Empty name
            'customer_email': 'invalid-email',  # Invalid email
            'customer_phone': '',  # Empty phone
            'booking_date': '',  # Empty date
            'start_time': '',  # Empty start time
            'end_time': ''  # Empty end time
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)
        self.assertIn('customer_email', form.errors)
        self.assertIn('customer_phone', form.errors)
        self.assertIn('booking_date', form.errors)
        self.assertIn('start_time', form.errors)
        self.assertIn('end_time', form.errors)

    def test_booking_form_save(self):
        form_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'customer@example.com',
            'customer_phone': '+1234567890',
            'booking_date': date.today() + timedelta(days=1),
            'start_time': time(10, 0),
            'end_time': time(11, 0)
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())
        booking = form.save(commit=False)
        booking.user = self.user
        booking.venue = self.venue
        booking.save()
        self.assertEqual(Booking.objects.count(), 1)


class BookingUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )
        self.booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Test Customer",
            customer_email="customer@example.com",
            customer_phone="+1234567890"
        )

    def test_booking_update_form_valid_data(self):
        form_data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        form = BookingUpdateForm(data=form_data, instance=self.booking)
        self.assertTrue(form.is_valid())

    def test_booking_update_form_invalid_data(self):
        form_data = {
            'customer_name': '',  # Empty name
            'customer_email': 'invalid-email',  # Invalid email
            'customer_phone': ''  # Empty phone
        }
        form = BookingUpdateForm(data=form_data, instance=self.booking)
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)
        self.assertIn('customer_email', form.errors)
        self.assertIn('customer_phone', form.errors)

    def test_booking_update_form_save(self):
        form_data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        form = BookingUpdateForm(data=form_data, instance=self.booking)
        self.assertTrue(form.is_valid())
        form.save()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.customer_name, 'Updated Customer')
        self.assertEqual(self.booking.customer_email, 'updated@example.com')
        self.assertEqual(self.booking.customer_phone, '+0987654321')


class BookingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )
        self.booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Test Customer",
            customer_email="customer@example.com",
            customer_phone="+1234567890"
        )

    def test_venue_booking_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:venue_booking', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.venue.name)
        self.assertContains(response, 'Pilih Hari')
        self.assertContains(response, 'Pilih Waktu')

    def test_venue_booking_view_unauthenticated(self):
        response = self.client.get(reverse('booking:venue_booking', args=[self.venue.id]))
        self.assertRedirects(response, f'/accounts/login/?next=/booking/venue/{self.venue.id}/')

    def test_venue_booking_view_with_date_parameter(self):
        self.client.login(username='testuser', password='testpass123')
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(reverse('booking:venue_booking', args=[self.venue.id]) + f'?date={tomorrow}')
        self.assertEqual(response.status_code, 200)

    def test_my_bookings_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.customer_name)

    def test_my_bookings_view_unauthenticated(self):
        response = self.client.get(reverse('booking:my_bookings'))
        self.assertRedirects(response, '/accounts/login/?next=/booking/my-bookings/')

    def test_my_bookings_view_with_filter_active(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:my_bookings') + '?filter=active')
        self.assertEqual(response.status_code, 200)

    def test_my_bookings_view_with_filter_past(self):
        # Create a past booking
        past_booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() - timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Past Customer",
            customer_email="past@example.com",
            customer_phone="+1234567890"
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:my_bookings') + '?filter=past')
        self.assertEqual(response.status_code, 200)

    def test_create_booking_success(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': 'New Customer',
            'customer_email': 'new@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Booking.objects.count(), 2)

    def test_create_booking_duplicate_time_slot(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': self.booking.booking_date.strftime('%Y-%m-%d'),
            'start_time': self.booking.start_time.strftime('%H:%M'),
            'end_time': '12:00',
            'customer_name': 'Duplicate Customer',
            'customer_email': 'duplicate@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('already booked', response_data['message'])

    def test_create_booking_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': '',  # Invalid: empty name
            'customer_email': 'invalid-email',  # Invalid email
            'customer_phone': ''  # Invalid: empty phone
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Validation failed', response_data['message'])

    def test_create_booking_unauthenticated(self):
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': 'New Customer',
            'customer_email': 'new@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_update_booking_success(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        response = self.client.post(
            reverse('booking:update_booking', args=[self.booking.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify the booking was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.customer_name, 'Updated Customer')
        self.assertEqual(self.booking.customer_email, 'updated@example.com')
        self.assertEqual(self.booking.customer_phone, '+0987654321')

    def test_update_booking_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'customer_name': '',  # Invalid: empty name
            'customer_email': 'invalid-email',  # Invalid email
            'customer_phone': ''  # Invalid: empty phone
        }
        response = self.client.post(
            reverse('booking:update_booking', args=[self.booking.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Validation failed', response_data['message'])

    def test_update_booking_wrong_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        response = self.client.post(
            reverse('booking:update_booking', args=[self.booking.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)  # Booking not found for this user

    def test_update_booking_unauthenticated(self):
        data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        response = self.client.post(
            reverse('booking:update_booking', args=[self.booking.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_delete_booking_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(
            reverse('booking:delete_booking', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Booking.objects.count(), 0)

    def test_delete_booking_wrong_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.delete(
            reverse('booking:delete_booking', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 404)  # Booking not found for this user

    def test_delete_booking_unauthenticated(self):
        response = self.client.delete(
            reverse('booking:delete_booking', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_sync_venue_success(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'New Venue',
            'location': 'New Location',
            'address': 'New Address',
            'image_url': 'https://example.com/image.jpg'
        }
        response = self.client.post(
            reverse('booking:sync_venue'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Venue.objects.count(), 2)

    def test_sync_venue_missing_required_fields(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': '',  # Missing name
            'address': ''  # Missing address
        }
        response = self.client.post(
            reverse('booking:sync_venue'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('required', response_data['message'])

    def test_sync_venue_existing_venue(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': self.venue.name,  # Existing venue name
            'location': 'Updated Location',
            'address': self.venue.address,  # Existing venue address
            'image_url': 'https://example.com/new-image.jpg'
        }
        response = self.client.post(
            reverse('booking:sync_venue'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Venue.objects.count(), 1)  # No new venue created

    def test_sync_venue_unauthenticated(self):
        data = {
            'name': 'New Venue',
            'location': 'New Location',
            'address': 'New Address'
        }
        response = self.client.post(
            reverse('booking:sync_venue'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_booking_invalid_json(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('booking:create_booking'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_update_booking_invalid_json(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('booking:update_booking', args=[self.booking.id]),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_sync_venue_invalid_json(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('booking:sync_venue'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_delete_booking_exception(self):
        """Test delete booking with an exception during deletion"""
        self.client.login(username='testuser', password='testpass123')
        
        # Use a non-existent booking ID to trigger the exception path
        fake_booking_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.delete(
            reverse('booking:delete_booking', args=[fake_booking_id])
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_booking_success_after_exception(self):
        """Test successful deletion after exception handling is covered"""
        self.client.login(username='testuser', password='testpass123')
        
        # First, try to delete a non-existent booking to trigger exception handling
        fake_booking_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.delete(
            reverse('booking:delete_booking', args=[fake_booking_id])
        )
        self.assertEqual(response.status_code, 404)
        
        # Now delete the actual booking to cover the success path
        response = self.client.delete(
            reverse('booking:delete_booking', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])


class BookingIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )

    def test_complete_booking_workflow(self):
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # View venue booking page
        response = self.client.get(reverse('booking:venue_booking', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        
        # Create a booking
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # View my bookings
        response = self.client.get(reverse('booking:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Customer')
        
        # Update the booking
        booking = Booking.objects.first()
        update_data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        response = self.client.post(
            reverse('booking:update_booking', args=[booking.id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Delete the booking
        response = self.client.delete(
            reverse('booking:delete_booking', args=[booking.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Booking.objects.count(), 0)


class BookingEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            location="Test Location",
            address="Test Address"
        )

    def test_create_booking_missing_venue(self):
        """Test creating booking with non-existent venue"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': '00000000-0000-0000-0000-000000000000',  # Non-existent venue
            'booking_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # The view returns 200 with error message, not 404
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_create_booking_past_date(self):
        """Test creating booking with past date"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '14:00',
            'end_time': '15:00',
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        # The form should still be valid as we don't validate past dates in the form
        # This tests the form validation logic

    def test_create_booking_invalid_time_format(self):
        """Test creating booking with invalid time format"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'venue_id': str(self.venue.id),
            'booking_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': 'invalid-time',
            'end_time': 'also-invalid',
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '+1234567890'
        }
        response = self.client.post(
            reverse('booking:create_booking'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_update_booking_missing_booking(self):
        """Test updating non-existent booking"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'customer_name': 'Updated Customer',
            'customer_email': 'updated@example.com',
            'customer_phone': '+0987654321'
        }
        fake_booking_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(
            reverse('booking:update_booking', args=[fake_booking_id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_booking_missing_booking(self):
        """Test deleting non-existent booking"""
        self.client.login(username='testuser', password='testpass123')
        fake_booking_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.delete(
            reverse('booking:delete_booking', args=[fake_booking_id])
        )
        self.assertEqual(response.status_code, 404)

    def test_sync_venue_duplicate_name_different_address(self):
        """Test syncing venue with same name but different address"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': self.venue.name,  # Same name
            'location': 'Different Location',
            'address': 'Different Address',  # Different address
            'image_url': 'https://example.com/image.jpg'
        }
        response = self.client.post(
            reverse('booking:sync_venue'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # The sync_venue view uses get_or_create with name as the lookup field
        # So it should update the existing venue, not create a new one
        self.assertEqual(Venue.objects.count(), 1)

    def test_booking_form_with_unicode_characters(self):
        """Test booking form with unicode characters"""
        form_data = {
            'customer_name': 'José María',
            'customer_email': 'jose@example.com',  # Use ASCII email
            'customer_phone': '+1234567890',
            'booking_date': date.today() + timedelta(days=1),
            'start_time': time(10, 0),
            'end_time': time(11, 0)
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_venue_booking_with_invalid_date_parameter(self):
        """Test venue booking with invalid date parameter"""
        self.client.login(username='testuser', password='testpass123')
        # This should raise an exception due to invalid date format
        with self.assertRaises(ValueError):
            response = self.client.get(
                reverse('booking:venue_booking', args=[self.venue.id]) + '?date=invalid-date'
            )

    def test_my_bookings_with_invalid_filter(self):
        """Test my bookings with invalid filter parameter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:my_bookings') + '?filter=invalid')
        self.assertEqual(response.status_code, 200)

    def test_booking_model_with_special_characters(self):
        """Test booking model with special characters in customer data"""
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Test & Co. (Ltd.)",
            customer_email="test+tag@example.com",
            customer_phone="+1 (555) 123-4567"
        )
        self.assertEqual(booking.customer_name, "Test & Co. (Ltd.)")
        self.assertEqual(booking.customer_email, "test+tag@example.com")
        self.assertEqual(booking.customer_phone, "+1 (555) 123-4567")

    def test_venue_model_with_special_characters(self):
        """Test venue model with special characters"""
        venue = Venue.objects.create(
            name="Test & Co. Sports Complex",
            location="Jakarta Selatan, DKI Jakarta",
            address="Jl. Sudirman No. 123, RT.1/RW.1, Kec. Setiabudi",
            description="Lapangan padel dengan fasilitas lengkap & modern"
        )
        self.assertEqual(venue.name, "Test & Co. Sports Complex")
        self.assertIn("Sudirman", venue.address)

    def test_booking_form_validation_edge_cases(self):
        """Test booking form validation with edge cases"""
        # Test with very long strings
        form_data = {
            'customer_name': 'A' * 200,  # Very long name
            'customer_email': 'test@example.com',
            'customer_phone': '+1234567890',
            'booking_date': date.today() + timedelta(days=1),
            'start_time': time(10, 0),
            'end_time': time(11, 0)
        }
        form = BookingForm(data=form_data)
        # Should be valid as we don't have max_length constraints
        self.assertTrue(form.is_valid())

    def test_booking_update_form_partial_data(self):
        """Test booking update form with partial data"""
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Original Name",
            customer_email="original@example.com",
            customer_phone="+1234567890"
        )
        
        # Test with only name update
        form_data = {
            'customer_name': 'Updated Name',
            'customer_email': 'original@example.com',  # Same email
            'customer_phone': '+1234567890'  # Same phone
        }
        form = BookingUpdateForm(data=form_data, instance=booking)
        self.assertTrue(form.is_valid())
        form.save()
        booking.refresh_from_db()
        self.assertEqual(booking.customer_name, 'Updated Name')
        self.assertEqual(booking.customer_email, 'original@example.com')

    def test_venue_booking_time_slot_logic(self):
        """Test venue booking time slot availability logic"""
        # Create a booking for today at 10:00
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            customer_name="Test Customer",
            customer_email="test@example.com",
            customer_phone="+1234567890"
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:venue_booking', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        # The response should contain the booking information
        self.assertContains(response, self.venue.name)

    def test_booking_str_representation_edge_cases(self):
        """Test booking string representation with edge cases"""
        # Test with time at midnight
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(0, 0),  # Midnight
            end_time=time(1, 0),
            customer_name="Midnight Customer",
            customer_email="midnight@example.com",
            customer_phone="+1234567890"
        )
        expected_str = f"{self.venue.name} - {booking.booking_date} {booking.start_time}"
        self.assertEqual(str(booking), expected_str)

    def test_venue_str_representation_edge_cases(self):
        """Test venue string representation with edge cases"""
        # Test with empty name
        venue = Venue.objects.create(
            name="",
            location="Test Location",
            address="Test Address"
        )
        self.assertEqual(str(venue), "")

    def test_booking_form_widgets(self):
        """Test booking form widget configuration"""
        form = BookingForm()
        # Check that widgets are properly configured
        self.assertIn('class', form.fields['customer_name'].widget.attrs)
        self.assertIn('class', form.fields['customer_email'].widget.attrs)
        self.assertIn('class', form.fields['customer_phone'].widget.attrs)
        self.assertEqual(form.fields['booking_date'].widget.input_type, 'date')
        self.assertEqual(form.fields['start_time'].widget.input_type, 'time')
        self.assertEqual(form.fields['end_time'].widget.input_type, 'time')

    def test_booking_update_form_widgets(self):
        """Test booking update form widget configuration"""
        form = BookingUpdateForm()
        # Check that widgets are properly configured
        self.assertIn('class', form.fields['customer_name'].widget.attrs)
        self.assertIn('class', form.fields['customer_email'].widget.attrs)
        self.assertIn('class', form.fields['customer_phone'].widget.attrs)
