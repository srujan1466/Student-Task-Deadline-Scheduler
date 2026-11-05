from flask import Flask, render_template, request, jsonify
from scheduler import TaskScheduler
from storage import load_tasks, save_tasks

app = Flask(__name__)
scheduler = TaskScheduler(load_tasks())


def persist():
    save_tasks(list(scheduler.tasks.values()))


def error_response(message, status=400):
    return jsonify({"error": str(message)}), status


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(scheduler.get_all_tasks())


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}

    try:
        task = scheduler.add_task(
            data.get("title", ""),
            data.get("category", ""),
            data.get("deadline", ""),
            data.get("importance", 3),
            data.get("hours", 1)
        )
        persist()
        result = task.copy()
        result["priority"] = scheduler.calculate_priority(task)
        return jsonify(result), 201
    except (ValueError, TypeError) as exc:
        return error_response(exc)


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    try:
        task = scheduler.update_task(
            task_id,
            data.get("title", ""),
            data.get("category", ""),
            data.get("deadline", ""),
            data.get("importance", 3),
            data.get("hours", 1)
        )
        persist()
        result = task.copy()
        result["priority"] = scheduler.calculate_priority(task)
        return jsonify(result)
    except KeyError as exc:
        return error_response(exc, 404)
    except (ValueError, TypeError) as exc:
        return error_response(exc)


@app.route("/api/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    try:
        task = scheduler.complete_task(task_id)
        persist()
        return jsonify(task)
    except KeyError as exc:
        return error_response(exc, 404)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        task = scheduler.delete_task(task_id)
        persist()
        return jsonify(task)
    except KeyError as exc:
        return error_response(exc, 404)


@app.route("/api/search")
def search_tasks():
    query = request.args.get("q", "")
    results = []

    for task in scheduler.search(query):
        item = task.copy()
        item["priority"] = scheduler.calculate_priority(item)
        results.append(item)

    return jsonify(results)


@app.route("/api/priority")
def priority_tasks():
    return jsonify(scheduler.get_ranked_tasks())


@app.route("/api/next")
def next_task():
    return jsonify(scheduler.get_next_task())


@app.route("/api/statistics")
def statistics():
    return jsonify(scheduler.get_statistics())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)