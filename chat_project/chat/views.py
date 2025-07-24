from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message, CustomUser

# --------------------------- Signup View ---------------------------
def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        user = CustomUser.objects.create_user(email=email, name=name, password=password)
        user.save()
        messages.success(request, "Account created.")
        return redirect('login')
    return render(request, 'signup.html')

# --------------------------- Login View ----------------------------
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'registration/login.html')

# --------------------------- Logout View ---------------------------
def logout_view(request):
    logout(request)
    return redirect('login')

# --------------------------- Dashboard View ------------------------
@login_required
def dashboard(request):
    rooms = request.user.chatrooms.all()
    users = CustomUser.objects.exclude(id=request.user.id)

    room_display = []
    for room in rooms:
        if room.is_group:
            display_name = room.name
        else:
            other_user = room.members.exclude(id=request.user.id).first()
            display_name = f"Private Chat with {other_user.name}" if other_user else "Private Chat"

        room_display.append({
            'id': room.id,
            'name': display_name,
            'is_group': room.is_group,
        })

    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        members = request.POST.getlist('members')

        group = ChatRoom.objects.create(name=group_name, is_group=True)
        group.members.add(request.user)
        for member_id in members:
            member = CustomUser.objects.get(id=member_id)
            group.members.add(member)
        return redirect('chat_room', room_id=group.id)

    return render(request, 'chat/dashboard.html', {
        'rooms': room_display,
        'users': users
    })

# ----------------------- Start Private Chat ------------------------
@login_required
def start_private_chat(request, user_id):
    other_user = CustomUser.objects.get(id=user_id)
    existing_room = ChatRoom.objects.filter(
        is_group=False, members=request.user
    ).filter(members=other_user).first()

    if existing_room:
        return redirect('chat_room', room_id=existing_room.id)

    room = ChatRoom.objects.create(is_group=False)
    room.members.add(request.user, other_user)
    return redirect('chat_room', room_id=room.id)

# ------------------------- Chat Room View --------------------------
@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user not in room.members.all():
        return HttpResponseForbidden("You are not a member of this room.")

    messages_list = Message.objects.filter(room=room).order_by('timestamp')

    if room.is_group:
        display_name = room.name
    else:
        other_member = room.members.exclude(id=request.user.id).first()
        display_name = other_member.name if other_member else "Private Chat"

    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': messages_list,
        'display_name': display_name,
    })

# --------------------------- Send Message --------------------------
@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        room = ChatRoom.objects.get(id=room_id)
        content = request.POST.get('content', '')
        file = request.FILES.get('file')
        Message.objects.create(room=room, sender=request.user, content=content, file=file)
        return redirect('chat_room', room_id=room.id)
