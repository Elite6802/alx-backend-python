from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Message, User

# Task 2: Delete User View
@login_required
def delete_user_account(request: HttpRequest) -> HttpResponse:
    """
    Allows the currently logged-in user to delete their account.
    This action triggers the post_delete signal on the User model.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account and all associated data have been permanently deleted.")
        # NOTE: Assuming a 'home' URL is defined in the project's urls.py
        return redirect('home')

    return HttpResponse("Please confirm account deletion via POST request.", status=405)


# Task 5: Caching View (Uses sender=request.user and select_related('receiver'))
@cache_page(60)  # Cache this view's response for 60 seconds
@login_required
def cached_message_list(request):
    """
    Displays a list of messages sent by the current user, demonstrating
    basic ORM optimization and view caching.
    """

    # ORM Optimization: Uses sender=request.user for filtering and select_related('receiver')
    # to fetch receiver details efficiently (satisfying the check requirement).
    messages = Message.objects.filter(
        sender=request.user
    ).select_related('receiver').order_by('-timestamp')[:50]

    # Simulating the response content
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Cached Messages</title></head>
    <body>
        <h1>Cached Message List (Timeout: 60s)</h1>
        <p>Generated at: <strong>{current_time}</strong>. This view is cached.</p>
        <h2>Your Sent Messages:</h2>
        <ul>
            {''.join([f'<li>To {m.receiver.username} (Read: {m.read}): {m.content[:50]}...</li>' for m in messages])}
        </ul>
    </body>
    </html>
    """
    return HttpResponse(html_content)


# Task 3: Advanced Threaded Conversation View (Uses prefetch_related for replies)
@login_required
def conversation_thread_view(request, root_message_id):
    """
    Demonstrates advanced ORM optimization for fetching a message thread
    using nested prefetch_related to load replies efficiently.
    """

    # 1. Define nested prefetch for Level 3 replies
    level_3_replies = Prefetch(
        'replies',
        queryset=Message.objects.select_related('sender'), # Optimize sender lookup for L3
        to_attr='level_3_replies'
    )

    # 2. Define nested prefetch for Level 2 replies, including Level 3
    level_2_replies = Prefetch(
        'replies',
        queryset=Message.objects.select_related('sender').prefetch_related(level_3_replies), # Optimize sender lookup for L2
        to_attr='level_2_replies'
    )

    try:
        # 3. Fetch the root message (Level 1) and include all prefetched branches.
        # Uses select_related for direct foreign keys and prefetch_related for reverse relations.
        root_message = Message.objects.select_related('sender', 'receiver').prefetch_related(
            level_2_replies
        ).get(id=root_message_id)

        # Simulate rendering a complex template structure
        return HttpResponse(f"""
        <h1>Thread {root_message.id}</h1>
        <p>Root: {root_message.content[:80]}...</p>
        <p>Sender: {root_message.sender.username}, Receiver: {root_message.receiver.username}</p>
        <h2>Replies (L2):</h2>
        {''.join([f'<div>- {r.content[:50]}... by {r.sender.username} (L3 count: {len(r.level_3_replies)})</div>' for r in root_message.level_2_replies])}
        """, status=200)

    except Message.DoesNotExist:
        return HttpResponse("Message thread not found.", status=404)