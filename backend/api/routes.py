import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from agent.audit_agent import audit_pitch
from agent.company_agent import build_company_profile
from agent.pitch_agent import generate_pitch
from rag.extraction import extract_text_from_pdf, validate_extraction
from rag.chunking import chunk_pages
from rag.embeddings import embed_chunks
from rag.index import build_index
from rag.retrieval import build_policy_profile
from service.audit_report import generate_audit_report
from service.pitch_generator import generate_pptx

from config import (
    UPLOADS_DIR, GENERATED_DIR,
    ABHI_DATA_DIR, CARE_DATA_DIR, HDFC_DATA_DIR, NIVA_DATA_DIR, TEMP_DATA_DIR
)

BASELINE_POLICIES = {
    "abhi": {
        "provider": "ABHI",
        "product_name": None,
        "document": "ABHI Product Brochure.pdf",
        "index_dir": ABHI_DATA_DIR,
    },
    "care": {
        "provider": "Care Health",
        "product_name": None,
        "document": "Care Health Product Brochure.pdf",
        "index_dir": CARE_DATA_DIR,
    },
    "hdfc": {
        "provider": "HDFC ERGO",
        "product_name": None,
        "document": "HDFC Product Brochure.pdf",
        "index_dir": HDFC_DATA_DIR,
    },
    "niva": {
        "provider": "Niva Bupa",
        "product_name": "ReAssure 2.0",
        "document": "Niva Bupa Product Brochure.pdf",
        "index_dir": NIVA_DATA_DIR,
    },
}

router = APIRouter(prefix='/api')

@router.get("/policies")
def list_policies():
    return [
        {
            "id": policy_id,
            "provider": policy["provider"],
            "product_name": policy["product_name"],
            "document": policy["document"],
        }
        for policy_id, policy in BASELINE_POLICIES.items()
    ]

def _save_upload(upload: UploadFile, upload_id: str) -> Path:
    if not upload.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    if not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF policy documents are supported.",
        )

    upload_path = UPLOADS_DIR / f"{upload_id}.pdf"

    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    return upload_path

def _build_custom_policy_index(pdf_path: Path, upload_id: str) -> Path:

    index_dir = TEMP_DATA_DIR / f"custom_{upload_id}"

    pages = extract_text_from_pdf(pdf_path)
    validate_extraction(pages=pages)

    chunks = chunk_pages(pages=pages, document_name=pdf_path.name)
    if not chunks:
        raise ValueError("No chunks could be created from the uploaded PDF.")

    embeddings = embed_chunks(chunks=chunk_pages)

    build_index(chunks=chunks, embeddings=embeddings, output_dir=index_dir)

    return index_dir

@router.post("/generate")
async def generate(
    company_name: str = Form(...),
    policy_id: str | None = Form(None),
    policy_pdf: UploadFile | None = File(None)
):
    company_name = company_name.strip()
    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Company name is required.",
        )

    upload_id = None
    if policy_pdf is not None:
        upload_id = str(uuid.uuid4())

        try:
            pdf_path = _save_upload(upload=policy_pdf, upload_id=upload_id)
            index_dir = _build_custom_policy_index(pdf_path=pdf_path, upload_id=upload_id)

            provider = Path(policy_pdf.filename).stem
            product_name = None
            document = policy_pdf.filename

        except HTTPException:
            raise

        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process policy PDF",
            ) 
    else:
        if not policy_id:
            raise HTTPException(
                status_code=400,
                detail="Select a policy or upload a custom policy PDF.",
            )

        policy = BASELINE_POLICIES.get(policy_id.lower())

        if policy is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown policy: {policy_id}",
            )

        index_dir = policy["index_dir"]
        provider = policy["provider"]
        product_name = policy["product_name"]
        document = policy["document"]

        if not index_dir.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Policy index not found for '{policy_id}'. "
                    "Build the baseline indexes first."
                ),
            )

    # 1. Company research

    try:
        company = build_company_profile(company_name)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Company research failed",
        )

    # 2. Policy retrieval

    try:
        policy_profile = build_policy_profile(
            company=company,
            provider=provider,
            product_name=product_name,
            document=document,
            index_dir=index_dir,
            top_k_per_query=3,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Policy retrieval failed: {exc}",
        ) from exc

    # ---------------------------------------------------------------
    # 3. Generate PitchContent

    try:
        pitch = generate_pitch(
            company=company,
            policy=policy_profile,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Pitch generation failed",
        ) 

    # 4. Generate PPTX
    #
    # IMPORTANT:
    # The audit does not modify the pitch.

    job_id = uuid.uuid4().hex

    pptx_path = GENERATED_DIR / f"{job_id}_Client_Pitch.pptx"

    try:
        generate_pptx(
            pitch=pitch,
            output_path=pptx_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PPTX generation failed",
        ) 

    # 5. Independent claim audit

    try:
        audit = audit_pitch(
            pitch=pitch,
            policy_index_dir=index_dir,
            top_k=3,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Pitch audit failed",
        ) 

    # 6. Generate audit DOCX

    audit_path = GENERATED_DIR / f"{job_id}_Audit_Report.docx"

    try:
        generate_audit_report(
            audit=audit,
            output_path=audit_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Audit report generation failed",
        ) 

    # Response

    return {
        "job_id": job_id,
        "company": company.model_dump(),
        "policy": {
            "provider": provider,
            "product_name": product_name,
            "document": document,
        },
        "pitch": pitch.model_dump(),
        "audit": {
            "total_claims": audit.total_claims,
            "supported_claims": audit.supported_claims,
            "partially_supported_claims": audit.partially_supported_claims,
            "unsupported_claims": audit.unsupported_claims,
            "audit_passed": audit.audit_passed,
        },
        "files": {
            "pptx": f"/api/download/{job_id}/pptx",
            "audit_report": f"/api/download/{job_id}/audit",
        },
    }


@router.get("/download/{job_id}/pptx")
def download_pptx(job_id: str):
    path = GENERATED_DIR / f"{job_id}_Client_Pitch.pptx"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="PPTX file not found.",
        )

    return FileResponse(
        path=path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
        filename="Client_Pitch.pptx",
    )


@router.get("/download/{job_id}/audit")
def download_audit_report(job_id: str):
    path = GENERATED_DIR / f"{job_id}_Audit_Report.docx"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Audit report not found.",
        )

    return FileResponse(
        path=path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename="Audit_Report.docx",
    )




