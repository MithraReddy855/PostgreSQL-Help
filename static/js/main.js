/**
 * PostgreSQL Agent - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips and popovers
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
  
  // Setup form submission with AJAX where appropriate
  setupAsyncForms();
  
  // Setup tab persistence
  setupTabPersistence();
  
  // Responsive sidebar toggle
  setupSidebar();
  
  // Setup copy buttons for code blocks
  setupCopyButtons();
});

/**
 * Setup asynchronous form submissions
 */
function setupAsyncForms() {
  const asyncForms = document.querySelectorAll('form[data-async="true"]');
  
  asyncForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const submitButton = form.querySelector('button[type="submit"]');
      const resultContainer = document.getElementById(form.dataset.resultContainer);
      
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      }
      
      // Convert FormData to JSON
      const jsonData = {};
      formData.forEach((value, key) => {
        jsonData[key] = value;
      });
      
      fetch(form.action, {
        method: form.method || 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(jsonData)
      })
      .then(response => response.json())
      .then(data => {
        if (resultContainer) {
          if (data.error) {
            resultContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
          } else {
            // Handle specific result formats based on form ID
            if (form.id === 'queryForm') {
              displayGeneratedQuery(data, resultContainer);
            } else if (form.id === 'errorForm') {
              displayErrorAnalysis(data, resultContainer);
            } else if (form.id === 'schemaForm') {
              displaySchemaAnalysis(data, resultContainer);
            } else if (form.id === 'docSearchForm') {
              displayDocSearchResults(data, resultContainer);
            } else {
              // Generic JSON display
              resultContainer.innerHTML = `<pre class="bg-dark text-light p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
            }
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        if (resultContainer) {
          resultContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error.message}</div>`;
        }
      })
      .finally(() => {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
        }
      });
    });
    
    // Store original button text
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.dataset.originalText = submitButton.innerHTML;
    }
  });
}

/**
 * Display generated SQL query
 */
