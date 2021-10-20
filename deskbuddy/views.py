from django.shortcuts import render, reverse
from datetime import datetime
from django.templatetags.static import static
from django.conf import settings
import os
from django.http import FileResponse
import urllib.parse

from deskbuddy.persistence import get_storage_obj

storage = get_storage_obj()


def index(request):
    date_str = datetime.now().strftime('%I:%M:%S %p')

    context = {
        'time': date_str,
    }
    return render(request, 'deskbuddy/index.html', context)


def photos(request):
    cwd = settings.PHOTO_ROOT
    # paths = [reverse('photo', args=(os.path.join(cwd, f),)) for f in os.listdir(cwd) if
    paths = [reverse('photo', args=(urllib.parse.quote(storage.build_path(cwd, f), safe=''),)) for f in storage.list(cwd) if
             # os.path.isfile(os.path.join(cwd, f))]
             storage.is_file(storage.build_path(cwd, f))]
    names = [f for f in storage.list(cwd) if
            # os.path.isfile(os.path.join(cwd, f))]
             storage.is_file(storage.build_path(cwd, f))]
    context = {
        'path': paths,
        'photo_descr': names
               }
    return render(request, 'deskbuddy/photos.html', context)


def photo(request, path):
    decoded_path = urllib.parse.unquote(path)
    img = storage.read(decoded_path)

    response = FileResponse(img)

    return response
