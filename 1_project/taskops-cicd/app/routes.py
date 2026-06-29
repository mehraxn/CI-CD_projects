"""HTTP route handlers for TaskOps.

Handlers stay thin: they parse input, delegate persistence to the database
layer, log meaningful events, and render templates or JSON.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from . import database

bp = Blueprint("taskops", __name__)


@bp.route("/")
def index():
    """Homepage / landing console."""
    return render_template("index.html")


@bp.route("/tasks")
def tasks():
    """List all tasks."""
    return render_template("tasks.html", tasks=database.get_tasks())


@bp.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    """Create a task with validation, preserving input on error."""
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        max_len = current_app.config["MAX_TITLE_LENGTH"]

        errors: list[str] = []
        if not title:
            errors.append("Title is required.")
        elif len(title) > max_len:
            errors.append(f"Title must be {max_len} characters or fewer.")

        if errors:
            current_app.logger.info("Task validation rejected: %s", "; ".join(errors))
            for message in errors:
                flash(message, "error")
            return (
                render_template(
                    "create_task.html",
                    title=title,
                    description=description,
                    max_len=max_len,
                ),
                400,
            )

        task_id = database.create_task(title, description)
        current_app.logger.info("Task created id=%s title=%r", task_id, title)
        flash("Task created.", "success")
        return redirect(url_for("taskops.tasks"))

    return render_template(
        "create_task.html",
        title="",
        description="",
        max_len=current_app.config["MAX_TITLE_LENGTH"],
    )


@bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete(task_id: int):
    """Mark a task as completed."""
    rows = database.complete_task(task_id)
    if rows:
        current_app.logger.info("Task completed id=%s", task_id)
        flash("Task marked complete.", "success")
    else:
        current_app.logger.info("Task complete no-op id=%s (missing)", task_id)
        flash("Task not found.", "error")
    return redirect(url_for("taskops.tasks"))


@bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete(task_id: int):
    """Delete a task. A missing task is a harmless no-op."""
    rows = database.delete_task(task_id)
    if rows:
        current_app.logger.info("Task deleted id=%s", task_id)
        flash("Task deleted.", "success")
    else:
        current_app.logger.info("Task delete no-op id=%s (missing)", task_id)
        flash("Task not found.", "error")
    return redirect(url_for("taskops.tasks"))


@bp.route("/health")
def health():
    """Liveness/readiness probe."""
    return jsonify(status="ok")
