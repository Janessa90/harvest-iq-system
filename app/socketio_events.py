from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from datetime import datetime


@socketio.on('connect')
def handle_connect():
    """User connects to websocket."""
    if current_user.is_authenticated:
        print(f'User {current_user.username} connected')


@socketio.on('disconnect')
def handle_disconnect():
    """User disconnects from websocket."""
    if current_user.is_authenticated:
        print(f'User {current_user.username} disconnected')


@socketio.on('join_conversation')
def handle_join_conversation(data):
    """User joins a conversation room."""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        room = f'conversation_{conversation_id}'
        join_room(room)
        print(f'User {current_user.username} joined {room}')


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """User leaves a conversation room."""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        room = f'conversation_{conversation_id}'
        leave_room(room)
        print(f'User {current_user.username} left {room}')
@socketio.on('typing')
def handle_typing(data):
    """Broadcast typing indicator."""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing', False)
    
    if conversation_id:
        room = f'conversation_{conversation_id}'
        emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.full_name or current_user.username,
            'is_typing': is_typing
        }, room=room, include_self=False)