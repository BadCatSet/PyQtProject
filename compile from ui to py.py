import os

names = ['admin', 'admin_item', 'item', 'login', 'main_page', 'new_var', 'signin']

for i in names:
    os.system(f'pyuic5 _{i}.ui -o __{i}.py')
