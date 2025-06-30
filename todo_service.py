# """
# Todo Service - מערכת לניהול משימות
# """
# from datetime import datetime
# from typing import List, Dict, Optional, Any
# from enum import Enum


# class TaskStatus(Enum):
#     """סטטוסים אפשריים למשימה"""
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     COMPLETED = "completed"
#     CANCELLED = "cancelled"


# class TaskType(Enum):
#     """סוגי משימות"""
#     PERSONAL = "personal"
#     WORK = "work"
#     URGENT = "urgent"
#     PROJECT = "project"


# class Task:
#     """הישות המרכזית - משימה"""
    
#     def __init__(self, code: str, title: str, description: str = "", 
#                  task_type: TaskType = TaskType.PERSONAL,
#                  start_date: Optional[datetime] = None,
#                  end_date: Optional[datetime] = None,
#                  status: TaskStatus = TaskStatus.PENDING):
#         self.code = code
#         self.title = title
#         self.description = description
#         self.task_type = task_type
#         self.start_date = start_date or datetime.now()
#         self.end_date = end_date
#         self.status = status
#         self.created_at = datetime.now()
#         self.updated_at = datetime.now()
    
#     def to_dict(self) -> Dict[str, Any]:
#         """המרה למילון"""
#         return {
#             "code": self.code,
#             "title": self.title,
#             "description": self.description,
#             "task_type": self.task_type.value,
#             "start_date": self.start_date.isoformat() if self.start_date else None,
#             "end_date": self.end_date.isoformat() if self.end_date else None,
#             "status": self.status.value,
#             "created_at": self.created_at.isoformat(),
#             "updated_at": self.updated_at.isoformat()
#         }


# class TodoService:
#     """שירות לניהול משימות"""
    
#     def __init__(self):
#         self._tasks: List[Task] = []
#         self._next_id = 1
    
#     def get_tasks(self, status: Optional[TaskStatus] = None,
#                   task_type: Optional[TaskType] = None,
#                   title_filter: Optional[str] = None) -> List[Dict[str, Any]]:
#         """
#         שליפת משימות עם סינונים שונים
        
#         Args:
#             status: סינון לפי סטטוס
#             task_type: סינון לפי סוג משימה
#             title_filter: סינון לפי כותרת (חיפוש חלקי)
        
#         Returns:
#             רשימת משימות מסוננת
#         """
#         filtered_tasks = self._tasks.copy()
        
#         if status:
#             filtered_tasks = [task for task in filtered_tasks if task.status == status]
        
#         if task_type:
#             filtered_tasks = [task for task in filtered_tasks if task.task_type == task_type]
        
#         if title_filter:
#             filtered_tasks = [task for task in filtered_tasks 
#                             if title_filter.lower() in task.title.lower()]
        
#         return [task.to_dict() for task in filtered_tasks]
    
#     def add_task(self, title: str, description: str = "",
#                  task_type: TaskType = TaskType.PERSONAL,
#                  start_date: Optional[datetime] = None,
#                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
#         """
#         הוספת משימה חדשה
        
#         Args:
#             title: כותרת המשימה
#             description: תיאור המשימה
#             task_type: סוג המשימה
#             start_date: תאריך התחלה
#             end_date: תאריך סיום
        
#         Returns:
#             המשימה שנוספה
#         """
#         if not title.strip():
#             raise ValueError("כותרת המשימה לא יכולה להיות רקה")
        
#         code = f"TASK_{self._next_id:04d}"
#         self._next_id += 1
        
#         task = Task(
#             code=code,
#             title=title.strip(),
#             description=description.strip(),
#             task_type=task_type,
#             start_date=start_date,
#             end_date=end_date
#         )
        
#         self._tasks.append(task)
#         return task.to_dict()
    
#     def update_task(self, code: str, **kwargs) -> Optional[Dict[str, Any]]:
#         """
#         עדכון משימה קיימת
        
