"""
Flask Server לסוכן AI לניהול משימות
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging
from agent_service import agent
from todo_service import todo_service, TaskType, TaskStatus

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# הגדרת מפתח OpenAI
if not os.getenv("OPENAI_API_KEY"):
    logger.warning("⚠️  אנא הגדר את משתנה הסביבה OPENAI_API_KEY")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'נתיב לא נמצא', 'success': False}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"שגיאת שרת: {error}")
    return jsonify({'error': 'שגיאת שרת פנימית', 'success': False}), 500

@app.route('/')
def index():
    """עמוד הבית"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """בדיקת תקינות השרת"""
    return jsonify({'status': 'healthy', 'success': True})

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint לשיחה עם הסוכן"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'נתונים חסרים', 'success': False}), 400
            
        query = data.get('query', '')
        
        if not query.strip():
            return jsonify({'error': 'שאילתה ריקה', 'success': False}), 400
        
        # בדיקת מפתח API
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({
                'error': 'מפתח OpenAI לא מוגדר',
                'success': False
            }), 500
        
        # הפעלת הסוכן
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(agent(query))
        finally:
            loop.close()
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"שגיאה ב-chat endpoint: {str(e)}")
        return jsonify({
            'error': f'שגיאה בעיבוד הבקשה: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    """API לקבלת כל המשימות"""
    try:
        # קבלת פרמטרים לסינון
        status_param = request.args.get('status')
        task_type_param = request.args.get('task_type')
        title_filter = request.args.get('title_filter')
        
        # המרת פרמטרים לאנומים
        status = None
        if status_param:
            try:
                status = TaskStatus(status_param)
            except ValueError:
                pass
                
        task_type = None
        if task_type_param:
            try:
                task_type = TaskType(task_type_param)
            except ValueError:
                pass
        
        tasks = todo_service.get_tasks(status=status, task_type=task_type, title_filter=title_filter)
        stats = todo_service.get_tasks_count()
        
        return jsonify({
            'tasks': tasks,
            'stats': stats,
            'success': True
        })
    except Exception as e:
        logger.error(f"שגיאה ב-tasks endpoint: {str(e)}")
        return jsonify({
            'error': f'שגיאה בטעינת המשימות: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks', methods=['POST'])
def add_task_api():
    """API להוספת משימה חדשה"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'נתונים חסרים', 'success': False}), 400
        
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'כותרת המשימה חובה', 'success': False}), 400
        
        description = data.get('description', '')
        task_type_str = data.get('task_type', 'personal')
        
        # המרת סוג המשימה
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.PERSONAL
        
        task = todo_service.add_task(
            title=title,
            description=description,
            task_type=task_type
        )
        
        return jsonify({
            'task': task,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"שגיאה בהוספת משימה: {str(e)}")
        return jsonify({
            'error': f'שגיאה בהוספת המשימה: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks/<string:task_code>', methods=['PUT'])
def update_task_api(task_code):
    """API לעדכון משימה"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'נתונים חסרים', 'success': False}), 400
        
        # המרת ערכי אנום אם נדרש
        if 'task_type' in data:
            try:
                data['task_type'] = TaskType(data['task_type'])
            except ValueError:
                pass
                
        if 'status' in data:
            try:
                data['status'] = TaskStatus(data['status'])
            except ValueError:
                pass
        
        task = todo_service.update_task(task_code, **data)
        if task:
            return jsonify({
                'task': task,
                'success': True
            })
        else:
            return jsonify({'error': 'משימה לא נמצאה', 'success': False}), 404
        
    except Exception as e:
        logger.error(f"שגיאה בעדכון משימה: {str(e)}")
        return jsonify({
            'error': f'שגיאה בעדכון המשימה: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks/<string:task_code>', methods=['DELETE'])
def delete_task_api(task_code):
    """API למחיקת משימה"""
    try:
        if todo_service.delete_task(task_code):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'משימה לא נמצאה', 'success': False}), 404
        
    except Exception as e:
        logger.error(f"שגיאה במחיקת משימה: {str(e)}")
        return jsonify({
            'error': f'שגיאה במחיקת המשימה: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks/<string:task_code>/complete', methods=['POST'])
def complete_task_api(task_code):
    """API לסימון משימה כהושלמה"""
    try:
        task = todo_service.update_task(task_code, status=TaskStatus.COMPLETED)
        if task:
            return jsonify({
                'task': task,
                'success': True
            })
        else:
            return jsonify({'error': 'משימה לא נמצאה', 'success': False}), 404
        
    except Exception as e:
        logger.error(f"שגיאה בהשלמת משימה: {str(e)}")
        return jsonify({
            'error': f'שגיאה בהשלמת המשימה: {str(e)}',
            'success': False
        }), 500

@app.route('/api/tasks/<string:task_code>', methods=['GET'])
def get_task_api(task_code):
    """API לקבלת משימה בודדת"""
    try:
        task = todo_service.get_task_by_code(task_code)
        if task:
            return jsonify({
                'task': task,
                'success': True
            })
        else:
            return jsonify({'error': 'משימה לא נמצאה', 'success': False}), 404
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת משימה: {str(e)}")
        return jsonify({
            'error': f'שגיאה בקבלת המשימה: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
