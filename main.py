from scheduler import TaskScheduler
from storage import load_tasks, save_tasks


def main():
    scheduler = TaskScheduler(load_tasks())

    while True:
        print("\n===== STUDENT TASK SCHEDULER =====")
        print("1. Add task")
        print("2. View all tasks")
        print("3. View priority queue")
        print("4. View next recommended task")
        print("5. Search task")
        print("6. Complete task")
        print("7. Delete task")
        print("8. Statistics")
        print("0. Exit")

        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                title = input("Task title: ")
                category = input("Category: ")
                deadline = input("Deadline (YYYY-MM-DD): ")
                importance = int(input("Importance (1-5): "))
                hours = float(input("Estimated hours: "))

                task = scheduler.add_task(
                    title, category, deadline, importance, hours
                )
                print("Task added:", task["id"])

            elif choice == "2":
                for task in scheduler.get_all_tasks():
                    print(task)

            elif choice == "3":
                for task in scheduler.get_ranked_tasks():
                    print(task)

            elif choice == "4":
                print(scheduler.get_next_task() or "No pending tasks.")

            elif choice == "5":
                query = input("Search by ID, title or category: ")
                for task in scheduler.search(query):
                    print(task)

            elif choice == "6":
                scheduler.complete_task(int(input("Task ID: ")))
                print("Task completed.")

            elif choice == "7":
                scheduler.delete_task(int(input("Task ID: ")))
                print("Task deleted.")

            elif choice == "8":
                print(scheduler.get_statistics())

            elif choice == "0":
                save_tasks(list(scheduler.tasks.values()))
                print("Data saved. Goodbye.")
                break

            else:
                print("Invalid choice.")

            save_tasks(list(scheduler.tasks.values()))

        except (ValueError, KeyError) as error:
            print("Error:", error)


if __name__ == "__main__":
    main()