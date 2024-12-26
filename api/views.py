import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from authentication.models import SpamReport, Contact
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Case, When, IntegerField

logger = logging.getLogger(__name__)

CustomUser = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def mark_spam(request):
    auth_header = request.headers.get("Authorization", None)

    if auth_header is None:
        logger.warning("Authorization header missing.")
        return Response(
            {"error": "Authorization header missing"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        token = auth_header.split(" ")[1]
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)

        phone_number = request.data.get("phone_number")
        
        if not phone_number:
            logger.warning("Phone number not provided.")
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        spam_report = SpamReport.objects.create(
            reported_by=user, 
            phone_number=phone_number
        )
        logger.info(f"Spam report created for phone number: {phone_number} by user {user.username}")

        return Response(
            {"message": f"Spam report for {phone_number} created successfully."},
            status=status.HTTP_201_CREATED,
        )
    
    except IndexError:
        logger.error("Invalid token format.")
        return Response(
            {"error": "Invalid token format."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as e:
        logger.exception("Error occurred in mark_spam view.")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def search_by_name(request):
    query = request.GET.get('name', None)
    
    if not query:
        logger.warning("Name query parameter missing.")
        return Response(
            {"error": "Name query parameter is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    custom_users = CustomUser.objects.filter(name__icontains=query).order_by(
        Case(
            When(name__istartswith=query, then=0),
            default=1,
            output_field=IntegerField(),
        ),
        'name'
    )
    
    contacts = Contact.objects.filter(name__icontains=query).order_by(
        Case(
            When(name__istartswith=query, then=0),
            default=1,
            output_field=IntegerField(),
        ),
        'name'
    )

    results = []
    for user in custom_users:
        spam_likelihood = "Unknown"  
        if SpamReport.objects.filter(phone_number=user.phone_number).exists():
            spam_likelihood = "Spam"
        results.append({
            "name": user.name,
            "phone_number": user.phone_number,
            "spam_likelihood": spam_likelihood
        })

    for contact in contacts:
        spam_likelihood = "Unknown"  
        if SpamReport.objects.filter(phone_number=contact.phone_number).exists():
            spam_likelihood = "Spam"
        results.append({
            "name": contact.name,
            "phone_number": contact.phone_number,
            "spam_likelihood": spam_likelihood
        })

    logger.info(f"Search results for name query '{query}': {len(results)} results found.")
    
    return Response({"results": results}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_number(request):
    phone_number = request.query_params.get('phone_number', None)
    
    if not phone_number:
        logger.warning("Phone number query parameter missing.")
        return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if user:
        logger.info(f"User found for phone number: {phone_number}")
        return Response({
            "message": "User found.",
            "name": user.name,
            "phone_number": user.phone_number
        }, status=status.HTTP_200_OK)

    contacts = Contact.objects.filter(phone_number=phone_number)
    if contacts.exists():
        contact_results = [{"name": contact.name, "phone_number": contact.phone_number} for contact in contacts]
        logger.info(f"Contacts found for phone number: {phone_number}")
        return Response({
            "message": "Contacts found.",
            "results": contact_results
        }, status=status.HTTP_200_OK)

    logger.warning(f"No results found for phone number: {phone_number}")
    return Response({"message": "No results found for this phone number."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spam_counter(request):
    phone_number = request.query_params.get('phone_number', None)
    
    if not phone_number:
        logger.warning("Phone number query parameter missing.")
        return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    spam_count = SpamReport.objects.filter(phone_number=phone_number).count()
    logger.info(f"Spam report count for phone number {phone_number}: {spam_count}")

    if spam_count > 0:
        return Response({
            "message": f"{spam_count} spam reports found for this phone number.",
            "spam_count": spam_count
        }, status=status.HTTP_200_OK)
    
    return Response({
        "message": "No spam reports found for this phone number."
    }, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_detail(request):
    phone_number = request.query_params.get('phone_number', None)
    
    if not phone_number:
        logger.warning("Phone number query parameter missing.")
        return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        logger.info(f"User details found for phone number: {phone_number}")
    except CustomUser.DoesNotExist:
        user = None
        logger.warning(f"No user found for phone number: {phone_number}")

    spam_count = SpamReport.objects.filter(phone_number=phone_number).count()

    response_data = {
        "phone_number": phone_number,
        "spam_likelihood": spam_count,
    }

    if user:
        current_user = request.user  
        is_contact = Contact.objects.filter(user=current_user, phone_number=phone_number).exists()

        response_data["name"] = user.name
        if is_contact:
            response_data["email"] = user.email  
        else:
            response_data["email"] = None  

    logger.info(f"Details response for phone number {phone_number}: {response_data}")
    
    return Response(response_data, status=status.HTTP_200_OK)
