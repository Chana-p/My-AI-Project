"""
הפעלת השרת עם הגדרות נוחות
"""
import os
from dotenv import load_dotenv
from app import app

# טעינת משתני סביבה
load_dotenv()

def main():
    """הפעלת השרת"""
    print("🚀 מפעיל את dovrotAI...")
    print("📱 הממשק יהיה זמין בכתובת: http://localhost:5000")
    
    # בדיקת מפתח OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  אזהרה: לא נמצא מפתח OpenAI API")
        print("   אנא צור קובץ .env עם המפתח:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print()
    
    # הוספת כמה משימות לדוגמה
    from todo_service import todo_service, TaskType
    from datetime import datetime, timedelta
    
    if len(todo_service.get_tasks()) == 0:
        print("📝 מוסיף משימות לדוגמה...")
        
        todo_service.add_task(
            title="סיום דוח חודשי",
            description="הכנת דוח ביצועים לחודש שעבר",
            task_type=TaskType.WORK,
            end_date=datetime.now() + timedelta(days=3)
        )
        
        todo_service.add_task(
            title="קניות לסוף השבוע",
            description="רכישת מצרכים ומוצרי ניקיון",
            task_type=TaskType.PERSONAL,
            end_date=datetime.now() + timedelta(days=1)
        )
        
        todo_service.add_task(
            title="תיקון באג בייצור",
            description="פתרון בעיה קריטית במערכת התשלומים",
            task_type=TaskType.URGENT,
            end_date=datetime.now() + timedelta(hours=6)
        )
        
        print("✅ נוספו 3 משימות לדוגמה")
    
    print("\n" + "="*50)
    print("💡 דוגמאות לשאילתות שאתה יכול לנסות:")
    print("   • הראה לי את כל המשימות שלי")
    print("   • הוסף משימה חדשה: 'פגישה עם לקוח' מסוג עבודה")
    print("   • מה המשימות הדחופות שלי?")
    print("   • עדכן את המשימה הראשונה לסטטוס 'בתהליך'")
    print("   • תן לי סטטיסטיקות על המשימות")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
