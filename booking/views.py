from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date, time
import json

from .models import Venue, Booking
from .forms import BookingForm, BookingUpdateForm

@login_required
def venue_booking(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    
    # Generate time slots from 10:00 to 22:00
    time_slots = []
    for hour in range(10, 22):
        start_time = time(hour, 0)
        end_time = time(hour + 1, 0)
        time_slots.append({
            'start': start_time,
            'end': end_time,
            'display': f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        })
    
    # Get existing bookings for the selected date
    existing_bookings = Booking.objects.filter(
        venue=venue,
        booking_date=selected_date
    ).values_list('start_time', flat=True)
    
    # Mark time slots as booked
    for slot in time_slots:
        slot['is_booked'] = slot['start'] in existing_bookings
    
    context = {
        'venue': venue,
        'time_slots': time_slots,
        'selected_date': selected_date,
    }
    return render(request, 'booking/venue_booking.html', context)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'bookings': bookings,
    }
    return render(request, 'booking/my_bookings.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_booking(request):
    try:
        data = json.loads(request.body)
        venue_id = data.get('venue_id')
        booking_date = data.get('booking_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        
        venue = get_object_or_404(Venue, id=venue_id)
        
        # Check if time slot is already booked
        existing_booking = Booking.objects.filter(
            venue=venue,
            booking_date=booking_date,
            start_time=start_time
        ).exists()
        
        if existing_booking:
            return JsonResponse({'success': False, 'message': 'This time slot is already booked'})
        
        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            venue=venue,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Booking Created!',
            'booking_id': str(booking.id)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        data = json.loads(request.body)
        
        booking.customer_name = data.get('customer_name', booking.customer_name)
        booking.customer_email = data.get('customer_email', booking.customer_email)
        booking.customer_phone = data.get('customer_phone', booking.customer_phone)
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Booking Updated!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Booking Deleted!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def sync_venue(request):
    """Sync venue from home app to booking app"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        location = data.get('location')
        address = data.get('address')
        image_url = data.get('image_url')
        
        if not name or not address:
            return JsonResponse({
                'success': False,
                'message': 'Name and address are required'
            })
        
        # Create or get existing venue
        venue, created = Venue.objects.get_or_create(
            name=name,
            defaults={
                'location': location or 'Unknown',
                'address': address,
                'image_url': image_url,
                'description': f'Padel court located at {address}'
            }
        )
        
        return JsonResponse({
            'success': True,
            'venue_id': str(venue.id),
            'message': 'Venue synced successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})