"""Offline aggregate report from operator-authorised R2 downloads.

Does not join gaps, feedback or usage at participant level. Highest weekly
usage revisions replace earlier snapshots; repeated uploads never add counts.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from benchside.domain.export.model.metascience import ActivityPayload, SurveyPayload
from benchside.domain.export.model.reporting import FeedbackPayload, UsagePayload
from benchside.domain.export.model.wire import validate_payload
from benchside.domain.shared.error import BenchsideError


def summarise(files):
    gaps, feedback, usage, surveys, activity = {}, {}, {}, {}, {}
    invalid, conflicts = 0, set()
    for path in files:
        try:
            text = Path(path).read_text(encoding="utf-8")
            data = json.loads(text)
            schema = data.get("schema")
            if schema == "benchside.gaps.v1":
                for item in validate_payload(text)["observations"]:
                    previous = gaps.get(item["id"])
                    if previous is not None and previous != item:
                        conflicts.add(("gaps", item["id"]))
                    gaps[item["id"]] = item
            elif schema == "benchside.feedback.v1":
                parsed = FeedbackPayload.model_validate_json(text)
                existing = feedback.get(parsed.feedback.id)
                if existing is not None and existing != parsed:
                    conflicts.add(("feedback", parsed.feedback.id))
                feedback[parsed.feedback.id] = parsed
            elif schema == "benchside.usage.v1":
                parsed = UsagePayload.model_validate_json(text)
                key = (parsed.installation_id, parsed.week)
                previous = usage.get(key)
                if previous and previous.revision == parsed.revision and previous != parsed:
                    conflicts.add(("usage", *key, parsed.revision))
                if previous is None or parsed.revision > previous.revision:
                    usage[key] = parsed
            elif schema == "benchside.survey.v1":
                parsed = SurveyPayload.model_validate_json(text)
                previous = surveys.get(parsed.response_id)
                if previous and previous != parsed:
                    conflicts.add(("survey", parsed.response_id))
                surveys[parsed.response_id] = parsed
            elif schema == "benchside.activity.v1":
                parsed = ActivityPayload.model_validate_json(text)
                previous = activity.get(parsed.batch_id)
                if previous and previous.revision == parsed.revision and previous != parsed:
                    conflicts.add(("activity", parsed.batch_id, parsed.revision))
                if previous is None or parsed.revision > previous.revision:
                    activity[parsed.batch_id] = parsed
            else:
                invalid += 1
        except (BenchsideError, OSError, ValueError, TypeError, AttributeError):
            invalid += 1
    gaps = {k: v for k, v in gaps.items() if ("gaps", k) not in conflicts}
    feedback = {k: v for k, v in feedback.items() if ("feedback", k) not in conflicts}
    usage = {
        key: value
        for key, value in usage.items()
        if ("usage", *key, value.revision) not in conflicts
    }
    surveys = {k: v for k, v in surveys.items() if ("survey", k) not in conflicts}
    activity = {k: v for k, v in activity.items() if ("activity", k, v.revision) not in conflicts}
    survey_counts = Counter()
    activity_counts = Counter()
    for survey in surveys.values():
        for question, answer in survey.answers.items():
            survey_counts[
                f"{survey.study_id}@{survey.study_version}/{survey.study_sha256}/{question}/{answer}"
            ] += 1
    for batch in activity.values():
        for observation in batch.observations:
            for field in ("activity", "obstacle", "verification", "outcome"):
                finding = getattr(observation, field)
                activity_counts[f"{field}/{finding.value}/{finding.basis}"] += 1
            activity_counts[f"benchside_role/{observation.benchside_role}"] += 1
            activity_counts[f"host/{observation.host}"] += 1
    active = defaultdict(set)
    uses = Counter()
    weekly = defaultdict(lambda: Counter())
    roles, hosts, app_versions, versions, errors = (
        Counter(),
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    for (installation, week), report in usage.items():
        for row in report.sessions:
            if (
                row.started
                or row.concluded
                or row.abandoned
                or sum(row.records.model_dump().values())
            ):
                active[week].add(installation)
            uses[installation] += row.started
            roles[row.role] += row.started
            hosts[f"{row.host}/{row.surface}"] += row.started
            app_versions[f"{row.host}@{row.app_version}"] += row.started
            versions[f"{report.benchside_version} / {row.role}@{row.role_version}"] += row.started
            for field in ("started", "concluded", "abandoned"):
                weekly[week][field] += getattr(row, field)
        errors.update(report.errors)
    # One demographic entry per participating installation, from its latest accepted
    # weekly snapshot. Never join these categories to gaps, feedback or activity.
    latest = {}
    for (installation, week), report in usage.items():
        previous = latest.get(installation)
        if previous is None or (week, report.revision) > (previous.week, previous.revision):
            latest[installation] = report
    demographic_counts = {"discipline": Counter(), "career_stage": Counter()}
    for report in latest.values():
        if report.demographics:
            for field, value in report.demographics.model_dump(exclude_none=True).items():
                demographic_counts[field][value] += 1
    weeks_by_installation = Counter(i for installations in active.values() for i in installations)
    return {
        "workflow_observations": len(gaps),
        "workflow_kinds": dict(sorted(Counter(o["gap"]["kind"] for o in gaps.values()).items())),
        "feedback_submissions": len(feedback),
        "feedback_ease": dict(
            sorted(Counter(str(f.feedback.ease) for f in feedback.values()).items())
        ),
        "feedback_repeat_intent": dict(
            sorted(Counter(f.feedback.would_use_again for f in feedback.values()).items())
        ),
        "demographic_installations": sum(
            bool(r.demographics and r.demographics.model_dump(exclude_none=True))
            for r in latest.values()
        ),
        "installations_by_discipline": dict(sorted(demographic_counts["discipline"].items())),
        "installations_by_career_stage": dict(sorted(demographic_counts["career_stage"].items())),
        "active_installations": len(weeks_by_installation),
        "returning_installations_across_weeks": sum(n >= 2 for n in weeks_by_installation.values()),
        "installations_with_multiple_consultations": sum(n >= 2 for n in uses.values()),
        "weekly": {
            week: {"active_installations": len(active[week]), **dict(weekly[week])}
            for week in sorted(set(active) | set(weekly))
        },
        "consultations_by_role": dict(sorted(roles.items())),
        "consultations_by_app": dict(sorted(hosts.items())),
        "consultations_by_app_version": dict(sorted(app_versions.items())),
        "consultations_by_version": dict(sorted(versions.items())),
        "failures": dict(sorted(errors.items())),
        "survey_submissions": len(surveys),
        "survey_answers": dict(sorted(survey_counts.items())),
        "activity_batches": len(activity),
        "activity_coverage": {
            "eligible_in_submitted_batches": sum(b.eligible for b in activity.values()),
            "selected_in_submitted_batches": sum(b.selected for b in activity.values()),
            "reviewed_and_shared": sum(len(b.observations) for b in activity.values()),
        },
        "activity_findings": dict(sorted(activity_counts.items())),
        "invalid_files": invalid,
        "conflicting_snapshots": len(conflicts),
        "interpretation": "Opt-in installations, not unique people or total adoption. Completion does not establish scientific benefit. Datasets are not linked. Demographic buckets describe optional self-reports from each installation's latest accepted weekly snapshot; they are not population estimates or unique people. Activity coverage describes only submitted batches of user-selected accessible sessions, not all research activity. Model-inferred findings and researcher-reported outcomes are distinct; review and nonresponse introduce selection bias. Validate the classifier on separately consented examples before making accuracy claims. These exploratory rollout findings are separate from the original paper evaluation.",
    }


def markdown(report):
    lines = [
        "# Benchside rollout report",
        "",
        report["interpretation"],
        "",
        f"- Active installations: {report['active_installations']}",
        f"- Returning across weeks: {report['returning_installations_across_weeks']}",
        f"- Multiple consultations: {report['installations_with_multiple_consultations']}",
        f"- Workflow observations: {report['workflow_observations']}",
        f"- Feedback submissions: {report['feedback_submissions']}",
        f"- Survey submissions: {report['survey_submissions']}",
        f"- Research activity batches: {report['activity_batches']}",
        f"- Invalid files: {report['invalid_files']}; conflicting snapshots: {report['conflicting_snapshots']}",
    ]
    for label, key in [
        ("Weekly activity", "weekly"),
        ("Workflow problems", "workflow_kinds"),
        ("Optional discipline buckets (installations)", "installations_by_discipline"),
        ("Optional career-stage buckets (installations)", "installations_by_career_stage"),
        ("Roles used", "consultations_by_role"),
        ("Apps used", "consultations_by_app"),
        ("App versions", "consultations_by_app_version"),
        ("Versions", "consultations_by_version"),
        ("Ease of use (1–5)", "feedback_ease"),
        ("Would use again", "feedback_repeat_intent"),
        ("Failures", "failures"),
        ("Survey answers (study/version/definition/question/answer)", "survey_answers"),
        ("Activity sampling coverage", "activity_coverage"),
        ("Activity findings and evidence basis", "activity_findings"),
    ]:
        lines += ["", f"## {label}", "", "| Measure | Count |", "|---|---|"]
        for name, value in report[key].items():
            rendered = (
                ", ".join(f"{k}: {v}" for k, v in value.items())
                if isinstance(value, dict)
                else str(value)
            )
            lines.append(f"| {name} | {rendered} |")
        if not report[key]:
            lines.append("| No reports yet | — |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    files = sorted(
        {
            p
            for source in args.inputs
            for p in (source.rglob("*.json") if source.is_dir() else [source])
        }
    )
    report = summarise(files)
    print(json.dumps(report, indent=2) if args.json else markdown(report))


if __name__ == "__main__":
    main()