function displayGeneratedQuery(data, container) {
  if (!data.query) {
    container.innerHTML = '<div class="alert alert-warning">No query was generated.</div>';
    return;
  }
  
  const html = `
    <div class="card border-info">
      <div class="card-header bg-info bg-opacity-25 d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Generated Query</h5>
        <button class="btn btn-sm btn-outline-secondary copy-btn" data-content="${encodeURIComponent(data.query)}">
          <i class="fas fa-copy"></i> Copy
        </button>
      </div>
      <div class="card-body">
        <pre class="query-result mb-0">${data.query}</pre>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Initialize code highlighting if CodeMirror is available
  if (typeof initCodeMirror === 'function') {
    initCodeMirror(container.querySelector('pre.query-result'));
  }
  
  // Setup copy button
  setupCopyButtons();
}

/**
 * Display error analysis results
 */
function displayErrorAnalysis(data, container) {
  if (data.error) {
    container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
    return;
  }
  
  const html = `
    <div class="card border-info mb-4">
      <div class="card-header bg-info bg-opacity-25">
        <h5 class="mb-0">Error Analysis: ${data.error_type || 'Unknown Error'}</h5>
      </div>
      <div class="card-body">
        <h6 class="card-subtitle mb-3 text-muted">Explanation:</h6>
        <p class="card-text">${data.explanation || 'No explanation available.'}</p>
        
        <h6 class="card-subtitle mb-3 text-muted mt-4">Recommended Solution:</h6>
        <div class="solution-steps">
          ${formatSolutionSteps(data.solution)}
        </div>
        
        ${data.error_code ? `<div class="mt-3 text-muted"><small>Error Code: ${data.error_code}</small></div>` : ''}
      </div>
    </div>
  `;
  
  container.innerHTML = html;
}

/**
 * Format solution steps from plain text to HTML
 */
function formatSolutionSteps(solutionText) {
  if (!solutionText) return '<p>No solution available.</p>';
  
  // Check if the solution text contains numbered steps
  if (/^\d+\.\s/.test(solutionText)) {
    // Split by newline and convert to ordered list
    const steps = solutionText.split('\n').filter(step => step.trim() !== '');
    return `<ol class="ps-3">${steps.map(step => `<li>${step.replace(/^\d+\.\s/, '')}</li>`).join('')}</ol>`;
  } else {
    // Return as paragraphs
    return solutionText.split('\n').filter(p => p.trim() !== '').map(p => `<p>${p}</p>`).join('');
  }
}

/**
 * Display schema analysis results
 */
function displaySchemaAnalysis(data, container) {
  if (data.error) {
    container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
    return;
  }
  
  // Generate table structure display
  let columnsHtml = '';
  if (data.columns && data.columns.length > 0) {
    columnsHtml = `
      <table class="table table-sm table-striped">
        <thead>
          <tr>
            <th>Column</th>
            <th>Type</th>
            <th>Nullable</th>
            <th>Default</th>
            <th>PK</th>
          </tr>
        </thead>
        <tbody>
          ${data.columns.map(col => `
            <tr>
              <td>${col.name}</td>
              <td><code>${col.type}</code></td>
              <td>${col.nullable ? 'Yes' : 'No'}</td>
              <td>${col.default !== 'None' ? `<code>${col.default}</code>` : '-'}</td>
              <td>${col.is_primary || (data.primary_key && data.primary_key.includes(col.name)) ? '✓' : ''}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } else {
    columnsHtml = '<div class="alert alert-warning">No column information available.</div>';
  }
  
  // Generate foreign keys display
  let fkHtml = '';
  if (data.foreign_keys && data.foreign_keys.length > 0) {
    fkHtml = `
      <h6 class="mt-4">Foreign Keys:</h6>
      <ul class="list-group">
        ${data.foreign_keys.map(fk => `
          <li class="list-group-item">
            <strong>${fk.name}</strong>: (${fk.columns.join(', ')}) → 
            ${fk.referred_table} (${fk.referred_columns.join(', ')})
          </li>
        `).join('')}
      </ul>
    `;
  }
  
  // Generate indexes display
  let indexesHtml = '';
  if (data.indexes && data.indexes.length > 0) {
    indexesHtml = `
      <h6 class="mt-4">Indexes:</h6>
      <ul class="list-group">
        ${data.indexes.map(idx => `
          <li class="list-group-item">
            <strong>${idx.name}</strong>: ${idx.unique ? 'UNIQUE ' : ''}(${idx.columns.join(', ')})
          </li>
        `).join('')}
      </ul>
    `;
  }
  
  // Generate CREATE TABLE SQL
  let sqlHtml = '';
  if (data.create_table_sql) {
    sqlHtml = `
      <div class="mt-4">
        <h6>CREATE TABLE SQL:</h6>
        <div class="position-relative">
          <button class="btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2 copy-btn" 
                  data-content="${encodeURIComponent(data.create_table_sql)}">
            <i class="fas fa-copy"></i> Copy
          </button>
          <pre class="bg-dark text-light p-3 rounded">${data.create_table_sql}</pre>
        </div>
      </div>
    `;
  }
  
  // Sample data structure
  let sampleDataHtml = '';
  if (data.sample_data_structure) {
    sampleDataHtml = `
      <div class="mt-4">
        <h6>Sample Data Structure:</h6>
        <pre class="bg-dark text-light p-3 rounded">${data.sample_data_structure}</pre>
      </div>
    `;
  }
  
  const html = `
    <div class="card border-info mb-4">
      <div class="card-header bg-info bg-opacity-25">
        <h5 class="mb-0">Schema Analysis: ${data.table_name}</h5>
      </div>
      <div class="card-body">
        <h6>Columns:</h6>
        ${columnsHtml}
        ${fkHtml}
        ${indexesHtml}
        ${sqlHtml}
        ${sampleDataHtml}
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Setup copy buttons
  setupCopyButtons();
}

/**
 * Display documentation search results
 */
function displayDocSearchResults(data, container) {
  if (data.error) {
    container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
    return;
  }
  
  if (!data.results || data.results.length === 0) {
    container.innerHTML = '<div class="alert alert-info">No documentation results found.</div>';
    return;
  }
  
  const resultsHtml = data.results.map(result => `
    <div class="card mb-3">
      <div class="card-body">
        <h5 class="card-title">
          <a href="${result.url}" target="_blank" rel="noopener noreferrer">${result.title}</a>
        </h5>
        <p class="card-text text-muted">
          <small>${result.url}</small>
        </p>
        <p class="card-text">${result.snippet || 'No description available.'}</p>
      </div>
    </div>
  `).join('');
  
  container.innerHTML = `
    <h5 class="mb-3">Documentation Search Results:</h5>
    ${resultsHtml}
  `;
}

/**
 * Setup tab persistence using localStorage
 */
function setupTabPersistence() {
  // Save active tab to localStorage when clicked
  const tabs = document.querySelectorAll('a[data-bs-toggle="tab"]');
  
  tabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(e) {
      const targetId = e.target.getAttribute('href');
      localStorage.setItem('activeTab', targetId);
    });
  });
  
  // Restore active tab from localStorage
  const activeTab = localStorage.getItem('activeTab');
  if (activeTab) {
    const tab = document.querySelector(`a[data-bs-toggle="tab"][href="${activeTab}"]`);
    if (tab) {
      const bsTab = new bootstrap.Tab(tab);
      bsTab.show();
    }
  }
}

/**
 * Setup sidebar toggle functionality
 */
function setupSidebar() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function(e) {
      e.preventDefault();
      document.body.classList.toggle('sidebar-collapsed');
      
      // Store preference
      const isCollapsed = document.body.classList.contains('sidebar-collapsed');
      localStorage.setItem('sidebarCollapsed', isCollapsed ? 'true' : 'false');
    });
    
    // Restore sidebar state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
      document.body.classList.add('sidebar-collapsed');
    }
  }
}

/**
 * Setup copy buttons for code blocks
 */
