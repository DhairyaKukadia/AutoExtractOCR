from datetime import datetime, timedelta

import pytest

from app.config.constants import Role
from app.data.models import User
from app.data.repositories.record_repository import RecordRepository
from app.services.auth_service import AuthService
from app.services.record_service import RecordService
from tests.conftest import make_test_session


def _create_user(session, username='creator'):
    auth = AuthService(session)
    user = User(
        username=username,
        password_hash=auth.hash_password('Password123'),
        full_name='Creator',
        role=Role.ADMIN,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_save_record_creates_fields_and_metadata():
    session = make_test_session()
    user = _create_user(session)
    service = RecordService(session)

    record = service.save_record(
        form_category='Prescription',
        source_file_name='file1.png',
        source_file_path='C:/tmp/file1.png',
        raw_ocr_text='Patient Name: A',
        extracted_fields={'patient_name': 'A', 'patient_identifier': 'ID-1', 'form_type': 'X'},
        status='reviewed',
        created_by=user.id,
        reviewed_by=user.id,
    )

    assert record.id is not None
    assert record.patient_identifier == 'ID-1'
    assert len(record.fields) == 3


def test_update_record_replaces_field_rows():
    session = make_test_session()
    user = _create_user(session)
    service = RecordService(session)

    created = service.save_record(
        form_category='Prescription',
        source_file_name='file1.png',
        source_file_path='C:/tmp/file1.png',
        raw_ocr_text='old',
        extracted_fields={'patient_name': 'Old', 'patient_identifier': 'ID-1', 'form_type': 'A'},
        status='draft',
        created_by=user.id,
    )

    updated = service.update_record(
        record_id=created.id,
        extracted_fields={'patient_name': 'New', 'patient_identifier': 'ID-2', 'form_type': 'B'},
        raw_ocr_text='new',
        status='approved',
        reviewed_by=user.id,
    )

    assert updated.patient_name == 'New'
    assert updated.review_status == 'approved'
    assert len(updated.fields) == 3


def test_update_record_missing_record_raises_value_error():
    session = make_test_session()
    service = RecordService(session)

    with pytest.raises(ValueError, match='Record not found'):
        service.update_record(
            record_id=9999,
            extracted_fields={'patient_name': 'Missing'},
            raw_ocr_text='missing',
            status='approved',
            reviewed_by=1,
        )


def test_record_repository_filters_status_and_date_to():
    session = make_test_session()
    user = _create_user(session)
    service = RecordService(session)
    repo = RecordRepository(session)

    approved_old = service.save_record(
        form_category='Prescription',
        source_file_name='approved-old.png',
        source_file_path='x',
        raw_ocr_text='x',
        extracted_fields={'patient_name': 'Old Approved', 'patient_identifier': 'A1', 'form_type': 'Lab'},
        status='approved',
        created_by=user.id,
    )
    approved_recent = service.save_record(
        form_category='Prescription',
        source_file_name='approved-recent.png',
        source_file_path='x',
        raw_ocr_text='x',
        extracted_fields={'patient_name': 'Recent Approved', 'patient_identifier': 'A2', 'form_type': 'Lab'},
        status='approved',
        created_by=user.id,
    )
    rejected_old = service.save_record(
        form_category='Prescription',
        source_file_name='rejected-old.png',
        source_file_path='x',
        raw_ocr_text='x',
        extracted_fields={'patient_name': 'Old Rejected', 'patient_identifier': 'R1', 'form_type': 'Lab'},
        status='rejected',
        created_by=user.id,
    )

    approved_old.created_at = datetime.utcnow() - timedelta(days=30)
    approved_recent.created_at = datetime.utcnow() - timedelta(days=1)
    rejected_old.created_at = datetime.utcnow() - timedelta(days=30)
    session.commit()

    cutoff = datetime.utcnow() - timedelta(days=10)
    records = repo.list_records(status='approved', date_to=cutoff)

    returned_ids = {record.id for record in records}
    assert approved_old.id in returned_ids
    assert approved_recent.id not in returned_ids
    assert rejected_old.id not in returned_ids


def test_record_repository_filters():
    session = make_test_session()
    user = _create_user(session)
    service = RecordService(session)
    repo = RecordRepository(session)

    first = service.save_record(
        form_category='Prescription',
        source_file_name='one.png',
        source_file_path='x',
        raw_ocr_text='x',
        extracted_fields={'patient_name': 'Jane Doe', 'patient_identifier': 'P1', 'form_type': 'Medication'},
        status='approved',
        created_by=user.id,
    )
    service.save_record(
        form_category='Lab Request',
        source_file_name='two.png',
        source_file_path='y',
        raw_ocr_text='y',
        extracted_fields={'patient_name': 'John Roe', 'patient_identifier': 'P2', 'form_type': 'CBC'},
        status='draft',
        created_by=user.id,
    )

    first.created_at = datetime.utcnow() - timedelta(days=2)
    session.commit()

    filtered = repo.list_records(category='Prescription', patient_name='Jane', form_type='Medication')
    assert len(filtered) == 1
    assert filtered[0].form_category == 'Prescription'

    recent = repo.list_records(date_from=datetime.utcnow() - timedelta(days=1))
    assert len(recent) == 1
    assert recent[0].id != first.id
