# pylint: disable=too-many-lines, invalid-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
"""
All eol tests
"""

from __future__ import absolute_import

import json

import ddt

from django.contrib.auth import get_user_model
from django.urls import reverse

from edx_proctoring.models import ProctoredExam
from edx_proctoring.runtime import set_runtime_service

from .test_services import MockCreditService, MockInstructorService
from .utils import LoggedInTestCase

User = get_user_model()


@ddt.ddt
class TestEOLStudentProctoredExamAttempt(LoggedInTestCase):

    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.save()
        self.second_user = User(username='tester2', email='tester2@test.com')
        self.second_user.save()
        self.client.login_user(self.user)
        self.student_taking_exam = User()
        self.student_taking_exam.save()

        set_runtime_service('credit', MockCreditService())
        set_runtime_service('instructor', MockInstructorService(is_user_course_staff=True))

    def test_eol_get_proctored_exam(self):
        """
            EOL MODIFICATION
            Test and check if get proctored exam is returning the new attributes
            (content_id, block_types_filter, username)
        """
        # Create an exam.
        proctored_exam = ProctoredExam.objects.create(
            course_id='a/b/c',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )
        response = self.client.get(
            reverse('edx_proctoring:proctored_exam.attempt.collection')
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertNotIn('exam_display_name', data)

        # Initialize exam
        attempt_data = {
            'exam_id': proctored_exam.id,
            'user_id': self.user.id,
            'external_id': proctored_exam.external_id,
            'start_clock': True
        }
        response = self.client.post(
            reverse('edx_proctoring:proctored_exam.attempt.collection'),
            attempt_data
        )
        self.assertEqual(response.status_code, 200)

        # Check new attributes
        response = self.client.get(
            reverse('edx_proctoring:proctored_exam.attempt.collection')
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('content_id', data)
        self.assertIn('block_types_filter', data)
        self.assertIn('username', data)
