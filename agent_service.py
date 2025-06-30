"""
AI Agent Service - שירות סוכן AI לניהול משימות
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from openai import OpenAI
import httpx
from dotenv import load_dotenv
from todo_service import todo_service, TaskStatus, TaskType

# *** חשוב: טעינת .env בתחילת הקובץ ***
load_dotenv()

# בדיקה שהמפתח נטען
print(f"🔍 API Key loaded: {'✅ כן' if os.getenv('OPENAI_API_KEY') else '❌ לא'}")

class TodoAgent:
    """סוכן AI לניהול משימות"""
    
    def __init__(self, debug=False):
        self.debug = debug
        
        # קבלת המפתח ממשתנה הסביבה בלבד
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # יצירת OpenAI client עם SSL מושבת אם נדרש
        try:
            self.client = OpenAI(api_key=api_key)
            # בדיקה מהירה
            self.client.models.list()
            if self.debug:
                print("✅ משתמש ב-OpenAI client רגיל")
            
        except Exception as e:
            if self.debug:
                print(f"⚠️  Client רגיל לא עובד: {e}")
                print("🔧 יוצר client עם SSL מושבת...")
            
            # יצירת client עם SSL מושבת
            http_client = httpx.Client(
                verify=False,
                timeout=30.0
            )
            
            self.client = OpenAI(api_key=api_key, http_client=http_client)
            
            if self.debug:
                print("✅ משתמש ב-OpenAI client עם SSL מושבת")
        
        # הגדרת הפונקציות הזמינות למערכת
        self.available_functions = {
            "get_tasks": {
                "function": self._get_tasks_wrapper,
                "description": "שליפת משימות עם אפשרות סינון לפי סטטוס, סוג או כותרת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "סינון לפי סטטוס המשימה"
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["personal", "work", "urgent", "project"],
                            "description": "סינון לפי סוג המשימה"
                        },
                        "title_filter": {
                            "type": "string",
                            "description": "חיפוש חלקי בכותרת המשימה"
                        }
                    }
                }
            },
            "add_task": {
                "function": self._add_task_wrapper,
                "description": "הוספת משימה חדשה למערכת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "כותרת המשימה (חובה)"
                        },
                        "description": {
                            "type": "string",
                            "description": "תיאור המשימה"
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["personal", "work", "urgent", "project"],
                            "description": "סוג המשימה"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "תאריך סיום בפורמט ISO (YYYY-MM-DD או YYYY-MM-DDTHH:MM:SS)"
                        }
                    },
                    "required": ["title"]
                }
            },
            "update_task": {
                "function": self._update_task_wrapper,
                "description": "עדכון משימה קיימת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "קוד המשימה לעדכון (חובה)"
                        },
                        "title": {
                            "type": "string",
                            "description": "כותרת חדשה"
                        },
                        "description": {
                            "type": "string",
                            "description": "תיאור חדש"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "סטטוס חדש"
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["personal", "work", "urgent", "project"],
                            "description": "סוג משימה חדש"
                        }
                    },
                    "required": ["code"]
                }
            },
            "delete_task": {
                "function": self._delete_task_wrapper,
                "description": "מחיקת משימה מהמערכת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "קוד המשימה למחיקה (חובה)"
                        }
                    },
                    "required": ["code"]
                }
            },
            "get_tasks_stats": {
                "function": self._get_stats_wrapper,
                "description": "קבלת סטטיסטיקות על המשימות במערכת",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    def _get_tasks_wrapper(self, status=None, task_type=None, title_filter=None):
        """Wrapper לפונקציית get_tasks"""
        try:
            # המרת strings ל-enums
            status_enum = TaskStatus(status) if status else None
            type_enum = TaskType(task_type) if task_type else None
            
            return {
                "success": True,
                "data": todo_service.get_tasks(status_enum, type_enum, title_filter)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_task_wrapper(self, title, description="", task_type="personal", end_date=None):
        """Wrapper לפונקציית add_task"""
        try:
            type_enum = TaskType(task_type)
            end_date_obj = None
            
            if end_date:
                try:
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except:
                    return {"success": False, "error": "פורמט תאריך לא תקין"}
            
            result = todo_service.add_task(
                title=title,
                description=description,
                task_type=type_enum,
                end_date=end_date_obj
            )
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_task_wrapper(self, code, **kwargs):
        """Wrapper לפונקציית update_task"""
        try:
            # המרת strings ל-enums במידת הצורך
            if 'status' in kwargs:
                kwargs['status'] = TaskStatus(kwargs['status'])
            if 'task_type' in kwargs:
                kwargs['task_type'] = TaskType(kwargs['task_type'])
            
            result = todo_service.update_task(code, **kwargs)
            
            if result:
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "משימה לא נמצאה"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_task_wrapper(self, code):
        """Wrapper לפונקציית delete_task"""
        try:
            success = todo_service.delete_task(code)
            if success:
                return {"success": True, "message": "המשימה נמחקה בהצלחה"}
            else:
                return {"success": False, "error": "משימה לא נמצאה"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_stats_wrapper(self):
        """Wrapper לפונקציית get_tasks_count"""
        try:
            return {"success": True, "data": todo_service.get_tasks_count()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_function_definitions(self):
        """יצירת הגדרות הפונקציות עבור OpenAI"""
        tools = []
        
        for func_name, func_info in self.available_functions.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": func_info["description"],
                    "parameters": func_info["parameters"]
                }
            })
        
        return tools
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]):
        """הפעלת פונקציה לפי שם וארגומנטים"""
        if function_name not in self.available_functions:
            return {"success": False, "error": f"פונקציה לא קיימת: {function_name}"}
        
        if self.debug:
            print(f"הפעלת פונקציה: {function_name} עם ארגומנטים: {arguments}")
        
        try:
            func = self.available_functions[function_name]["function"]
            return func(**arguments)
        except Exception as e:
            return {"success": False, "error": f"שגיאה בהפעלת הפונקציה: {str(e)}"}
    
    async def process_query(self, query: str) -> str:
        """
        הפונקציה המרכזית של הסוכן
        
        Args:
            query: שאילתת המשתמש
            
        Returns:
            תשובה מנוסחת בשפת בני אדם
        """
        try:
            if self.debug:
                print(f"שאילתת המשתמש: {query}")
            
            # שלב 1: שליחת השאילתה ל-GPT עם הגדרת הפונקציות
            tools = self._create_function_definitions()
            
            messages = [
                {
                    "role": "system",
                    "content": """אתה סוכן AI לניהול משימות. אתה יכול לעזור למשתמשים:
                    - לצפות במשימות שלהם
                    - להוסיף משימות חדשות
                    - לעדכן משימות קיימות
                    - למחוק משימות
                    - לקבל סטטיסטיקות
                    
                    השתמש בפונקציות הזמינות לך כדי לבצע את הפעולות הנדרשות.
                    תמיד תן תשובות בעברית וביטוי ידידותי."""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            if self.debug:
                print(f"תשובה ראשונית: {response}")
            
            message = response.choices[0].message
            
            # שלב 2: בדיקה אם GPT רוצה להפעיל פונקציה
            if message.tool_calls:
                # הוספת הודעת הסוכן למערך ההודעות
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })
                
                # הפעלת כל הפונקציות שנדרשו
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # שלב 3: הפעלת הפונקציה
                    function_result = self._execute_function(function_name, function_args)
                    
                    # הוספת תוצאת הפונקציה להודעות
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result, ensure_ascii=False)
                    })
                
                # קבלת תשובה סופית מ-GPT
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                
                if self.debug:
                    print(f"תשובה סופית: {final_response}")
                
                return final_response.choices[0].message.content
            
            else:
                # אם GPT לא רוצה להפעיל פונקציה, מחזיר את התשובה הישירה
                return message.content
            
        except Exception as e:
            if self.debug:
                print(f"שגיאה בעיבוד השאילתה: {str(e)}")
            return f"מצטער, אירעה שגיאה: {str(e)}"


# יצירת instance גלובלי של הסוכן (עם דיבוג לבדיקה)
agent_service = TodoAgent(debug=True)

# פונקציה נוחה לשימוש
async def agent(query: str) -> str:
    """
    פונקציה נוחה לשימוש בסוכן
    
    Args:
        query: שאילתת המשתמש
        
    Returns:
        תשובת הסוכן
    """
    print(f"🔍 Agent received query: {query}")
    print(f"🔍 Available functions: {list(agent_service.available_functions.keys())}")
    return await agent_service.process_query(query)
