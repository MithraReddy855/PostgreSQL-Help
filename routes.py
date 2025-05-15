from flask import render_template, request, jsonify, redirect, url_for, flash
from app import db
from models import QueryHistory, ErrorReport, DocumentationAccess, Schema
import logging

from services.documentation_service import search_documentation, get_doc_sections
from services.error_service import analyze_error, get_common_errors
from services.query_service import generate_query, get_query_templates
from services.schema_service import analyze_schema, get_table_info

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/documentation', methods=['GET', 'POST'])
    def documentation():
        search_results = []
        search_term = ""
        
        if request.method == 'POST':
            search_term = request.form.get('search_term', '')
            logger.debug(f"Documentation search for: {search_term}")
            
            if search_term:
                search_results = search_documentation(search_term)
                
                # Record the search
                doc_access = DocumentationAccess(
                    search_term=search_term,
                    result_count=len(search_results)
                )
                db.session.add(doc_access)
                db.session.commit()
        
        doc_sections = get_doc_sections()
        return render_template('documentation.html', 
                              search_results=search_results, 
                              search_term=search_term,
                              doc_sections=doc_sections)

    @app.route('/query_generator', methods=['GET', 'POST'])
    def query_generator():
        generated_query = ""
        query_type = "select"
        
        if request.method == 'POST':
            query_type = request.form.get('query_type', 'select')
            table_name = request.form.get('table_name', '')
            columns = request.form.get('columns', '')
            conditions = request.form.get('conditions', '')
            
            logger.debug(f"Query generation for type: {query_type}")
            
            if table_name:
                generated_query = generate_query(
                    query_type=query_type,
                    table_name=table_name,
                    columns=columns,
                    conditions=conditions,
                    join_table=request.form.get('join_table', ''),
                    join_condition=request.form.get('join_condition', ''),
                    order_by=request.form.get('order_by', ''),
                    group_by=request.form.get('group_by', ''),
                    limit=request.form.get('limit', '')
                )
                
                # Record the query
                query_history = QueryHistory(
                    query_text=generated_query,
                    query_type=query_type
                )
                db.session.add(query_history)
                db.session.commit()
        
        templates = get_query_templates()
        return render_template('query_generator.html', 
                              generated_query=generated_query,
                              query_type=query_type,
                              templates=templates)

    @app.route('/error_troubleshooter', methods=['GET', 'POST'])
    def error_troubleshooter():
        error_analysis = {}
        error_text = ""
        
        if request.method == 'POST':
            error_text = request.form.get('error_text', '')
            logger.debug(f"Error analysis requested: {error_text[:50]}...")
            
            if error_text:
                error_analysis = analyze_error(error_text)
                
                # Record the error report
                error_report = ErrorReport(
                    error_text=error_text,
                    solution=error_analysis.get('solution', '')
                )
                db.session.add(error_report)
                db.session.commit()
        
        common_errors = get_common_errors()
        return render_template('error_troubleshooter.html', 
                              error_analysis=error_analysis,
                              error_text=error_text,
                              common_errors=common_errors)

    @app.route('/schema_analyzer', methods=['GET', 'POST'])
    def schema_analyzer():
        schema_analysis = {}
        connection_string = ""
        
        if request.method == 'POST':
            connection_string = request.form.get('connection_string', '')
            table_name = request.form.get('table_name', '')
            
            logger.debug(f"Schema analysis requested for table: {table_name}")
            
            if connection_string and table_name:
                schema_analysis = analyze_schema(connection_string, table_name)
                
                if schema_analysis and not schema_analysis.get('error'):
                    # Record the schema
                    schema = Schema(
                        name=table_name,
                        structure=str(schema_analysis)
                    )
                    db.session.add(schema)
                    db.session.commit()
        
        return render_template('schema_analyzer.html', 
                              schema_analysis=schema_analysis,
                              connection_string=connection_string)

    @app.route('/api/documentation/search', methods=['POST'])
    def api_documentation_search():
        data = request.get_json()
        search_term = data.get('search_term', '')
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        results = search_documentation(search_term)
        
        # Record the search
        doc_access = DocumentationAccess(
            search_term=search_term,
            result_count=len(results)
        )
        db.session.add(doc_access)
        db.session.commit()
        
        return jsonify({'results': results})

    @app.route('/api/query/generate', methods=['POST'])
    def api_query_generate():
        data = request.get_json()
        
        query_type = data.get('query_type', 'select')
        table_name = data.get('table_name', '')
        
        if not table_name:
            return jsonify({'error': 'Table name is required'}), 400
        
        generated_query = generate_query(
            query_type=query_type,
            table_name=table_name,
            columns=data.get('columns', ''),
            conditions=data.get('conditions', ''),
            join_table=data.get('join_table', ''),
            join_condition=data.get('join_condition', ''),
            order_by=data.get('order_by', ''),
            group_by=data.get('group_by', ''),
            limit=data.get('limit', '')
        )
        
        # Record the query
        query_history = QueryHistory(
            query_text=generated_query,
            query_type=query_type
        )
        db.session.add(query_history)
        db.session.commit()
        
        return jsonify({'query': generated_query})

    @app.route('/api/error/analyze', methods=['POST'])
    def api_error_analyze():
        data = request.get_json()
        error_text = data.get('error_text', '')
        
        if not error_text:
            return jsonify({'error': 'Error text is required'}), 400
        
        analysis = analyze_error(error_text)
        
        # Record the error report
        error_report = ErrorReport(
            error_text=error_text,
            solution=analysis.get('solution', '')
        )
        db.session.add(error_report)
        db.session.commit()
        
        return jsonify(analysis)

    @app.route('/api/schema/analyze', methods=['POST'])
    def api_schema_analyze():
        data = request.get_json()
        connection_string = data.get('connection_string', '')
        table_name = data.get('table_name', '')
        
        if not connection_string or not table_name:
            return jsonify({'error': 'Connection string and table name are required'}), 400
        
        analysis = analyze_schema(connection_string, table_name)
        
        if not analysis.get('error'):
            # Record the schema
            schema = Schema(
                name=table_name,
                structure=str(analysis)
            )
            db.session.add(schema)
            db.session.commit()
        
        return jsonify(analysis)

    @app.route('/api/table/info', methods=['POST'])
    def api_table_info():
        data = request.get_json()
        connection_string = data.get('connection_string', '')
        
        if not connection_string:
            return jsonify({'error': 'Connection string is required'}), 400
        
        table_info = get_table_info(connection_string)
        return jsonify({'tables': table_info})

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                              error_code=404, 
                              error_message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', 
                              error_code=500, 
                              error_message="Internal server error"), 500

    logger.info("Routes registered successfully")
