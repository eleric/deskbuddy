import os
from django.conf import settings
from django.core.files.base import ContentFile
import boto3
import logging
import io

STORAGE_TYPE = 'STORAGE_TYPE'
STORAGE_TYPE_LOCAL = 'local'
STORAGE_TYPE_S3 = 's3'
STORAGE_TYPES = (STORAGE_TYPE_S3, STORAGE_TYPE_LOCAL)
ACCESS_KEY = 'ACCESS_KEY'
SECRET_ACCESS_KEY = 'SECRET_ACCESS_KEY'
REGION_NAME = 'REGION_NAME'
BUCKET_NAME = 'BUCKET_NAME'


def get_access_key():
    access_key_id = os.getenv(ACCESS_KEY)

    if access_key_id is None:
        raise EnvironmentError(f'No access_key_id environment variable set for {ACCESS_KEY}')

    access_key_id = access_key_id.strip().strip("'").strip('"')

    return access_key_id


def get_secret_access_key():
    secret_access_key = os.getenv(SECRET_ACCESS_KEY)

    if secret_access_key is None:
        raise EnvironmentError(f'No secret_access_key_id environment variable set for {SECRET_ACCESS_KEY}')

    secret_access_key = secret_access_key.strip().strip("'").strip('"')

    return secret_access_key


def get_region_name():
    region_name = os.getenv(REGION_NAME)

    if region_name is None:
        raise EnvironmentError(f'No region name environment variable set for {REGION_NAME}')

    region_name = region_name.strip().strip("'").strip('"')

    return region_name


def get_bucket_name():
    bucket_name = os.getenv(BUCKET_NAME)

    if bucket_name is None:
        raise EnvironmentError(f'No bucket name environment variable set for {BUCKET_NAME}')

    bucket_name = bucket_name.strip().strip("'").strip('"')

    return bucket_name


def get_storage_type():
    storage_type = os.getenv(STORAGE_TYPE)

    if storage_type is None:
        raise EnvironmentError(f'No storage type environment variable set for {STORAGE_TYPE}')

    storage_type = storage_type.strip().strip("'").strip('"')

    if any(storage_type == s for s in STORAGE_TYPES):
        return storage_type
    else:
        raise EnvironmentError(f'Storage type environment variable {STORAGE_TYPE} set to invalid types {storage_type}.'
                               f'  Valid types: {STORAGE_TYPES}')


def get_storage_obj():
    storage_type = get_storage_type()
    if storage_type == STORAGE_TYPE_LOCAL:
        return LocalStorage()
    if storage_type == STORAGE_TYPE_S3:
        return S3Storage(get_access_key(), get_secret_access_key(), get_region_name(), get_bucket_name())


class Storage:
    def __init__(self):
        pass

    def save(self, file, name):
        raise NotImplementedError

    def delete(self, name):
        raise NotImplementedError

    def list(self, path):
        raise NotImplementedError

    def is_file(self, path):
        raise NotImplementedError

    def read(self, path):
        raise NotImplementedError

    def build_path(self, path, file):
        raise NotImplementedError

    def build_long_path(self, path, file):
        raise NotImplementedError


class LocalStorage(Storage):
    def __init__(self):
        pass

    def save(self, file, name):
        path = self.build_path(settings.PHOTO_ROOT, name)

        fout = open(path, 'wb+')

        file_content = ContentFile(file.read())

        # Iterate through the chunks.
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()

    def delete(self, name):
        path = self.build_path(settings.PHOTO_ROOT, name)
        print(path)
        os.remove(path)

    def list(self, path):
        return os.listdir(path)

    def is_file(self, path):
        return os.path.isfile(os.path.join(path))

    def read(self, path):
        return open(path, 'rb')

    def build_path(self, path, file):
        return os.path.join(path, file)

    def build_long_path(self, path, file):
        return os.path.join(path, file)


class S3Storage(Storage):
    def __init__(self, access_key_id, secret_access_key, region_name, bucket_name):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.bucket_name = bucket_name
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name
        )
        self.resource = boto3.resource(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name
        )

    def save(self, file, name):
        path = self.build_long_path(settings.PHOTO_ROOT, name)

        self.client.upload_fileobj(file, self.bucket_name, path)

    def delete(self, name):
        path = self.build_long_path(settings.PHOTO_ROOT, name)
        # os.remove(path)
        self.client.delete_object(Bucket=self.bucket_name, Key=path)

    def list(self, path):
        keys = [obj['Key'] for obj in self.client.list_objects(Bucket=self.bucket_name, Prefix=path)['Contents']]
        print(f'List - {keys}')
        return keys

    def is_file(self, path):
        obj = self.resource.Object(self.bucket_name, path)
        content_type = obj.get()['ContentType']
        if content_type is None:
            return False
        return 'application/x-directory' not in content_type

    def read(self, path):
        obj = self.resource.Object(self.bucket_name, path)
        data = obj.get()['Body'].read()
        file = io.BytesIO(data)
        return file

    def build_path(self, path, file):
        return file

    def build_long_path(self, path, file):
        return '/'.join([path, file])
