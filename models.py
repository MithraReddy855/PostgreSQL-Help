from datetime import datetime
from app import db

class QueryHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    query_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory {self.id} - {self.query_type}>"

class ErrorReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_text = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ErrorReport {self.id}>"

class DocumentationAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(255), nullable=False)
    result_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentationAccess {self.id} - {self.search_term}>"

class Schema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    structure = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Schema {self.id} - {self.name}>"
