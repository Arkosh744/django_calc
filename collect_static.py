import os
print('Collecting static')
os.system('cmd /C python manage.py collectstatic --noinput')
print('done')