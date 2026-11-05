from datetime import date
from priority_queue import MaxHeap


class TaskScheduler:
    def __init__(self, initial_tasks=None):
        self.tasks = {}
        self.next_id = 1
        self.queue = MaxHeap()

        for task in initial_tasks or []:
            self.tasks[int(task["id"])] = task
            self.next_id = max(self.next_id, int(task["id"]) + 1)

        self.rebuild_queue()

    @staticmethod
    def urgency_score(deadline):
        due = date.fromisoformat(deadline)
        days_left = (due - date.today()).days

        if days_left <= 0:
            return 100
        if days_left <= 1:
            return 95
        if days_left <= 3:
            return 80
        if days_left <= 7:
            return 60
        if days_left <= 14:
            return 40
        return 20

    @classmethod
    def calculate_priority(cls, task):
        urgency = cls.urgency_score(task["deadline"])
        importance = int(task["importance"]) * 20
        effort = min(float(task["hours"]) * 10, 100)

        return round(
            0.50 * urgency
            + 0.30 * importance
            + 0.20 * effort,
            2
        )

    def rebuild_queue(self):
        self.queue = MaxHeap()

        for task in self.tasks.values():
            if task["status"] == "Pending":
                self.queue.push({
                    "id": task["id"],
                    "score": self.calculate_priority(task),
                    "deadline": task["deadline"]
                })

    def add_task(self, title, category, deadline, importance, hours):
        title = title.strip()
        category = category.strip()

        if not title:
            raise ValueError("Task title cannot be empty.")
        if not category:
            raise ValueError("Category cannot be empty.")

        date.fromisoformat(deadline)

        importance = int(importance)
        hours = float(hours)

        if not 1 <= importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")
        if not 0 < hours <= 100:
            raise ValueError("Estimated hours must be greater than 0 and at most 100.")

        task = {
            "id": self.next_id,
            "title": title,
            "category": category,
            "deadline": deadline,
            "importance": importance,
            "hours": hours,
            "status": "Pending"
        }

        self.tasks[self.next_id] = task
        self.next_id += 1
        self.rebuild_queue()
        return task

    def update_task(self, task_id, title, category, deadline,
                    importance, hours):
        task_id = int(task_id)

        if task_id not in self.tasks:
            raise KeyError("Task not found.")

        old_status = self.tasks[task_id]["status"]

        if old_status == "Completed":
            raise ValueError("Completed tasks cannot be edited.")

        title = title.strip()
        category = category.strip()

        if not title or not category:
            raise ValueError("Title and category are required.")

        date.fromisoformat(deadline)

        importance = int(importance)
        hours = float(hours)

        if not 1 <= importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")
        if not 0 < hours <= 100:
            raise ValueError("Estimated hours must be greater than 0 and at most 100.")

        self.tasks[task_id].update({
            "title": title,
            "category": category,
            "deadline": deadline,
            "importance": importance,
            "hours": hours
        })

        self.rebuild_queue()
        return self.tasks[task_id]

    def complete_task(self, task_id):
        task_id = int(task_id)

        if task_id not in self.tasks:
            raise KeyError("Task not found.")

        self.tasks[task_id]["status"] = "Completed"
        self.rebuild_queue()
        return self.tasks[task_id]

    def delete_task(self, task_id):
        task_id = int(task_id)

        if task_id not in self.tasks:
            raise KeyError("Task not found.")

        task = self.tasks.pop(task_id)
        self.rebuild_queue()
        return task

    def search(self, query):
        query = query.strip().lower()

        if query.isdigit():
            task = self.tasks.get(int(query))
            return [task] if task else []

        return [
            task for task in self.tasks.values()
            if query in task["title"].lower()
            or query in task["category"].lower()
        ]

    def get_ranked_tasks(self):
        self.rebuild_queue()
        ranked = []

        while not self.queue.is_empty():
            item = self.queue.pop()
            task = self.tasks[item["id"]].copy()
            task["priority"] = item["score"]
            ranked.append(task)

        return ranked

    def get_next_task(self):
        self.rebuild_queue()
        item = self.queue.peek()

        if item is None:
            return None

        task = self.tasks[item["id"]].copy()
        task["priority"] = item["score"]
        return task

    def get_all_tasks(self):
        result = []

        for task in self.tasks.values():
            item = task.copy()
            item["priority"] = self.calculate_priority(item)
            result.append(item)

        return sorted(
            result,
            key=lambda t: (
                t["status"] == "Completed",
                -t["priority"] if t["status"] == "Pending" else 0
            )
        )

    def get_statistics(self):
        tasks = list(self.tasks.values())
        pending = [t for t in tasks if t["status"] == "Pending"]
        completed = [t for t in tasks if t["status"] == "Completed"]
        today = date.today()

        overdue = [
            t for t in pending
            if date.fromisoformat(t["deadline"]) < today
        ]

        return {
            "total": len(tasks),
            "pending": len(pending),
            "completed": len(completed),
            "overdue": len(overdue)
        }