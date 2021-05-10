from flask_mysqldb import MySQL
import MySQLdb.cursors


def get_review_stat(mysql):
    """
    Return count of total reviews and true reviews.
    """
    # Check if reviews exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT count(id) as c FROM reviews')
    # Fetch one record
    total_reviews_count = cursor.fetchone()['c']
    # Check if true reviews exists using MySQL
    cursor.execute('SELECT count(id) as c FROM reviews WHERE `label` = true')
    # Fetch one record
    true_reviews_count = cursor.fetchone()['c']
    return total_reviews_count, true_reviews_count

def insert_review(mysql,review_content, label):
    """
    Insert one review into database.
    """
    # Check if reviews exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Insert a review
    cursor.execute('INSERT INTO reviews (`review_content`,`label`) VALUES (%s, %b)', (review_content,label))
    mysql.connection.commit()