# mbz-email-fix

Moodle course restores occasionally fail with a message like `Trying to restore user '<username>' from backup will cause conflict`. This occurs when there is a mismatch between the user's email address in the .mbz and the email address on the target site.

This script unpacks an .mbz, extracts the users.xml file, and updates email addresses according to a provided CSV.

### Requirements
- Python >= 3.6

### Usage
`python mbz_fixer.py -c user_map.csv -b backup.mbz` 
where `user_map.csv` is a headerless CSV file with a username and email column (in that order).

or `python mbz_fixer.py -h` for usage info.

