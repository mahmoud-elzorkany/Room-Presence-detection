from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from .models import Room, Record
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from Crypto.Cipher import AES
import base64

@csrf_protect
def index(request):    
    room_list = Room.objects.order_by('-name')
    context = {'room_list': room_list}
    return render(request, 'detection/index.html', context)

@csrf_protect
def detail(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    records = room.record_set.all().order_by('-date_start')
    context = {'room': room, 'records' : records}
    return render(request, 'detection/detail.html', context)

@csrf_protect
def update_room(request):
    if request.method == "POST":
        cryptkey = request.POST['csrfmiddlewaretoken']
        cipher = AES.new(cryptkey[:32],AES.MODE_ECB)
        decoded_username = cipher.decrypt(base64.b64decode(request.POST['username']))[10:]
        decoded_password = cipher.decrypt(base64.b64decode(request.POST['password']))[2:]
        if decoded_username == b'update' and decoded_password == b'updatepassword':
            room_name = request.POST['room_name']
            status = request.POST['room_status']
            room = get_object_or_404(Room, name=room_name)
            if status == "True":
                room.occupied = True
                print("Room %s occupied"%(room_name))
            else:
                room.occupied = False
                print("Room %s freed"%(room_name))
            if status == "False":
                date_occupied = request.POST['date_occupied']
                date_freed = request.POST['date_freed']
                record = Record(room_record = room, date_start = date_occupied, date_end = date_freed)
                record.save()
                print("%s created"%(record))
            room.save()
            room_list = Room.objects.order_by('-name')
            context = {'room_list': room_list}
            
            return render(request, 'detection/index.html', context)
        else:
            return HttpResponseForbidden()

    if request.method == "GET":
        context = {}
        return render(request, 'detection/update.html', context)