from src.extensions import db

class Citation(db.Model):
    __tablename__ = 'citations'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    raw_line = db.Column(db.Text, nullable=False)
    cleaned_title = db.Column(db.String(500))
    status = db.Column(db.String(50), nullable=False)  # Valid, Not Found, Timeout, Error
    
    def to_dict(self):
        """Convert citation to dictionary."""
        return {
            'id': self.id,
            'raw': self.raw_line,
            'cleaned_title': self.cleaned_title,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<Citation {self.id}: {self.status}>'