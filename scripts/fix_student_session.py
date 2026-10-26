import sqlite3

def run_migration():
    conn = sqlite3.connect('pytutor.db')
    cursor = conn.cursor()
    
    # 1. Update user_exercise_stars
    cursor.execute("""
        UPDATE user_exercise_stars 
        SET username = 'student' 
        WHERE username = 'stu_1791982087044_h6ifts'
    """)
    print(f"Updated user_exercise_stars: {cursor.rowcount} rows")
    
    # 2. Update user_achievements
    cursor.execute("""
        UPDATE user_achievements 
        SET username = 'student' 
        WHERE username = 'stu_1791982087044_h6ifts'
    """)
    print(f"Updated user_achievements: {cursor.rowcount} rows")
    
    # 3. Update submissions
    cursor.execute("""
        UPDATE submissions 
        SET session_id = 'student' 
        WHERE session_id = 'stu_1791982087044_h6ifts'
    """)
    print(f"Updated submissions: {cursor.rowcount} rows")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
