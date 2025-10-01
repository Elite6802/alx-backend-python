from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from .models import Message

# Simple view to handle user account deletion
@login_required
def delete_user_account(request: HttpRequest) -> HttpResponse:
    """
    Allows the currently logged-in user to delete their account.
    This action triggers the post_delete signal on the User model.
    """
    if request.method == 'POST':
        user = request.user

        # 1. Log out the user immediately
        logout(request)

        # 2. Delete the user object (This triggers the post_delete signal)
        user.delete()

        # 3. Provide feedback and redirect
        messages.success(request, "Your account and all associated data have been permanently deleted.")
        return redirect('home') # Redirect to a safe, unauthenticated page

    # If not POST, you might render a confirmation page (not required by the prompt)
    return HttpResponse("Please confirm account deletion via POST request.", status=405)


@login_required
def unread_inbox_view(request):
    """
    Displays only the unread messages for the currently logged-in user.
    Uses the custom manager and .only() optimization.
    """
    user = request.user

    unread_messages = Message.unread.for_user(user)

    context = {
        'unread_messages': unread_messages,
        'user': user,
    }
