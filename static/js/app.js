// Finanzas SRI Ecuador - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar aplicación
    initApp();
});

function initApp() {
    // Configurar sidebar toggle
    setupSidebarToggle();
    
    // Configurar tooltips
    setupTooltips();
    
    // Configurar file uploads
    setupFileUploads();
    
    // Configurar auto-refresh
    setupAutoRefresh();
    
    // Configurar notificaciones
    setupNotifications();
}

// Sidebar Toggle
function setupSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Cerrar sidebar al hacer click fuera en móvil
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }
}

// Tooltips Bootstrap
function setupTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// File Upload Handling
function setupFileUploads() {
    const fileInputs = document.querySelectorAll('.file-upload-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            handleFileSelect(e, this);
        });
        
        // Drag and drop
        const wrapper = input.closest('.file-upload-wrapper');
        if (wrapper) {
            wrapper.addEventListener('dragover', function(e) {
                e.preventDefault();
                wrapper.classList.add('dragover');
            });
            
            wrapper.addEventListener('dragleave', function(e) {
                e.preventDefault();
                wrapper.classList.remove('dragover');
            });
            
            wrapper.addEventListener('drop', function(e) {
                e.preventDefault();
                wrapper.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    handleFileSelect({target: input}, input);
                }
            });
        }
    });
}

function handleFileSelect(event, input) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validar tipo de archivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('error', 'Tipo de archivo no permitido. Use imágenes (JPG, PNG) o PDF.');
        input.value = '';
        return;
    }
    
    // Validar tamaño (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('error', 'El archivo es muy grande. Máximo 16MB permitido.');
        input.value = '';
        return;
    }
    
    // Mostrar preview si es imagen
    if (file.type.startsWith('image/')) {
        showImagePreview(file, input);
    }
    
    // Mostrar nombre del archivo
    const fileName = file.name;
    const fileInfo = input.parentElement.querySelector('.file-info');
    if (fileInfo) {
        fileInfo.textContent = `Archivo seleccionado: ${fileName}`;
        fileInfo.style.display = 'block';
    }
}

function showImagePreview(file, input) {
    const reader = new FileReader();
    reader.onload = function(e) {
        let preview = input.parentElement.querySelector('.image-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview mt-3';
            input.parentElement.appendChild(preview);
        }
        
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <button type="button" class="btn btn-sm btn-danger ms-2" onclick="removePreview(this)">
                <i class="fas fa-times"></i>
            </button>
        `;
    };
    reader.readAsDataURL(file);
}

function removePreview(button) {
    const preview = button.closest('.image-preview');
    const input = preview.parentElement.querySelector('input[type="file"]');
    
    if (preview) preview.remove();
    if (input) input.value = '';
    
    const fileInfo = preview.parentElement.querySelector('.file-info');
    if (fileInfo) fileInfo.style.display = 'none';
}

// Upload de facturas
function uploadReceipt(formData, progressCallback) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // Progreso de subida
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                if (progressCallback) {
                    progressCallback(percentComplete);
                }
            }
        });
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        reject('Error parsing response');
                    }
                } else {
                    reject(`Error ${xhr.status}: ${xhr.statusText}`);
                }
            }
        };
        
        xhr.open('POST', '/upload', true);
        xhr.send(formData);
    });
}

// Auto-refresh dashboard
function setupAutoRefresh() {
    if (window.location.pathname === '/') {
        setInterval(refreshDashboardStats, 60000); // Cada minuto
    }
}

function refreshDashboardStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardCards(data);
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

function updateDashboardCards(data) {
    // Actualizar tarjetas de estadísticas
    const totalUsed = data.total_used || 0;
    const totalAvailable = data.total_available || 14753.40;
    const remaining = totalAvailable - totalUsed;
    const percentage = totalAvailable > 0 ? (totalUsed / totalAvailable * 100) : 0;
    
    // Actualizar valores en las tarjetas
    const elements = {
        'deducciones-disponibles': `$${remaining.toLocaleString('es-EC', {minimumFractionDigits: 2})}`,
        'total-utilizado': `$${totalUsed.toLocaleString('es-EC', {minimumFractionDigits: 2})}`,
        'porcentaje-utilizado': `${percentage.toFixed(1)}%`
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
    
    // Actualizar barra de progreso
    const progressBar = document.querySelector('.progress-bar.bg-info');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
}

// Notificaciones Toast
function setupNotifications() {
    // Configurar auto-dismiss para alertas
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

function showNotification(type, message, duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = 9999;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            <strong class="me-auto">${getTypeLabel(type)}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration
    });
    
    bsToast.show();
    
    // Remover del DOM después de ocultar
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getTypeLabel(type) {
    const labels = {
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'info': 'Información'
    };
    return labels[type] || 'Notificación';
}

// Utilidades para formateo
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

function formatPercentage(value) {
    return new Intl.NumberFormat('es-EC', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// Validación de formularios
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Loading states
function showLoading(element, text = 'Cargando...') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.innerHTML = `
        <span class="spinner-custom me-2"></span>
        ${text}
    `;
    element.disabled = true;
}

function hideLoading(element) {
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
        element.removeAttribute('data-original-content');
    }
    element.disabled = false;
}

// Exportar funciones globales
window.FinanzasSRI = {
    showNotification,
    uploadReceipt,
    formatCurrency,
    formatDate,
    formatPercentage,
    validateForm,
    showLoading,
    hideLoading,
    refreshDashboardStats
}; 