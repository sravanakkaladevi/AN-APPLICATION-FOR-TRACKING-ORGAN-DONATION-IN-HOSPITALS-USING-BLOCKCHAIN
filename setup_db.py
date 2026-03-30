import pymysql

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='8309484956',
        port=3306
    )
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS organ_donation_db")
        print("Database 'organ_donation_db' created or already exists.")
    connection.commit()
    connection.close()
except Exception as e:
    print("Could not connect to MySQL. Ensure it is running on port 3306 without a password for root.")
    print(e)
