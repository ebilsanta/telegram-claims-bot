import os
import mysql.connector
from mysql.connector import Error

def add_claim(username, date, description, amount):
	try:
		month = date[3:]
		day = date[:2]
		f_date = f"2022-{month}-{day}"
		connection = mysql.connector.connect(host=os.environ['DB_HOST'],
											database=os.environ['DB_DATABASE'],
											user=os.environ['DB_USERNAME'],
											password=os.environ['DB_PASSWORD'])
		cursor = connection.cursor()
		mySql_insert_query = """INSERT INTO claims (username, date, description, amount) 
							VALUES (%s, %s, %s, %s)"""
		record = (username, f_date, description, str(amount))
		cursor.execute(mySql_insert_query, record)
		connection.commit()
		connection.close()
		cursor.close()
		print("MySQL connection is closed")
		return "Claim has been added successfully"

	except mysql.connector.Error as error:
		return "Error adding claim, please check formatting!"

def get_claims(username):
	try:
		connection = mysql.connector.connect(host=os.environ['DB_HOST'],
											database=os.environ['DB_DATABASE'],
											user=os.environ['DB_USERNAME'],
											password=os.environ['DB_PASSWORD'])

		sql_select_Query = "select * from claims where username = %s"

		cursor = connection.cursor()
		cursor.execute(sql_select_Query, (username,))
		records = cursor.fetchall()
		print("Total number of rows in table: ", cursor.rowcount)

		print("\nPrinting each row")
		for row in records:
			print("username = ", row[0])
			print("date = ", row[1])
			print("claimId = ", row[2])
			print("description = ", row[3])
			print("amount = ", row[4], "\n")
		connection.close()
		cursor.close()
		print("MySQL connection is closed")
		return records

	except mysql.connector.Error as e:
		return "Error getting claims, please contact @ebilsanta for help"

def delete_claim(username, index):
	try:
		connection = mysql.connector.connect(host=os.environ['DB_HOST'],
											database=os.environ['DB_DATABASE'],
											user=os.environ['DB_USERNAME'],
											password=os.environ['DB_PASSWORD'])
		cursor = connection.cursor()
		sql_Delete_query = """DELETE FROM claims WHERE claimId = (
								SELECT max(claimId) FROM (
									SELECT claimId FROM claims WHERE username = %s LIMIT %s
									) as temp
								)"""

		cursor.execute(sql_Delete_query, (username, int(index),))
		connection.commit()
		connection.close()
		cursor.close()
		print("MySQL connection is closed")
		return "Claim removed successfully!"

	except mysql.connector.Error as error:
		return "Failed to delete claim, please check submitted number or contact @ebilsanta for help"

def clear_claims(username):
	try:
		connection = mysql.connector.connect(host=os.environ['DB_HOST'],
											database=os.environ['DB_DATABASE'],
											user=os.environ['DB_USERNAME'],
											password=os.environ['DB_PASSWORD'])
		cursor = connection.cursor()
		sql_Delete_query = "DELETE FROM claims WHERE username = %s"
		# row to delete
		cursor.execute(sql_Delete_query, (username,))
		connection.commit()
		print("Records Deleted successfully ")
		connection.close()
		cursor.close()
		print("MySQL connection is closed")

	except mysql.connector.Error as error:
		print("Failed to Delete record from table: {}".format(error))
