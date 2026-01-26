"""
Unit tests for CFP Module

Chạy tests: python -m pytest test_cfp_module.py -v
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from services.conference_service import ConferenceService
from services.track_service import TrackService
from services.email_template_service import EmailTemplateService, EmailLogService
from infrastructure.repositories.conference_repository import ConferenceRepository
from infrastructure.repositories.track_repository import TrackRepository
from infrastructure.repositories.email_template_repository import EmailTemplateRepository, EmailLogRepository


class TestConferenceService(unittest.TestCase):
    """Test ConferenceService"""
    
    def setUp(self):
        self.mock_repository = Mock(spec=ConferenceRepository)
        self.service = ConferenceService(self.mock_repository)
    
    def test_create_conference_success(self):
        """Test tạo hội nghị thành công"""
        data = {
            'tenant_id': 1,
            'name': 'ICSE 2026',
            'short_name': 'ICSE-2026',
            'description': 'Test conference'
        }
        
        self.mock_repository.get_by_short_name.return_value = None
        mock_conference = Mock()
        mock_conference.id = 1
        self.mock_repository.create.return_value = mock_conference
        
        result = self.service.create_conference(data)
        
        self.assertIsNotNone(result)
        self.mock_repository.create.assert_called_once()
    
    def test_create_conference_missing_required_field(self):
        """Test tạo hội nghị không có field bắt buộc"""
        data = {
            'tenant_id': 1,
            'name': 'ICSE 2026'
            # Missing short_name
        }
        
        with self.assertRaises(ValueError):
            self.service.create_conference(data)
    
    def test_create_conference_duplicate_short_name(self):
        """Test tạo hội nghị với short_name trùng"""
        data = {
            'tenant_id': 1,
            'name': 'ICSE 2026',
            'short_name': 'ICSE-2026'
        }
        
        self.mock_repository.get_by_short_name.return_value = Mock()
        
        with self.assertRaises(ValueError):
            self.service.create_conference(data)
    
    def test_get_conference(self):
        """Test lấy hội nghị"""
        mock_conference = Mock()
        self.mock_repository.get_by_id.return_value = mock_conference
        
        result = self.service.get_conference(1)
        
        self.assertEqual(result, mock_conference)
        self.mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_publish_cfp(self):
        """Test publish CFP"""
        mock_conference = Mock()
        self.mock_repository.get_by_id.return_value = mock_conference
        self.mock_repository.update_cfp_content.return_value = mock_conference
        
        result = self.service.publish_cfp(1, "CFP Content")
        
        self.assertIsNotNone(result)
        self.mock_repository.update_cfp_content.assert_called_once()
    
    def test_is_cfp_open_when_closed(self):
        """Test CFP không mở (deadline đã qua)"""
        mock_conference = Mock()
        mock_conference.cfp_is_public = True
        mock_conference.status = 'open'
        mock_conference.submission_deadline = datetime.utcnow() - timedelta(days=1)
        
        self.mock_repository.get_by_id.return_value = mock_conference
        
        result = self.service.is_cfp_open(1)
        
        self.assertFalse(result)
    
    def test_is_cfp_open_when_active(self):
        """Test CFP mở"""
        mock_conference = Mock()
        mock_conference.cfp_is_public = True
        mock_conference.status = 'open'
        mock_conference.submission_deadline = datetime.utcnow() + timedelta(days=30)
        
        self.mock_repository.get_by_id.return_value = mock_conference
        
        result = self.service.is_cfp_open(1)
        
        self.assertTrue(result)


class TestTrackService(unittest.TestCase):
    """Test TrackService"""
    
    def setUp(self):
        self.mock_repository = Mock(spec=TrackRepository)
        self.service = TrackService(self.mock_repository)
    
    def test_create_track_success(self):
        """Test tạo track thành công"""
        data = {
            'conference_id': 1,
            'name': 'Software Architecture'
        }
        
        self.mock_repository.get_by_name.return_value = None
        mock_track = Mock()
        mock_track.id = 1
        self.mock_repository.create.return_value = mock_track
        
        result = self.service.create_track(data)
        
        self.assertIsNotNone(result)
        self.mock_repository.create.assert_called_once()
    
    def test_list_conference_tracks(self):
        """Test lấy danh sách tracks của hội nghị"""
        mock_tracks = [Mock(), Mock()]
        self.mock_repository.get_by_conference.return_value = mock_tracks
        
        result = self.service.list_conference_tracks(1)
        
        self.assertEqual(len(result), 2)
        self.mock_repository.get_by_conference.assert_called_once_with(1)
    
    def test_is_track_submission_open(self):
        """Test kiểm tra track submission mở"""
        mock_track = Mock()
        mock_track.is_active = True
        mock_track.submission_deadline = datetime.utcnow() + timedelta(days=10)
        
        self.mock_repository.get_by_id.return_value = mock_track
        
        result = self.service.is_track_submission_open(1)
        
        self.assertTrue(result)


class TestEmailTemplateService(unittest.TestCase):
    """Test EmailTemplateService"""
    
    def setUp(self):
        self.mock_template_repo = Mock(spec=EmailTemplateRepository)
        self.mock_log_repo = Mock(spec=EmailLogRepository)
        self.service = EmailTemplateService(self.mock_template_repo, self.mock_log_repo)
    
    def test_create_template_success(self):
        """Test tạo email template thành công"""
        data = {
            'template_type': 'submission_confirmation',
            'name': 'Submission Confirmation',
            'subject': 'Paper Submitted',
            'body_html': '<p>Dear {{author_name}},</p>'
        }
        
        mock_template = Mock()
        mock_template.id = 1
        self.mock_template_repo.create.return_value = mock_template
        
        result = self.service.create_template(data)
        
        self.assertIsNotNone(result)
        self.mock_template_repo.create.assert_called_once()
    
    def test_render_template(self):
        """Test render email template"""
        mock_template = Mock()
        mock_template.subject = "Hello {{name}}"
        mock_template.body_html = "<p>Dear {{name}}, Welcome to {{conference}}!</p>"
        
        self.mock_template_repo.get_by_id.return_value = mock_template
        
        placeholders = {
            'name': 'John Doe',
            'conference': 'ICSE 2026'
        }
        
        subject, body = self.service.render_template(1, placeholders)
        
        self.assertEqual(subject, "Hello John Doe")
        self.assertIn("John Doe", body)
        self.assertIn("ICSE 2026", body)
    
    def test_get_available_placeholders(self):
        """Test lấy danh sách placeholders"""
        placeholders = self.service.get_available_placeholders('submission_confirmation')
        
        self.assertIn('author_name', placeholders)
        self.assertIn('paper_title', placeholders)
        self.assertIn('conference_name', placeholders)


class TestEmailLogService(unittest.TestCase):
    """Test EmailLogService"""
    
    def setUp(self):
        self.mock_repository = Mock(spec=EmailLogRepository)
        self.service = EmailLogService(self.mock_repository)
    
    def test_log_email_success(self):
        """Test ghi nhật ký email"""
        data = {
            'recipient_email': 'test@example.com',
            'subject': 'Test Email'
        }
        
        mock_log = Mock()
        mock_log.id = 1
        mock_log.status = 'pending'
        self.mock_repository.create.return_value = mock_log
        
        result = self.service.log_email(data)
        
        self.assertIsNotNone(result)
        self.mock_repository.create.assert_called_once()
    
    def test_mark_as_sent(self):
        """Test đánh dấu email đã gửi"""
        mock_log = Mock()
        mock_log.status = 'sent'
        self.mock_repository.update_status.return_value = mock_log
        
        result = self.service.mark_as_sent(1)
        
        self.assertEqual(result.status, 'sent')
        self.mock_repository.update_status.assert_called_once()
    
    def test_mark_as_failed(self):
        """Test đánh dấu email thất bại"""
        mock_log = Mock()
        mock_log.status = 'failed'
        self.mock_repository.update_status.return_value = mock_log
        
        result = self.service.mark_as_failed(1, "Email address invalid")
        
        self.assertEqual(result.status, 'failed')


if __name__ == '__main__':
    unittest.main()
