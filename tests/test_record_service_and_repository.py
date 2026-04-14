from datetime import datetime, timedelta

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
        status='extracted',
        reviewed_by=user.id,
    )

    assert updated.patient_name == 'New'
    assert updated.review_status == 'extracted'
    assert len(updated.fields) == 3


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


def test_update_record_status_rejects_invalid_transition():
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

    try:
        service.update_record_status(created.id, 'approved', reviewed_by=user.id)
        assert False, 'Expected ValueError for invalid transition'
    except ValueError as exc:
        assert 'Invalid status transition' in str(exc)


def test_update_record_rejects_invalid_transition():
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

    try:
        service.update_record(
            record_id=created.id,
            extracted_fields={'patient_name': 'New', 'patient_identifier': 'ID-2', 'form_type': 'B'},
            raw_ocr_text='new',
            status='approved',
            reviewed_by=user.id,
        )
        assert False, 'Expected ValueError for invalid transition'
    except ValueError as exc:
        assert 'Invalid status transition' in str(exc)
