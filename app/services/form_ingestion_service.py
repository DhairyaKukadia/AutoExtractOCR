from __future__ import annotations

from sqlalchemy import select

from app.data.form_models import (
    BloodCompatibilityTest,
    BloodComponentRequest,
    BloodIssueRecord,
    BloodRequestForm,
    BloodRequestType,
    BloodReserveRecord,
    ClinicalChemistryForm,
    ClinicalChemistryTest,
    MasterForm,
    PathologyHematologyForm,
    PathologyHematologyTest,
)
from app.data.form_payloads import (
    BloodRequestDetailPayload,
    ClinicalChemistryDetailPayload,
    MasterFormPayload,
    PathologyHematologyDetailPayload,
)
from app.utils.uid import generate_record_uid


class FormIngestionService:
    """Service layer for transaction-safe insertion of the three selected form types."""

    def __init__(self, session):
        self.session = session

    def insert_pathology_hematology(
        self,
        master_payload: MasterFormPayload,
        detail_payload: PathologyHematologyDetailPayload,
    ) -> tuple[int, str]:
        if master_payload.form_type != 'pathology_hematology':
            raise ValueError('master_payload.form_type must be pathology_hematology')

        with self.session.begin_nested():
            master = self._create_master(master_payload)
            detail_data = detail_payload.model_dump(exclude={'tests'})
            detail = PathologyHematologyForm(master_id=master.master_id, **detail_data)
            self.session.add(detail)
            self.session.flush()

            for test in detail_payload.tests:
                self.session.add(PathologyHematologyTest(pathology_id=detail.pathology_id, **test.model_dump()))

        self.session.commit()
        return master.master_id, master.record_uid

    def insert_clinical_chemistry(
        self,
        master_payload: MasterFormPayload,
        detail_payload: ClinicalChemistryDetailPayload,
    ) -> tuple[int, str]:
        if master_payload.form_type != 'clinical_chemistry':
            raise ValueError('master_payload.form_type must be clinical_chemistry')

        with self.session.begin_nested():
            master = self._create_master(master_payload)
            detail_data = detail_payload.model_dump(exclude={'tests'})
            detail = ClinicalChemistryForm(master_id=master.master_id, **detail_data)
            self.session.add(detail)
            self.session.flush()

            for test in detail_payload.tests:
                self.session.add(ClinicalChemistryTest(chemistry_id=detail.chemistry_id, **test.model_dump()))

        self.session.commit()
        return master.master_id, master.record_uid

    def insert_blood_request(
        self,
        master_payload: MasterFormPayload,
        detail_payload: BloodRequestDetailPayload,
    ) -> tuple[int, str]:
        if master_payload.form_type != 'blood_request':
            raise ValueError('master_payload.form_type must be blood_request')

        with self.session.begin_nested():
            master = self._create_master(master_payload)
            detail_data = detail_payload.model_dump(
                exclude={'request_types', 'component_requests', 'reserve_records', 'compatibility_test', 'issue_records'}
            )
            detail = BloodRequestForm(master_id=master.master_id, **detail_data)
            self.session.add(detail)
            self.session.flush()

            for item in detail_payload.request_types:
                self.session.add(BloodRequestType(blood_request_id=detail.blood_request_id, **item.model_dump()))

            for item in detail_payload.component_requests:
                self.session.add(BloodComponentRequest(blood_request_id=detail.blood_request_id, **item.model_dump()))

            for item in detail_payload.reserve_records:
                self.session.add(BloodReserveRecord(blood_request_id=detail.blood_request_id, **item.model_dump()))

            if detail_payload.compatibility_test:
                self.session.add(
                    BloodCompatibilityTest(
                        blood_request_id=detail.blood_request_id,
                        **detail_payload.compatibility_test.model_dump(),
                    )
                )

            for item in detail_payload.issue_records:
                self.session.add(BloodIssueRecord(blood_request_id=detail.blood_request_id, **item.model_dump()))

        self.session.commit()
        return master.master_id, master.record_uid

    def search_by_patient_name(self, patient_name: str) -> list[MasterForm]:
        stmt = select(MasterForm).where(MasterForm.patient_name.ilike(f'%{patient_name}%')).order_by(MasterForm.upload_datetime.desc())
        return list(self.session.scalars(stmt))

    def search_by_mrd_no(self, mrd_no: str) -> list[MasterForm]:
        stmt = select(MasterForm).where(MasterForm.mrd_no.ilike(f'%{mrd_no}%')).order_by(MasterForm.upload_datetime.desc())
        return list(self.session.scalars(stmt))

    def search_by_form_type(self, form_type: str) -> list[MasterForm]:
        stmt = select(MasterForm).where(MasterForm.form_type == form_type).order_by(MasterForm.upload_datetime.desc())
        return list(self.session.scalars(stmt))

    def _create_master(self, payload: MasterFormPayload) -> MasterForm:
        data = payload.model_dump()
        record_uid = generate_record_uid(payload.form_type)
        master = MasterForm(record_uid=record_uid, **data)
        self.session.add(master)
        self.session.flush()
        return master
