# myapp/views.py
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import qrcode
from io import BytesIO
from .serializers import UserRegistrationSerializer, TOTPDeviceSerializer
from rest_framework.permissions import AllowAny

class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate and store TOTP secret for the user
            totp_device = TOTPDevice.objects.create(user=user, confirmed=False)
            totp_device.save()

            # Build the URL for TOTP registration
            totp_registration_url = reverse('totp-registration', kwargs={'device_id': totp_device.id})
            registration_url = request.build_absolute_uri(totp_registration_url)

            # Send registration email
            subject = 'Welcome to My Website'
            message = f'Thank you for registering! Click the following link to complete TOTP registration: <a href="{registration_url}" style="color: blue;">{registration_url}</a>'
            from_email = 'febinaadhi@gmail.com'
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, html_message=message)

            return Response({'message': 'Registration successful. An email has been sent for verification.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TOTPRegistrationView(APIView):
    def get(self, request, device_id, *args, **kwargs):
        totp_device = get_object_or_404(TOTPDevice, id=device_id)
        totp_device.confirmed = True
        totp_device.save()

        # Generate QR code
        totp_url = totp_device.config_url
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        qr_code_image = buffer.getvalue()

        response = HttpResponse(qr_code_image, content_type="image/png")
        response['Content-Disposition'] = 'attachment; filename="qrcode.png"'
        return response


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        otp = request.data.get('otp')

        user = get_user_model().objects.filter(username=username).first()

        if user is not None and user.check_password(password):
            # Check OTP
            totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

            if totp_device and totp_device.verify_token(otp):
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                return Response({'message': 'Login successful', 'access_token': access_token}, status=status.HTTP_200_OK)

            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


