"""
Upload Routes - Handle file uploads and processing
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import UploadHistory, db
from data_processor import process_uploaded_file
import os
from datetime import datetime

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        else:
            # For non-CSV files, mark as pending for manual processing
            return jsonify({
                'message': 'File uploaded successfully. Non-CSV files require manual processing.',
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
