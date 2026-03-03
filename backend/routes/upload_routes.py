"""
Upload Routes - Handle file uploads and processing
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import UploadHistory, db
from data_processor import process_uploaded_file, get_processor
import os
from datetime import datetime
import PyPDF2
import re

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf'}

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
        upload_folder = '../uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, unique_filename)
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
        
        # Process file through NLP and ML pipeline
        if file_type == 'csv':
            try:
                stats = process_uploaded_file(filepath, source='upload')
                
                # Update upload record
                upload_record.status = 'completed'
                upload_record.records_processed = stats.get('processed', 0)
                upload_record.processed_at = datetime.now()
                db.session.commit()
                
                return jsonify({
                    'message': 'File uploaded and processed successfully',
                    'upload_id': upload_record.id,
                    'filename': unique_filename,
                    'status': 'completed',
                    'stats': stats
                }), 201
                
            except Exception as e:
                upload_record.status = 'failed'
                upload_record.error_message = str(e)
                db.session.commit()
                
                return jsonify({
                    'error': f'Processing failed: {str(e)}',
                    'upload_id': upload_record.id
                }), 500
        
        elif file_type == 'pdf':
            # Process PDF through NLP pipeline
            try:
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(filepath)
                
                # Parse jobs from PDF text
                jobs = parse_jobs_from_pdf_text(pdf_text)
                
                # Process each job through NLP pipeline
                processor = get_processor()
                processed_count = 0
                skipped_count = 0
                
                for job_data in jobs:
                    result = processor.process_and_save_job(job_data, source='pdf_upload')
                    if result:
                        processed_count += 1
                    else:
                        skipped_count += 1
                
                # Update upload record
                upload_record.status = 'completed'
                upload_record.records_processed = processed_count
                upload_record.processed_at = datetime.now()
                db.session.commit()
                
                stats = {
                    'total': len(jobs),
                    'processed': processed_count,
                    'skipped': skipped_count,
                    'status': 'success'
                }
                
                return jsonify({
                    'message': f'PDF uploaded and processed. Extracted {len(jobs)} job postings through NLP.',
                    'upload_id': upload_record.id,
                    'filename': unique_filename,
                    'status': 'completed',
                    'stats': stats
                }), 201
                
            except Exception as e:
                upload_record.status = 'failed'
                upload_record.error_message = str(e)
                db.session.commit()
                
                return jsonify({
                    'error': f'PDF processing failed: {str(e)}',
                    'upload_id': upload_record.id
                }), 500
        
        else:
            # For Excel files, mark as pending for manual processing
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
