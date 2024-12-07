from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Load dummy data from an SQL file'

    def add_arguments(self, parser):
        parser.add_argument('sql_file', type=str, help='Path to the SQL file')

    def handle(self, *args, **kwargs):
        sql_file = kwargs['sql_file']
        with open(sql_file, 'r') as file:
            sql = file.read()
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded dummy data'))