#         Args:
#             code: קוד המשימה
#             **kwargs: שדות לעדכון
        
#         Returns:
#             המשימה המעודכנת או None אם לא נמצאה
#         """
#         task = self._find_task_by_code(code)
#         if not task:
#             return None
        
#         # עדכון השדות המותרים
#         allowed_fields = ['title', 'description', 'task_type', 'start_date', 'end_date', 'status']
        
#         for field, value in kwargs.items():
#             if field in allowed_fields and hasattr(task, field):
#                 if field == 'title' and not value.strip():
#                     raise ValueError("כותרת המשימה לא יכולה להיות רקה")
                
#                 if field in ['task_type', 'status']:
#                     # וידוא שהערך הוא מהסוג הנכון
#                     if field == 'task_type' and isinstance(value, str):
#                         value = TaskType(value)
#                     elif field == 'status' and isinstance(value, str):
#                         value = TaskStatus(value)
                
#                 setattr(task, field, value)
        
#         task.updated_at = datetime.now()
#         return task.to_dict()
    
#     def delete_task(self, code: str) -> bool:
#         """
#         מחיקת משימה
        
#         Args:
#             code: קוד המשימה
        
#         Returns:
#             True אם המשימה נמחקה, False אם לא נמצאה
#         """
#         task = self._find_task_by_code(code)
#         if task:
#             self._tasks.remove(task)
#             return True
#         return False
    
#     def _find_task_by_code(self, code: str) -> Optional[Task]:
#         """חיפוש משימה לפי קוד"""
#         for task in self._tasks:
#             if task.code == code:
#                 return task
#         return None
    
#     def get_task_by_code(self, code: str) -> Optional[Dict[str, Any]]:
#         """שליפת משימה בודדת לפי קוד"""
#         task = self._find_task_by_code(code)
#         return task.to_dict() if task else None
    
#     def get_tasks_count(self) -> Dict[str, int]:
#         """קבלת מספר המשימות לפי סטטוס"""
#         counts = {status.value: 0 for status in TaskStatus}
        
#         for task in self._tasks:
#             counts[task.status.value] += 1
        
#         counts['total'] = len(self._tasks)
#         return counts


# # יצירת instance גלובלי של השירות
# todo_service = TodoService()

# # הוספת משימות לדוגמה
# todo_service.add_task(
#     title="סיום פרויקט AI",
#     description="להשלים את פיתוח הסוכן החכם",
#     task_type=TaskType.WORK
# )

# todo_service.add_task(
#     title="קניות בסופר",
#     description="לקנות חלב, לחם וביצים",
#     task_type=TaskType.PERSONAL
# )

# todo_service.add_task(
#     title="פגישה עם לקוח",
#     description="פגישה חשובה בשעה 14:00",
#     task_type=TaskType.URGENT
# )

