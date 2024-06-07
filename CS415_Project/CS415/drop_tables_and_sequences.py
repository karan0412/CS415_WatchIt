import subprocess

def drop_tables_in_loop(db_name='WatchIt', user='karan', host='localhost', port='5432'):
    tables = [
        "WatchIt_cinemahall", "WatchIt_movie", "WatchIt_showtime", "WatchIt_user", "WatchIt_booking",
        "WatchIt_seat", "WatchIt_booking_seats", "WatchIt_feedback", "WatchIt_tag", "WatchIt_movie_tags",
        "auth_group", "WatchIt_user_groups", "django_content_type", "auth_permission", "WatchIt_user_user_permissions",
        "auth_group_permissions", "django_admin_log", "django_migrations", "django_session"
    ]
    for table in tables:
        command = f'psql -U {user} -h {host} -p {port} -d {db_name} -c "DROP TABLE IF EXISTS \\"{table}\\" CASCADE;"'
        try:
            result = subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            print(f"Dropped table: {table}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error dropping table {table}: {e.stderr}")

drop_tables_in_loop()
