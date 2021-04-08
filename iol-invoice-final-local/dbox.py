#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dropbox

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)

def main():
    access_token = 'sl.AuDzGV7kpNnJA5gepSbNkvTyibXXMh8w_x6vQSuX1NeYn1UEeWlng5j9tuMGrd6hpvipGyfa47_WykodFtZIcRBYVqqHbs_8cQK8eyfYIhRfRmRQHHu4uaIQW-L81CTd6Kn77mwb'
    transferData = TransferData(access_token)

    file_from = 'test.txt'
    file_to = '/test_dropbox/test.txt'  # The full path to upload the file to, including the file name
    dbx = dropbox.Dropbox(access_token)
    # API v2
    transferData.upload_file(file_from, file_to)
    
    result = dbx.files_get_temporary_link(file_to)

    print(result.link)

if __name__ == '__main__':
    main()