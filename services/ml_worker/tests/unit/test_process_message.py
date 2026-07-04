from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from src.ai_pipeline.state import PipelineOutput
from src.models import Entity, EntityLabel, SourceType, UnifiedDocument
from src.report import save_report
from src.tasks.process_message import (
    _dedup_entities,
    _merge_documents,
    process_message,
)


class TestDedupEntities:
    def test_removes_duplicates_by_name_and_label(self):
        entities = [
            Entity(name="Ниобий", label=EntityLabel.MATERIAL),
            Entity(name="ниобий", label=EntityLabel.MATERIAL),
            Entity(name="Отжиг", label=EntityLabel.PROCESS),
        ]
        result = _dedup_entities(entities)
        assert len(result) == 2
        labels = [e.label for e in result]
        assert EntityLabel.MATERIAL in labels
        assert EntityLabel.PROCESS in labels


class TestMergeDocuments:
    def test_returns_single_document_unchanged(self):
        doc = UnifiedDocument(
            source_type=SourceType.TEXT,
            source_uri="/app/uploads/test.txt",
            elements=[],
        )
        result = _merge_documents([doc])
        assert result.source_uri == "/app/uploads/test.txt"

    def test_merges_multiple_documents(self):
        doc1 = UnifiedDocument(
            source_type=SourceType.TEXT,
            source_uri="/app/uploads/a.txt",
            elements=[],
        )
        doc2 = UnifiedDocument(
            source_type=SourceType.TEXT,
            source_uri="/app/uploads/b.txt",
            elements=[],
        )
        result = _merge_documents([doc1, doc2])
        assert "/app/uploads/a.txt" in result.source_uri
        assert "/app/uploads/b.txt" in result.source_uri

    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError, match="No documents to merge"):
            _merge_documents([])


class TestSaveReport:
    async def test_creates_json_and_html_files(self, tmp_path):
        report_dir = tmp_path / "reports"
        with patch("src.report.settings") as mock_settings:
            mock_settings.report_dir = str(report_dir)

            output = PipelineOutput()
            result_path = await save_report("sess_abc", "msg_def", output)

            json_file = report_dir / "sess_abc" / "msg_def.json"
            html_file = report_dir / "sess_abc" / "msg_def.html"

            assert Path(result_path) == json_file
            assert json_file.exists()
            assert html_file.exists()

            data = json.loads(json_file.read_text(encoding="utf-8"))
            assert "hypothesis" in data
            assert "review" in data
            assert "graph" in data


class TestProcessMessage:
    @patch("src.tasks.process_message.download_file")
    @patch("src.tasks.process_message.extract_document")
    @patch("src.tasks.process_message.extract_entities")
    @patch("src.tasks.process_message.run_pipeline")
    @patch("src.tasks.process_message.save_report")
    @patch("src.tasks.process_message.SessionLocal")
    def test_processes_first_message_successfully(
        self,
        mock_session_local,
        mock_save_report,
        mock_run_pipeline,
        mock_extract_entities,
        mock_extract_document,
        mock_download_file,
    ):
        mock_download_file.side_effect = lambda x: x
        mock_extract_document.return_value = UnifiedDocument(
            source_type=SourceType.TEXT,
            source_uri="/app/uploads/sess_abc/file.pdf",
            elements=[],
        )
        mock_extract_entities.return_value = []

        fake_hypothesis = MagicMock()
        fake_hypothesis.hypothesis = "test hypothesis"
        fake_hypothesis.model_dump_json.return_value = "{}"

        fake_review = MagicMock()
        fake_review.model_dump_json.return_value = "{}"

        fake_graph = MagicMock()
        fake_graph.model_dump_json.return_value = "{}"

        fake_output = MagicMock()
        fake_output.hypothesis = fake_hypothesis
        fake_output.review = fake_review
        fake_output.graph = fake_graph
        fake_output.model_dump.return_value = {
            "hypothesis": {},
            "review": {},
            "graph": {},
        }
        mock_run_pipeline.return_value = fake_output
        mock_save_report.return_value = "/reports/sess_abc/msg_def.json"

        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db

        fake_session = MagicMock()
        fake_session.weights = {"novelty": 1.0}
        fake_session.constraints = "budget 5M"
        fake_session.status = "created"
        mock_db.get.side_effect = [
            fake_session,
            None,
            fake_session,
            fake_session,
        ]

        fake_message = MagicMock()
        fake_message.status = "queued"
        fake_message.content = ""
        mock_db.get.side_effect = [
            fake_session,
            fake_message,
            fake_session,
            fake_message,
            fake_session,
        ]

        result = process_message.run(
            user_id="usr_1",
            uuid="sess_abc",
            message_id="msg_def",
            first_message=True,
            upload_files=["/app/uploads/sess_abc/file.pdf"],
            prompt="test problem",
        )

        assert result is not None
        mock_run_pipeline.assert_called_once()
        mock_save_report.assert_called_once()

        call_args = mock_run_pipeline.call_args[0][0]
        assert call_args.session_id == "sess_abc"
        assert call_args.problem == "test problem"
        assert call_args.constraints == "budget 5M"
        assert call_args.weights == {"novelty": 1.0}
        assert call_args.iteration == 0
        assert call_args.feedback is None
