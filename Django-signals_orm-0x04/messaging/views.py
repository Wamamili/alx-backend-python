from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User

# ✅ Send a message (sender=request.user, includes receiver)
@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')

        if not receiver_id or not content:
            return JsonResponse({'error': 'Receiver and content are required'}, status=400)

        message = Message.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content
        )
        return JsonResponse({
            'message': 'Message sent successfully',
            'data': {
                'id': message.id,
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'content': message.content,
                'timestamp': message.timestamp
            }
        }, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ✅ Retrieve all conversations for the logged-in user using select_related for optimization
@login_required
def get_conversations(request):
    messages = (
        Message.objects.filter(receiver=request.user)
        .select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )

    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'content': msg.content,
            'timestamp': msg.timestamp,
            'replies': [
                {
                    'id': reply.id,
                    'sender': reply.sender.username,
                    'content': reply.content,
                    'timestamp': reply.timestamp
                } for reply in msg.replies.all()
            ]
        })

    return JsonResponse({'conversations': data}, safe=False)


# ✅ Retrieve a single message thread (message + replies)
@login_required
def get_message_thread(request, message_id):
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').prefetch_related('replies'),
        id=message_id
    )

    thread_data = {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp,
        'replies': [
            {
                'id': reply.id,
                'sender': reply.sender.username,
                'receiver': reply.receiver.username,
                'content': reply.content,
                'timestamp': reply.timestamp
            } for reply in message.replies.all()
        ]
    }

    return JsonResponse(thread_data, safe=False)

@login_required
def unread_inbox(request):
    """Display only unread messages for the logged-in user."""
    # Using custom manager and .only() for optimization
    unread_messages = Message.unread.unread_for_user(request.user)

    context = {
        "unread_messages": unread_messages
    }
    return render(request, "messaging/unread_inbox.html", context)



@cache_page(60)  # Cache this view for 60 seconds
@login_required
def conversation_messages(request, username):
    """Display messages between the logged-in user and another user."""
    other_user = get_object_or_404(User, username=username)

    # Retrieve all messages between the two users
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    context = {
        'messages': messages,
        'other_user': other_user
    }

    return render(request, 'chats/conversation.html', context)
