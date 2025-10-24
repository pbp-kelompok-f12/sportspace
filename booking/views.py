from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import datetime, date, time, timedelta
import json
import pytz

from .models import Venue, Booking
from .forms import BookingForm, BookingUpdateForm

@login_required
def venue_booking(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Get Jakarta timezone
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    now = timezone.now().astimezone(jakarta_tz)
    selected_date = request.GET.get('date', now.date().strftime('%Y-%m-%d'))
    
    # Generate time slots from 10:00 to 22:00
    time_slots = []
    current_time = now.time()
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    is_today = selected_date_obj == now.date()
    
    for hour in range(10, 22):
        start_time = time(hour, 0)
        end_time = time(hour + 1, 0)
        
        # Check if time slot is in the past (only for today)
        is_past_time = is_today and start_time <= current_time
        
        time_slots.append({
            'start': start_time,
            'end': end_time,
            'display': f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}",
            'is_past': is_past_time
        })
    
    # Get existing bookings for the selected date
    existing_bookings = Booking.objects.filter(
        venue=venue,
        booking_date=selected_date
    ).values_list('start_time', flat=True)
    
    # Mark time slots as booked or past
    for slot in time_slots:
        slot['is_booked'] = slot['start'] in existing_bookings
        slot['is_unavailable'] = slot['is_booked'] or slot['is_past']
    
    # Generate next 7 days for date selection
    today = now.date()
    date_options = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        date_options.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'display': current_date.strftime('%d %b'),
            'is_today': i == 0
        })
    
    context = {
        'venue': venue,
        'time_slots': time_slots,
        'selected_date': selected_date,
        'date_options': date_options,
        'now': now,
    }
    return render(request, 'booking/venue_booking.html', context)

@login_required
def my_bookings(request):
    # Get Jakarta timezone
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    now = timezone.now().astimezone(jakarta_tz)
    today = now.date()
    current_time = now.time()
    filter_type = request.GET.get('filter', 'all')
    
    bookings = Booking.objects.filter(user=request.user)
    
    if filter_type == 'active':
        # Active bookings: future dates OR today with future times
        bookings = bookings.filter(
            models.Q(booking_date__gt=today) | 
            models.Q(booking_date=today, start_time__gt=current_time)
        )
    elif filter_type == 'past':
        # Past bookings: past dates OR today with past times
        bookings = bookings.filter(
            models.Q(booking_date__lt=today) | 
            models.Q(booking_date=today, start_time__lte=current_time)
        )
    
    bookings = bookings.order_by('-booking_date', '-start_time')
    
    # Add is_past flag to each booking for template
    for booking in bookings:
        booking.is_past = (
            booking.booking_date < today or 
            (booking.booking_date == today and booking.start_time <= current_time)
        )
    
    context = {
        'bookings': bookings,
        'filter_type': filter_type,
        'now': now,
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
        
        # Create form instance with data
        form_data = {
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'booking_date': booking_date,
            'start_time': start_time,
            'end_time': end_time,
        }
        
        form = BookingForm(data=form_data)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.venue = venue
            booking.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Booking Created!',
                'booking_id': str(booking.id)
            })
        else:
            # Return form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors[0] if field_errors else ''
            return JsonResponse({'success': False, 'message': 'Validation failed', 'errors': errors})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    except:
        return JsonResponse({'success': False, 'message': 'Booking not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Create form instance with current booking data and new data
        form_data = {
            'customer_name': data.get('customer_name', booking.customer_name),
            'customer_email': data.get('customer_email', booking.customer_email),
            'customer_phone': data.get('customer_phone', booking.customer_phone),
        }
        
        form = BookingUpdateForm(data=form_data, instance=booking)
        
        if form.is_valid():
            form.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking Updated!'
            })
        else:
            # Return form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors[0] if field_errors else ''
            return JsonResponse({'success': False, 'message': 'Validation failed', 'errors': errors})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    except:
        return JsonResponse({'success': False, 'message': 'Booking not found'}, status=404)
    
    try:
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