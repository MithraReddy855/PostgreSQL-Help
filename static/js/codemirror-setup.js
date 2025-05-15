/**
 * Initialize CodeMirror for SQL syntax highlighting
 */
function initCodeMirror(element) {
  // Check if CodeMirror is available
  if (typeof CodeMirror === 'undefined') {
    console.warn('CodeMirror not loaded');
    return;
  }
  
  // Check if element is valid
  if (!element) {
    console.warn('Invalid element for CodeMirror initialization');
    return;
  }
  
  // Get the content
  const content = element.textContent;
  
  // Create a new textarea to replace the pre
  const textarea = document.createElement('textarea');
  textarea.value = content;
  
  // Replace the pre with the textarea
  element.parentNode.replaceChild(textarea, element);
  
  // Initialize CodeMirror
  const editor = CodeMirror.fromTextArea(textarea, {
    mode: 'text/x-sql',
    theme: 'darcula',
    lineNumbers: true,
    readOnly: true,
    viewportMargin: Infinity,
    indentWithTabs: true,
    smartIndent: true,
    lineWrapping: true,
    matchBrackets: true,
    autofocus: false
  });
  
  // Set proper height
  editor.setSize(null, 'auto');
  
  return editor;
}

/**
 * Initialize CodeMirror for SQL input
 */
function initSqlEditor(elementId) {
  // Check if CodeMirror is available
  if (typeof CodeMirror === 'undefined') {
    console.warn('CodeMirror not loaded');
    return;
  }
  
  const element = document.getElementById(elementId);
  
  // Check if element is valid
  if (!element) {
    console.warn('Invalid element for CodeMirror initialization');
    return;
  }
  
  // Initialize CodeMirror
  const editor = CodeMirror.fromTextArea(element, {
    mode: 'text/x-sql',
    theme: 'darcula',
    lineNumbers: true,
    indentWithTabs: true,
    smartIndent: true,
    lineWrapping: true,
    matchBrackets: true,
    autofocus: true,
    extraKeys: {"Ctrl-Space": "autocomplete"}
  });
  
  // Set proper height
  editor.setSize(null, 150);
  
  // Update the textarea on change
  editor.on('change', function() {
    editor.save();
  });
  
  return editor;
}

// Initialize SQL editors when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize all pre.sql-code elements
  document.querySelectorAll('pre.sql-code').forEach(function(element) {
    initCodeMirror(element);
  });
  
  // Initialize SQL input editors
  const sqlInputs = ['conditions', 'columns', 'error_text'];
  sqlInputs.forEach(function(id) {
    const element = document.getElementById(id);
    if (element) {
      initSqlEditor(id);
    }
  });
});
