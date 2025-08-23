from datetime import datetime
from src.extensions import db

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(500))
    extracted_text = db.Column(db.Text)  # Store extracted PDF text
    word_count = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = db.relationship('Analysis', backref='document', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self, include_text=False):
        """Convert document to dictionary."""
        data = {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'word_count': self.word_count,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'analysis_id': self.analysis.id if self.analysis else None
        }
        
        # Only include extracted text if explicitly requested (for authorized users)
        if include_text:
            data['extracted_text'] = self.extracted_text
            
        return data
    
    def __repr__(self):
        return f'<Document {self.filename}>'