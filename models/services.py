import csv
from datetime import datetime
import io
import json

from ai_engine.baseai import agent
from config import (
    CHRONIC_RATIO_THRESHOLD,
    EMERGING_RATIO_THRESHOLD,
    HIGH_PROCRASTINATION_THRESHOLD,
    WEIGHT_DELAY,
    WEIGHT_LATE,
    WEIGHT_RESCHEDULES,
    DASHBOARD_PAYLOADS_PATH,
)
from models.schemas import Task

def load_pt_model():
    if DASHBOARD_PAYLOADS_PATH.exists():
        try:
            import torch
            return torch.load(DASHBOARD_PAYLOADS_PATH, map_location="cpu", weights_only=False)
        except Exception:
            pass
    return None

PT_MODEL = load_pt_model()


def parse_date(date_str: str | None):
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip().replace("Z", "")
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(cleaned, fmt)
            except Exception:
                continue
    return None


def parse_csv_tasks(text: str) -> list[Task]:
    reader = csv.DictReader(io.StringIO(text.strip()))
    tasks = []
    for row in reader:
        c = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}
        reschedules_val = 0
        if c.get("reschedules"):
            try:
                reschedules_val = int(c.get("reschedules"))
            except ValueError:
                reschedules_val = 0
        tasks.append(Task(
            task_id=c.get("task_id", ""),
            course=c.get("course", ""),
            assigned=c.get("assigned", ""),
            due=c.get("due", ""),
            first_activity=c.get("first_activity") or None,
            submitted=c.get("submitted") or None,
            reschedules=reschedules_val,
        ))
    return tasks


def calculate_fallback(tasks: list[Task]):
    scores = []
    high_count = 0
    onset_task = None
    streak = 0

    for t in tasks:
        assigned_dt = parse_date(t.assigned)
        due_dt = parse_date(t.due)
        first_act_dt = parse_date(t.first_activity)
        sub_dt = parse_date(t.submitted)

        start_delay_ratio = 0.5
        if assigned_dt and due_dt and (due_dt > assigned_dt):
            total_sec = (due_dt - assigned_dt).total_seconds()
            if first_act_dt and first_act_dt >= assigned_dt:
                act_sec = (first_act_dt - assigned_dt).total_seconds()
                start_delay_ratio = min(1.0, max(0.0, act_sec / total_sec))
            elif first_act_dt:
                start_delay_ratio = 0.0

        is_late = False
        if sub_dt and due_dt:
            is_late = sub_dt > due_dt
        elif not sub_dt:
            is_late = True

        reschedules = t.reschedules or 0
        w_delay = PT_MODEL.get("WEIGHT_DELAY", WEIGHT_DELAY) if isinstance(PT_MODEL, dict) else WEIGHT_DELAY
        w_late = PT_MODEL.get("WEIGHT_LATE", WEIGHT_LATE) if isinstance(PT_MODEL, dict) else WEIGHT_LATE
        w_reschedules = PT_MODEL.get("WEIGHT_RESCHEDULES", WEIGHT_RESCHEDULES) if isinstance(PT_MODEL, dict) else WEIGHT_RESCHEDULES
        delay_score = start_delay_ratio * w_delay
        late_score = w_late if is_late else 0.0
        reschedule_score = min(w_reschedules, reschedules * 0.07)
        score = delay_score + late_score + reschedule_score
        score = round(min(1.0, max(0.0, score)), 2)
        is_procrastinated = score >= HIGH_PROCRASTINATION_THRESHOLD
        if is_procrastinated:
            high_count += 1
            streak += 1
            if streak >= 2 and onset_task is None:
                onset_task = t.task_id
        else:
            streak = 0
        scores.append({
            "task_id": t.task_id,
            "course": t.course,
            "score": score,
            "start_delay_ratio": round(start_delay_ratio, 2),
            "is_late": is_late,
            "reschedules": reschedules,
        })

    total = len(tasks)
    if total == 0:
        label = "none"
    else:
        ratio = high_count / total
        if ratio >= CHRONIC_RATIO_THRESHOLD:
            label = "chronic"
            if not onset_task and scores:
                onset_task = scores[0]["task_id"]
        elif ratio >= EMERGING_RATIO_THRESHOLD or (onset_task is not None):
            label = "emerging"
            if not onset_task:
                for s in scores:
                    if s["score"] >= HIGH_PROCRASTINATION_THRESHOLD:
                        onset_task = s["task_id"]
                        break
        else:
            label = "none"
            onset_task = None

    if label == "chronic":
        explanation = f"Frequent last-minute starts, delays, or rescheduled deadlines detected across multiple assignments (starting around task {onset_task or 'early assignments'})."
    elif label == "emerging":
        explanation = f"Student started with steady habits, but procrastination patterns began appearing around task {onset_task or 'recent assignments'}."
    else:
        explanation = "Assignments were started in advance and submitted on time with little to no postponement."

    return scores, label, onset_task, explanation


def try_parse_model_response(raw_text: str | None):
    if not raw_text:
        return None
    try:
        return json.loads(raw_text.strip())
    except Exception:
        pass

    if "{" in raw_text and "}" in raw_text:
        try:
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            return json.loads(raw_text[start:end])
        except Exception:
            pass
    return None


def analyze_student_history(tasks: list[Task], user_id: int | None = None):
    fb_scores, fb_label, fb_onset, fb_explanation = calculate_fallback(tasks)
    model_classified = False
    label = None
    onset_task = None
    explanation = None

    try:
        tasks_json = json.dumps([t.model_dump() for t in tasks], indent=2)
        prompt = (
            f"Analyze the student's task history for academic procrastination.\n"
            f"User ID: {user_id if user_id is not None else 'N/A'}\n"
            f"Tasks:\n{tasks_json}\n\n"
            "Classify the student's procrastination pattern. Return JSON format with:\n"
            "{\n"
            '  "label": "none" | "emerging" | "chronic",\n'
            '  "onset_task": "<task_id or null>",\n'
            '  "explanation": "<explanation of procrastination pattern>"\n'
            "}"
        )

        res = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

        raw_output = None
        if isinstance(res, dict) and "messages" in res and res["messages"]:
            last_msg = res["messages"][-1]
            raw_output = getattr(last_msg, "content", None)
        elif isinstance(res, str):
            raw_output = res

        parsed = try_parse_model_response(raw_output)
        if parsed and isinstance(parsed, dict) and parsed.get("label"):
            candidate_label = str(parsed["label"]).lower().strip()
            if candidate_label in ("none", "emerging", "chronic"):
                label = candidate_label
                onset_task = parsed.get("onset_task")
                explanation = parsed.get("explanation")
                model_classified = True
    except Exception:
        pass
    if not model_classified or not label:
        label = fb_label
        onset_task = fb_onset
        explanation = fb_explanation

    return {
        "user_id": user_id,
        "label": label,
        "onset_task": onset_task,
        "scores": fb_scores,
        "explanation": explanation,
    }
