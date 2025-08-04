from rest_framework import generics, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomLoginSerializer
from rest_framework import status as http_status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from .models import CustomUser, PasswordResetToken
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .tasks import send_reset_email_task
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View




class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "message": "Registration failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer



class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return Response({
                "status": "success",
                "message": "Token refreshed successfully.",
                "access_token": response.data.get("access")
            }, status=http_status.HTTP_200_OK)

        except AuthenticationFailed as e:
            # Catch token errors like "token_not_valid"
            return Response({
                "status": "error",
                "message": "Refresh token is invalid or expired.",
                "details": str(e.detail)
            }, status=http_status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong while refreshing the token.",
                "details": str(e)
            }, status=http_status.HTTP_400_BAD_REQUEST)
        


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
                reset_link = f"http://127.0.0.1:8000/reset-password/{token.token}/"

                send_reset_email_task.delay(email, reset_link)
                return Response({
                    "status": "success",
                    "message": "Password reset link sent to your email."
                }, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "No user found with this email."
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, token):
        serializer = PasswordResetConfirmSerializer(data={**request.data, 'token': token})
        if serializer.is_valid():
            token_obj = get_object_or_404(PasswordResetToken, token=token)

            if not token_obj.is_valid():
                return Response({
                    "status": "error",
                    "message": "Token is expired or already used."
                }, status=status.HTTP_400_BAD_REQUEST)

            user = token_obj.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            token_obj.mark_used()

            return Response({
                "status": "success",
                "message": "Password has been reset successfully."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordHTMLView(View):
    def get(self, request, token):
        token_obj = PasswordResetToken.objects.filter(token=token, used=False).first()
        if not token_obj or not token_obj.is_valid():
            return render(request, 'users/reset_password.html', {"error": "Invalid or expired token."})

        return render(request, 'users/reset_password.html')

    def post(self, request, token):
        new_password = request.POST.get("new_password")
        token_obj = PasswordResetToken.objects.filter(token=token, used=False).first()

        if not token_obj or not token_obj.is_valid():
            return render(request, 'users/reset_password.html', {"error": "Token is invalid or expired."})

        user = token_obj.user
        user.set_password(new_password)
        user.save()
        token_obj.mark_used()

        return render(request, 'users/reset_password.html', {"success": "Password has been reset successfully."})