function setupCopyButtons() {
  const copyButtons = document.querySelectorAll('.copy-btn');
  
  copyButtons.forEach(button => {
    button.addEventListener('click', function() {
      const content = decodeURIComponent(this.dataset.content);
      
      // Copy to clipboard
      navigator.clipboard.writeText(content)
        .then(() => {
          // Visual feedback
          const originalText = this.innerHTML;
          this.innerHTML = '<i class="fas fa-check"></i> Copied!';
          
          setTimeout(() => {
            this.innerHTML = originalText;
          }, 2000);
        })
        .catch(err => {
          console.error('Failed to copy: ', err);
          this.innerHTML = '<i class="fas fa-times"></i> Failed';
          
          setTimeout(() => {
            this.innerHTML = originalText;
          }, 2000);
        });
    });
  });
}

/**
 * Dynamic form fields based on query type
 */
function updateQueryForm(queryType) {
  const joinFields = document.getElementById('joinFields');
  const columnLabel = document.getElementById('columnLabel');
  const columnHelp = document.getElementById('columnHelp');
  const conditionFields = document.getElementById('conditionFields');
  const orderByFields = document.getElementById('orderByFields');
  const limitFields = document.getElementById('limitFields');
  
  // Reset all fields
  if (joinFields) joinFields.style.display = 'none';
  if (orderByFields) orderByFields.style.display = 'none';
  if (limitFields) limitFields.style.display = 'none';
  
  // Configure fields based on query type
  switch (queryType) {
    case 'select':
      if (columnLabel) columnLabel.textContent = 'Columns:';
      if (columnHelp) columnHelp.textContent = 'Comma-separated list of columns to select (leave empty for *)';
      if (conditionFields) conditionFields.style.display = 'block';
      if (joinFields) joinFields.style.display = 'block';
      if (orderByFields) orderByFields.style.display = 'block';
      if (limitFields) limitFields.style.display = 'block';
      break;
      
    case 'insert':
      if (columnLabel) columnLabel.textContent = 'Columns:';
      if (columnHelp) columnHelp.textContent = 'Comma-separated list of columns to insert';
      if (conditionFields) conditionFields.style.display = 'none';
      if (joinFields) joinFields.style.display = 'none';
      if (orderByFields) orderByFields.style.display = 'none';
      if (limitFields) limitFields.style.display = 'none';
      break;
      
    case 'update':
      if (columnLabel) columnLabel.textContent = 'SET Clause:';
      if (columnHelp) columnHelp.textContent = 'SET clause (e.g., "column1 = value1, column2 = value2")';
      if (conditionFields) conditionFields.style.display = 'block';
      if (joinFields) joinFields.style.display = 'none';
      if (orderByFields) orderByFields.style.display = 'none';
      if (limitFields) limitFields.style.display = 'none';
      break;
      
    case 'delete':
      if (columnLabel) columnLabel.textContent = 'Columns:';
      if (columnHelp) columnHelp.textContent = 'Columns are not used for DELETE queries';
      if (conditionFields) conditionFields.style.display = 'block';
      if (joinFields) joinFields.style.display = 'none';
      if (orderByFields) orderByFields.style.display = 'none';
      if (limitFields) limitFields.style.display = 'none';
      break;
      
    case 'create_table':
      if (columnLabel) columnLabel.textContent = 'Column Definitions:';
      if (columnHelp) columnHelp.textContent = 'Column definitions (e.g., "name VARCHAR(100), age INTEGER, created_at TIMESTAMP")';
      if (conditionFields) conditionFields.style.display = 'none';
      if (joinFields) joinFields.style.display = 'none';
      if (orderByFields) orderByFields.style.display = 'none';
      if (limitFields) limitFields.style.display = 'none';
      break;
  }
}

/**
 * Load common error examples
 */
function loadErrorExample(errorType) {
  const errorExamples = {
    'connection_refused': 'could not connect to server: Connection refused\nIs the server running on host "localhost" (127.0.0.1) and accepting\nTCP/IP connections on port 5432?',
    'authentication_failed': 'FATAL: password authentication failed for user "postgres"\nFATAL: password authentication failed for user "postgres"',
    'permission_denied': 'ERROR: permission denied for table customers\nSQL state: 42501',
    'relation_not_found': 'ERROR: relation "users" does not exist\nLINE 1: SELECT * FROM users\n                      ^',
    'syntax_error': 'ERROR: syntax error at or near "SLECT"\nLINE 1: SLECT * FROM customers\n        ^',
    'duplicate_key': 'ERROR: duplicate key value violates unique constraint "users_email_key"\nDETAIL: Key (email)=(john@example.com) already exists.',
    'foreign_key_violation': 'ERROR: insert or update on table "orders" violates foreign key constraint "orders_customer_id_fkey"\nDETAIL: Key (customer_id)=(999) is not present in table "customers".',
    'out_of_memory': 'ERROR: out of memory\nDETAIL: Failed on request of size 2147483647.'
  };
  
  const errorTextArea = document.getElementById('error_text');
  if (errorTextArea && errorExamples[errorType]) {
    errorTextArea.value = errorExamples[errorType];
  }
}
