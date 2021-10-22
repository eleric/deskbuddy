from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, reverse
from datetime import datetime
from django.templatetags.static import static
from django.conf import settings
import os
from django.http import FileResponse, HttpResponse
import urllib.parse
import io
from deskbuddy.models import UserSettings
from deskbuddy.persistence import get_storage_obj
from PIL import Image, ImageFont, ImageDraw
from django.contrib.auth.models import User

storage = get_storage_obj()
user_name = 'eleric'
standard_height = 1000
font_size = 50


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='deskbuddy_user').exists())
def index(request):
    date_str = datetime.now().strftime('%I:%M:%S %p')

    context = {
        'time': date_str,
    }
    return render(request, 'deskbuddy/index.html', context)


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='deskbuddy_user').exists())
def photos(request):
    current_user = request.user
    print(f'User {current_user}')
    cwd = settings.PHOTO_ROOT
    user_settings = UserSettings.objects.get(name=user_name)
    paths = [reverse('photo', args=(urllib.parse.quote(storage.build_path(cwd, f), safe=''),)) for f in storage.list(cwd) if
             storage.is_file(storage.build_path(cwd, f))]
    names = [f for f in storage.list(cwd) if
             storage.is_file(storage.build_path(cwd, f))]
    context = {
        'path': paths,
        'photo_descr': names,
        'photo_frequency': user_settings.photo_frequency
               }
    return render(request, 'deskbuddy/photos.html', context)


def photo(request, path):
    current_user = request.user
    decoded_path = urllib.parse.unquote(path)
    img = storage.read(decoded_path)

    edited_img = render_photo(img, current_user)

    return HttpResponse(edited_img)


def render_photo(img, current_user=None):
    img = Image.open(img)
    old_size = img.size
    old_width = old_size[0]
    old_height = old_size[1]
    ratio = standard_height/old_height
    new_width = int(ratio * old_width)
    new_height = standard_height
    new_size = (new_width, new_height)
    img = img.resize(new_size)

    time_text = datetime.now().strftime("%I:%M%p")
    title_font = ImageFont.truetype('static/fonts/GeosansLight.ttf', font_size)
    image_editable = ImageDraw.Draw(img)
    image_editable.text((15, 15), time_text, fill=None, font=title_font)
    if current_user:
        image_editable.text((15, 100), str(current_user), fill=None, font=title_font)

    buf = io.BytesIO()
    img.save(buf, format='JPEG')

    b = buf.getvalue()

    return b