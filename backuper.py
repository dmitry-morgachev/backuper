# -*- coding: utf-8 -*-

import os
import sys
import datetime

import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError


PROJECT_NAME = os.environ["PROJECT_NAME"]
DROPBOX_TOKEN = os.environ["TOKEN"]

LOCAL_FILE = 'backup.7z'
BACKUP_PATH = '/{}/backup_{}.7z'.format(
    PROJECT_NAME,
    datetime.datetime.now().strftime('%d-%m-%Y')
)


def backup():
    with open(LOCAL_FILE, 'rb') as f:
        print(f"Uploading {LOCAL_FILE} to Dropbox as {BACKUP_PATH}...")
        try:
            dbx.files_upload(
                f.read(),
                BACKUP_PATH,
                mode=WriteMode('overwrite')
            )
        except ApiError as err:
            if err.error.is_path() and\
                    err.error.get_path().reason.is_insufficient_space():
                files = dbx.files_list_folder(
                    '/{}'.format(PROJECT_NAME)
                )
                # тут попытка найти самый старый бэкап в облаке, удалить его и перезалить новый
                oldest_file = sorted(
                    files.entries,
                    key=lambda entry: entry.server_modified
                )[0]
                print(f'Insufficient space. Delete oldest backup: {oldest_file}')
                dbx.files_delete(oldest_file.path_display)
                print('Reupload latest backup')
                backup()
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()


def remove():
    new_date = datetime.datetime.now()
    delta = datetime.timedelta(days=20)
    old_date = new_date - delta
    old_file_path = '/backup_{}'.format(old_date.strftime('%d-%m-%Y'))

    try:
        dbx.files_delete(old_file_path)
    except ApiError as err:
        if err.error.is_path_lookup() and err.error.get_path_lookup().not_found.is_not_found():
            print('Old backup file from {} not found'.format(old_date.strftime('%d-%m-%Y')))
        elif err.user_message_text:
            print(err.user_message_text)
        else:
            print(err)


if __name__ == '__main__':
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    try:
        dbx.users_get_current_account()
    except AuthError:
        sys.exit("ERROR: Invalid access token")

    backup()
    remove()