# print(f"🔍 Agent received query: {query}")
# print(f"🔍 Available functions: {list(self.available_functions.keys())}")
"""
Todo Service - מערכת לניהול משימות
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class TaskStatus(Enum):
    """סטטוסים אפשריים למשימה"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """סוגי משימות"""
    PERSONAL = "personal"
    WORK = "work"
    URGENT = "urgent"
    PROJECT = "project"


class Task:
    """הישות המרכזית - משימה"""
    
    def __init__(self, code: str, title: str, description: str = "", 
                 task_type: TaskType = TaskType.PERSONAL,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 status: TaskStatus = TaskStatus.PENDING):
        self.code = code
        self.title = title
        self.description = description
        self.task_type = task_type
        self.start_date = start_date or datetime.now()
        self.end_date = end_date
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class TodoService:
    """שירות לניהול משימות"""
    
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1
    
    def get_tasks(self, status: Optional[TaskStatus] = None,
                  task_type: Optional[TaskType] = None,
                  title_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        שליפת משימות עם סינונים שונים
        
        Args:
            status: סינון לפי סטטוס
            task_type: סינון לפי סוג משימה
            title_filter: סינון לפי כותרת (חיפוש חלקי)
        
        Returns:
            רשימת משימות מסוננת
        """
        filtered_tasks = self._tasks.copy()
        
        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]
        
        if task_type:
            filtered_tasks = [task for task in filtered_tasks if task.task_type == task_type]
        
        if title_filter:
            filtered_tasks = [task for task in filtered_tasks 
                            if title_filter.lower() in task.title.lower()]
        
        return [task.to_dict() for task in filtered_tasks]
    
    def add_task(self, title: str, description: str = "",
                 task_type: TaskType = TaskType.PERSONAL,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        הוספת משימה חדשה
        
        Args:
            title: כותרת המשימה
            description: תיאור המשימה
            task_type: סוג המשימה
            start_date: תאריך התחלה
            end_date: תאריך סיום
        
        Returns:
            המשימה שנוספה
        """
        if not title.strip():
            raise ValueError("כותרת המשימה לא יכולה להיות רקה")
        
        code = f"TASK_{self._next_id:04d}"
        self._next_id += 1
        
        task = Task(
            code=code,
            title=title.strip(),
            description=description.strip(),
            task_type=task_type,
            start_date=start_date,
            end_date=end_date
        )
        
        self._tasks.append(task)
        return task.to_dict()
    
    def update_task(self, code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        עדכון משימה קיימת
        
        Args:
            code: קוד המשימה
            **kwargs: שדות לעדכון
        
        Returns:
            המשימה המעודכנת או None אם לא נמצאה
        """
        task = self._find_task_by_code(code)
        if not task:
            return None
        
        # עדכון השדות המותרים
        allowed_fields = ['title', 'description', 'task_type', 'start_date', 'end_date', 'status']
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(task, field):
                if field == 'title' and not value.strip():
                    raise ValueError("כותרת המשימה לא יכולה להיות רקה")
                
                if field in ['task_type', 'status']:
                    # וידוא שהערך הוא מהסוג הנכון
                    if field == 'task_type' and isinstance(value, str):
                        value = TaskType(value)
                    elif field == 'status' and isinstance(value, str):
                        value = TaskStatus(value)
                
                setattr(task, field, value)
        
        task.updated_at = datetime.now()
        return task.to_dict()
    
    def delete_task(self, code: str) -> bool:
        """
        מחיקת משימה
        
        Args:
            code: קוד המשימה
        
        Returns:
            True אם המשימה נמחקה, False אם לא נמצאה
        """
        task = self._find_task_by_code(code)
        if task:
            self._tasks.remove(task)
            return True
        return False
    
    def _find_task_by_code(self, code: str) -> Optional[Task]:
        """חיפוש משימה לפי קוד"""
        for task in self._tasks:
            if task.code == code:
                return task
        return None
    
    def get_task_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """שליפת משימה בודדת לפי קוד"""
        task = self._find_task_by_code(code)
        return task.to_dict() if task else None
    
    def get_tasks_count(self) -> Dict[str, int]:
        """קבלת מספר המשימות לפי סטטוס"""
        counts = {status.value: 0 for status in TaskStatus}
        
        for task in self._tasks:
            counts[task.status.value] += 1
        
        counts['total'] = len(self._tasks)
        return counts


# יצירת instance גלובלי של השירות
todo_service = TodoService()

# הוספת משימות לדוגמה
todo_service.add_task(
    title="סיום פרויקט AI",
    description="להשלים את פיתוח הסוכן החכם",
    task_type=TaskType.WORK
)

todo_service.add_task(
    title="קניות בסופר",
    description="לקנות חלב, לחם וביצים",
    task_type=TaskType.PERSONAL
)

todo_service.add_task(
    title="פגישה עם לקוח",
    description="פגישה חשובה בשעה 14:00",
    task_type=TaskType.URGENT
)

# הסרתי את השורות הבעייתיות שגרמו לשגיאה
print("✅ Todo Service initialized successfully")
