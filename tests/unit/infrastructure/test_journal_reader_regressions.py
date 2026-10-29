import pytest

from benchside.domain.consultation.event.opened import ConsultationOpened
from benchside.domain.shared.model.ids import PersonaId, ProjectId


@pytest.mark.parametrize("reader", ["read", "read_envelopes"])
def test_non_object_journal_lines_are_skipped_and_logged(paths, journal, caplog, reader):
    project = ProjectId("synthetic")
    event = ConsultationOpened(
        id="event-1", consultation_id="consultation-1", project_id=project,
        persona_id=PersonaId("pi"),
    )
    journal.append(project, event)
    path = paths.journal_file(project.root)
    original = path.read_text()
    path.write_text(original + 'null\n123\n["private text must not enter a log"]\n' + original)
    before = path.read_bytes()

    records = list(getattr(journal, reader)(project))

    assert len(records) == 2
    assert path.read_bytes() == before
    assert len(caplog.records) == 3
    assert all("Skipping unreadable journal line" in record.message for record in caplog.records)
    assert "private text" not in caplog.text
