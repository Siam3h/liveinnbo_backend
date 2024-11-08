import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from .models import Transaction
from event.models import Event
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Process Payment View
@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    email = request.data.get('email')
    phone = request.data.get('phone')

    if not email or not phone:
        return Response({"message": "Email and phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

    amount = event.price * 100  # Paystack requires the amount in kobo
    transaction = Transaction.objects.create(
        email=email,
        phone=phone,
        amount=event.price,
        event=event
    )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": int(amount),
        "reference": transaction.ref,
        "callback_url": "https://yourdomain.com/payments/verify_payment/"
    }

    url = "https://api.paystack.co/transaction/initialize"
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data.get('status'):
        transaction.ref = response_data['data']['reference']
        transaction.save()
        return Response({"authorization_url": response_data['data']['authorization_url']}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Failed to initiate payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Verify Payment View
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_payment(request):
    ref = request.GET.get('reference')
    if not ref:
        return Response({"message": "No reference provided."}, status=status.HTTP_400_BAD_REQUEST)

    transaction = get_object_or_404(Transaction, ref=ref)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data.get('status') and response_data['data']['status'] == "success":
        transaction.verified = True
        transaction.save()

        event = transaction.event
        email = transaction.email

        # Send email with the event details
        subject = f"Your Event Ticket: {event.title}"
        message = render_to_string('payments/events_email.html', {
            'event': event,
            'transaction': transaction,
        })

        email_message = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        email_message.content_subtype = 'html'

        # Attach the receipt (if exists)
        if event.receipt:
            receipt_path = event.receipt.path
            if os.path.exists(receipt_path):
                email_message.attach_file(receipt_path)

        email_message.send()

        return Response({"message": "Payment verified successfully, ticket sent via email."}, status=status.HTTP_200_OK)

    return Response({"message": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

# Thank You View
@api_view(['GET'])
@permission_classes([AllowAny])
def thankyou(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, verified=True)
    event = transaction.event

    return Response({
        "message": "Thank you for your purchase!",
        "event_title": event.title,
        "event_date": event.date,
        "event_location": event.location
    }, status=status.HTTP_200_OK)
