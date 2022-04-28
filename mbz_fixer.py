from argparse import ArgumentParser
import tarfile
import shutil
import tempfile
import csv
import os
import pathlib
import xml.etree.ElementTree as ET

def parse_csv(usercsv):
    usermap = {}
    with open(usercsv, 'r', newline='') as usermap_f:
        usermap_reader = csv.reader(usermap_f)
        for row in usermap_reader:
            usermap[row[0]] = row[1]
    return usermap


def fix_xml(users_xml, usermap):
    users_tree = ET.parse(users_xml)
    users_root = users_tree.getroot()

    for user in users_root.findall('user'):
        username = user.find('username').text
        if username in usermap:
            email_node = user.find('email')
            old_email = email_node.text
            email_node.text = usermap[username]
            print('Updated user %s: email changed from %s to %s' %
                  (username, old_email, email_node.text)
            )

    users_tree.write(users_xml)



def fix_mbz(usercsv, backupfile):
    """
    Replace email addresses in an .mbz backup with the correct email addresses
    given in a CSV.

    usercsv    -- path to a CSV with two columns. The first column is a username,
                  and the second column is a email address.
    backupfile -- path to an .mbz file
    """
    usermap = parse_csv(usercsv)

    temp_dir = tempfile.mkdtemp()

    try:
        mbz_noext = pathlib.Path(backupfile).stem
        temp_tgz = os.path.join(temp_dir, mbz_noext + '.tar.gz')
        temp_tar = os.path.join(temp_dir, mbz_noext + '.tar')

        shutil.copy(backupfile, temp_tgz)

        # We need a plain .tar in order to append files. Doing this in Python
        # put me in encoding hell, so I gave up and used gunzip.
        os.system('gunzip ' + temp_tgz)

        with tarfile.open(temp_tar, 'r') as mb:
            try:
                users_xml = mb.getmember('users.xml')
            except KeyError as e:
                raise Exception('users.xml could not be found in the .mbz file.')

            mb.extract(users_xml, path=temp_dir)

        users_xml = os.path.join(temp_dir, 'users.xml')
        fix_xml(users_xml, usermap)

        # Apparently Python tarfile can't delete files from the archive. At
        # this point it may be best to just use CLI tar for everything
        os.system('tar -vf ' + temp_tar + ' --delete users.xml')

        with tarfile.open(temp_tar, 'a') as mb:
            mb.add(users_xml, 'users.xml')

        # Zip it back up and overwrite the original.
        os.system('gzip ' + temp_tar)
        os.remove(backupfile)
        shutil.copy(temp_tgz, backupfile)

    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    parser = ArgumentParser(description="""
        Tool for updating user information in .mbz files. Original files will
        be overwritten.
    """)

    parser.add_argument(
        '--usercsv', '-c', required=True, type=str, help="CSV file with NO headers and two columns containing usernames and email addresses"
    )

    parser.add_argument(
        '--backupfile', '-b', required=True, type=str, help="Moodle backup to fix"
    )

    # parser.add_argument(
    #     '--no-preserve-original', '-n', default=False, action='store_true', help="Replace the original .mbz instead of making a copy."
    # )

    fix_mbz(**vars(parser.parse_args()))
