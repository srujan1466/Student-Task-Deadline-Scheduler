const API = "/api";
let tasks = [];
let editingId = null;
let toastTimer = null;

async function api(path, options = {}) {
    const response = await fetch(API + path, {
        headers: { "Content-Type": "application/json" },
        ...options
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
    }
    return data;
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function isOverdue(task) {
    return task.status === "Pending" &&
        task.deadline < new Date().toISOString().slice(0, 10);
}

function formatDate(value) {
    return new Date(value + "T00:00:00").toLocaleDateString(
        undefined, { day: "numeric", month: "short", year: "numeric" }
    );
}

async function refresh() {
    try {
        const [all, stats, ranked, next] = await Promise.all([
            api("/tasks"),
            api("/statistics"),
            api("/priority"),
            api("/next")
        ]);

        tasks = all;
        document.getElementById("totalCount").textContent = stats.total;
        document.getElementById("pendingCount").textContent = stats.pending;
        document.getElementById("completedCount").textContent = stats.completed;
        document.getElementById("overdueCount").textContent = stats.overdue;

        renderTasks();
        renderPriority(ranked);
        renderNext(next);
    } catch (error) {
        showToast(error.message);
    }
}

function renderNext(task) {
    const container = document.getElementById("nextTask");

    if (!task) {
        container.innerHTML = `
            <div>
                <p class="eyebrow light">RECOMMENDED NEXT TASK</p>
                <h2>You're all caught up!</h2>
                <p>Add a pending task to get a recommendation.</p>
            </div><div class="recommend-icon">✓</div>`;
        return;
    }

    container.innerHTML = `
        <div>
            <p class="eyebrow light">RECOMMENDED NEXT TASK</p>
            <h2>${escapeHTML(task.title)}</h2>
            <p>${escapeHTML(task.category)} · Due ${formatDate(task.deadline)}
            · Priority score ${task.priority}</p>
        </div>
        <div class="recommend-icon">↗</div>`;
}

function renderTasks() {
    const query = document.getElementById("searchInput").value.trim().toLowerCase();
    const sort = document.getElementById("sortSelect").value;

    let filtered = tasks.filter(task =>
        String(task.id).includes(query) ||
        task.title.toLowerCase().includes(query) ||
        task.category.toLowerCase().includes(query)
    );

    if (sort === "deadline") {
        filtered.sort((a, b) => a.deadline.localeCompare(b.deadline));
    } else if (sort === "title") {
        filtered.sort((a, b) => a.title.localeCompare(b.title));
    } else {
        filtered.sort((a, b) => {
            if (a.status !== b.status) return a.status === "Pending" ? -1 : 1;
            return b.priority - a.priority;
        });
    }

    const container = document.getElementById("taskList");

    if (!filtered.length) {
        container.innerHTML = `<div class="empty">No matching tasks found.</div>`;
        return;
    }

    container.innerHTML = filtered.map(task => {
        const statusClass = task.status === "Completed"
            ? "completed" : isOverdue(task) ? "overdue" : "";
        const statusText = task.status === "Completed"
            ? "Completed" : isOverdue(task) ? "Overdue" : "Pending";

        return `
        <article class="task-row">
            <div class="task-info">
                <strong>${escapeHTML(task.title)}</strong>
                <div class="task-meta">
                    #${task.id} · ${escapeHTML(task.category)}
                    · Due ${formatDate(task.deadline)}
                    · ${task.hours} hours
                </div>
            </div>
            <div class="task-actions">
                <span class="pill ${statusClass}">${statusText}</span>
                <span class="score">${task.priority}</span>
                ${task.status === "Pending" ? `
                    <button class="action-btn" onclick="editTask(${task.id})">Edit</button>
                    <button class="action-btn" onclick="completeTask(${task.id})">Done</button>
                ` : ""}
                <button class="action-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </article>`;
    }).join("");
}

function renderPriority(ranked) {
    const container = document.getElementById("priorityList");

    if (!ranked.length) {
        container.innerHTML = `<div class="empty">No pending tasks in the priority queue.</div>`;
        return;
    }

    container.innerHTML = ranked.map((task, index) => `
        <article class="priority-row">
            <span class="rank">${index + 1}</span>
            <div class="task-info">
                <strong>${escapeHTML(task.title)}</strong>
                <div class="task-meta">
                    ${escapeHTML(task.category)} · Due ${formatDate(task.deadline)}
                </div>
            </div>
            <span class="score">${task.priority} pts</span>
        </article>
    `).join("");
}

function openForm(task = null) {
    editingId = task ? task.id : null;
    document.getElementById("modalTitle").textContent =
        task ? "Edit task" : "Create a task";

    document.getElementById("taskId").value = task ? task.id : "";
    document.getElementById("title").value = task ? task.title : "";
    document.getElementById("category").value = task ? task.category : "";
    document.getElementById("deadline").value = task ? task.deadline : "";
    document.getElementById("importance").value = task ? task.importance : 3;
    document.getElementById("hours").value = task ? task.hours : 2;

    document.getElementById("taskModal").classList.add("show");
}

function closeForm() {
    document.getElementById("taskModal").classList.remove("show");
    document.getElementById("taskForm").reset();
    editingId = null;
}

async function editTask(id) {
    const task = tasks.find(item => item.id === id);
    if (task) openForm(task);
}

async function completeTask(id) {
    try {
        await api(`/tasks/${id}/complete`, { method: "POST" });
        showToast("Task marked as completed.");
        await refresh();
    } catch (error) {
        showToast(error.message);
    }
}

async function deleteTask(id) {
    if (!confirm("Delete this task permanently?")) return;

    try {
        await api(`/tasks/${id}`, { method: "DELETE" });
        showToast("Task deleted.");
        await refresh();
    } catch (error) {
        showToast(error.message);
    }
}

document.getElementById("taskForm").addEventListener("submit", async event => {
    event.preventDefault();

    const data = {
        title: document.getElementById("title").value,
        category: document.getElementById("category").value,
        deadline: document.getElementById("deadline").value,
        importance: Number(document.getElementById("importance").value),
        hours: Number(document.getElementById("hours").value)
    };

    try {
        const path = editingId ? `/tasks/${editingId}` : "/tasks";
        await api(path, {
            method: editingId ? "PUT" : "POST",
            body: JSON.stringify(data)
        });

        closeForm();
        showToast(editingId ? "Task updated." : "Task created.");
        await refresh();
    } catch (error) {
        showToast(error.message);
    }
});

document.getElementById("searchInput").addEventListener("input", renderTasks);
document.getElementById("sortSelect").addEventListener("change", renderTasks);

function openFormFromButton() {
    openForm();
}

refresh();