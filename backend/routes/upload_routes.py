"""
Upload Routes - Handle file uploads and processing
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func
from models import UploadHistory, JobPosting, JobSkill, TrendingSkill, db
from data_processor import process_uploaded_file, get_processor
import os
from datetime import datetime
import PyPDF2
import re
from threading import Thread, Lock

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf'}
ACTIVE_UPLOADS = set()
ACTIVE_UPLOADS_LOCK = Lock()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    """
    Extract text from PDF file
    
    Args:
        filepath: Path to PDF file
        
    Returns:
        Extracted text from PDF
    """
    try:
        text = []
        with open(filepath, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def parse_jobs_from_pdf_text(pdf_text):
    """
    Parse job postings from PDF text
    Attempts to identify job entries by looking for common patterns
    
    Args:
        pdf_text: Extracted text from PDF
        
    Returns:
        List of job data dictionaries
    """
    jobs = []
    
    # Split by common job posting separators
    job_blocks = re.split(r'\n(?=.*(?:Position|Job Title|Role|Title|JOB|POSITION))', pdf_text, flags=re.IGNORECASE)
    
    for block in job_blocks:
        if len(block.strip()) < 50:  # Skip very short blocks
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        # Try to extract job information
        job_data = {
            'job_title': '',
            'company': '',
            'job_location': '',
            'job_summary': block.strip()[:1000],  # First 1000 chars as summary
            'job_link': f"pdf_upload_{len(jobs)}",
            'data_source': 'pdf_upload'
        }
        
        # Look for title in first few lines
        for i, line in enumerate(lines[:5]):
            if any(keyword in line.lower() for keyword in ['position', 'job title', 'role', 'title']):
                # Extract text after the keyword
                match = re.search(r'(?:Position|Job Title|Role|Title|JOB|POSITION)[:\s]*(.+)', line, re.IGNORECASE)
                if match:
                    job_data['job_title'] = match.group(1).strip()
                    break
        
        # Look for company
        for line in lines[:10]:
            if any(keyword in line.lower() for keyword in ['company', 'organization', 'employer']):
                match = re.search(r'(?:Company|Organization|Employer)[:\s]*(.+)', line, re.IGNORECASE)
                if match:
                    job_data['company'] = match.group(1).strip()
                    break
        
        # Look for location
        for line in lines[:10]:
            if any(keyword in line.lower() for keyword in ['location', 'city', 'state', 'country']):
                match = re.search(r'(?:Location|City|State|Country)[:\s]*(.+)', line, re.IGNORECASE)
                if match:
                    job_data['job_location'] = match.group(1).strip()
                    break
        
        # Only add if we found at least a title
        if job_data['job_title']:
            jobs.append(job_data)
    
    # If no jobs were parsed, treat entire PDF as one job posting
    if not jobs:
        jobs = [{
            'job_title': 'Job Posting from PDF',
            'company': 'Unknown Company',
            'job_location': 'Location Not Specified',
            'job_summary': pdf_text[:2000],
            'job_link': 'pdf_upload_0',
            'data_source': 'pdf_upload'
        }]
    
    return jobs


def _source_tag_for_upload(upload_id):
    return f"upload_{upload_id}"


def _reset_upload_data(source_tag):
    """Delete previously processed rows for a specific upload source tag before retrying."""
    existing_jobs = JobPosting.query.filter_by(data_source=source_tag).all()
    if not existing_jobs:
        return

    job_ids = [job.id for job in existing_jobs]
    if job_ids:
        JobSkill.query.filter(JobSkill.job_id.in_(job_ids)).delete(synchronize_session=False)
    JobPosting.query.filter(JobPosting.id.in_(job_ids)).delete(synchronize_session=False)
    db.session.commit()


def _rebuild_trending_skills_from_jobs():
    """Rebuild trending skills from actual JobSkill records to avoid drift/duplicates."""
    aggregated = db.session.query(
        JobSkill.skill_name,
        func.count(JobSkill.id).label('count')
    ).group_by(JobSkill.skill_name).all()

    TrendingSkill.query.delete(synchronize_session=False)
    for skill_name, count in aggregated:
        db.session.add(TrendingSkill(
            skill_name=skill_name,
            mention_count=int(count or 0),
            is_technical=True,
            category='General'
        ))
    db.session.commit()


def _process_upload_in_background(flask_app, upload_id, filepath, file_type):
    """Process uploaded file in background and update UploadHistory status."""
    with ACTIVE_UPLOADS_LOCK:
        ACTIVE_UPLOADS.add(upload_id)

    with flask_app.app_context():
        upload_record = UploadHistory.query.get(upload_id)
        if not upload_record:
            with ACTIVE_UPLOADS_LOCK:
                ACTIVE_UPLOADS.discard(upload_id)
            return

        try:
            source_tag = _source_tag_for_upload(upload_id)
            _reset_upload_data(source_tag)

            if file_type == 'csv':
                stats = process_uploaded_file(filepath, source=source_tag)
                _rebuild_trending_skills_from_jobs()
                upload_record.status = 'completed'
                upload_record.records_processed = stats.get('processed', 0)
                upload_record.processed_at = datetime.now()
                db.session.commit()
                return

            if file_type == 'pdf':
                pdf_text = extract_text_from_pdf(filepath)
                jobs = parse_jobs_from_pdf_text(pdf_text)

                processor = get_processor()
                processed_count = 0
                skipped_count = 0

                for job_data in jobs:
                    result = processor.process_and_save_job(job_data, source=source_tag)
                    if result:
                        processed_count += 1
                    else:
                        skipped_count += 1

                _rebuild_trending_skills_from_jobs()

                upload_record.status = 'completed'
                upload_record.records_processed = processed_count
                upload_record.processed_at = datetime.now()
                db.session.commit()
                return

            upload_record.status = 'pending'
            upload_record.error_message = 'File type requires manual processing.'
            db.session.commit()

        except Exception as e:
            upload_record.status = 'failed'
            upload_record.error_message = str(e)
            upload_record.processed_at = datetime.now()
            db.session.commit()
        finally:
            with ACTIVE_UPLOADS_LOCK:
                ACTIVE_UPLOADS.discard(upload_id)


def _get_upload_filepath(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', '../uploads')
    if os.path.isabs(upload_folder):
        base_folder = upload_folder
    else:
        base_folder = os.path.abspath(os.path.join(current_app.root_path, upload_folder))
    os.makedirs(base_folder, exist_ok=True)
    return os.path.join(base_folder, filename)


def _start_background_processing(upload_record, filepath, file_type):
    flask_app = current_app._get_current_object()
    thread = Thread(
        target=_process_upload_in_background,
        args=(flask_app, upload_record.id, filepath, file_type),
        daemon=True
    )
    thread.start()


def _recover_stuck_uploads():
    """Requeue csv/pdf uploads that are still pending/processing and not currently active."""
    candidates = UploadHistory.query.filter(
        UploadHistory.status.in_(['pending', 'processing']),
        UploadHistory.file_type.in_(['csv', 'pdf'])
    ).all()

    requeued = 0
    for upload in candidates:
        with ACTIVE_UPLOADS_LOCK:
            if upload.id in ACTIVE_UPLOADS:
                continue

        filepath = _get_upload_filepath(upload.filename)
        if not os.path.exists(filepath):
            upload.status = 'failed'
            upload.error_message = f"Uploaded file not found: {upload.filename}"
            upload.processed_at = datetime.now()
            db.session.commit()
            continue

        upload.status = 'processing'
        upload.error_message = None
        db.session.commit()
        _start_background_processing(upload, filepath, upload.file_type)
        requeued += 1

    return requeued

@bp.route('/file', methods=['POST'])
def upload_file():
    """Upload a new data file (CSV, Excel, or PDF)"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: CSV, XLSX, PDF'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file
        filepath = _get_upload_filepath(unique_filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # Create upload history record
        upload_record = UploadHistory(
            filename=unique_filename,
            file_type=file_type,
            file_size=file_size,
            status='processing'
        )
        db.session.add(upload_record)
        db.session.commit()
        
        # Process CSV/PDF asynchronously to avoid request timeout on large uploads
        if file_type in {'csv', 'pdf'}:
            _start_background_processing(upload_record, filepath, file_type)

            return jsonify({
                'message': 'File uploaded. NLP processing started in background.',
                'upload_id': upload_record.id,
                'filename': unique_filename,
                'status': 'processing'
            }), 202

        else:
            # For Excel files, mark as pending for manual processing
            upload_record.status = 'pending'
            db.session.commit()
            return jsonify({
                'message': 'File uploaded successfully. Excel files require manual processing.',
                'upload_id': upload_record.id,
                'filename': unique_filename,
                'status': 'pending'
            }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
def get_upload_history():
    """Get upload history"""
    _recover_stuck_uploads()

    uploads = UploadHistory.query\
        .order_by(UploadHistory.uploaded_at.desc())\
        .limit(50)\
        .all()
    
    return jsonify({
        'uploads': [upload.to_dict() for upload in uploads]
    })

@bp.route('/status/<int:upload_id>', methods=['GET'])
def get_upload_status(upload_id):
    """Get status of a specific upload"""
    upload = UploadHistory.query.get_or_404(upload_id)
    return jsonify(upload.to_dict())
