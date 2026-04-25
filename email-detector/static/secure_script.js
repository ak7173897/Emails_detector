/**
 * =============================================================================
 * AI Email Security Detector - Secure Frontend JavaScript
 * =============================================================================
 * SECURITY FEATURES:
 * - XSS prevention with proper DOM handling
 * - Input validation and sanitization
 * - CSRF token handling
 * - Secure error handling
 * =============================================================================
 */

'use strict';

/* =============================================================================
   PARTICLE CANVAS ANIMATION
============================================================================= */
const ParticleSystem = {
    canvas: null,
    ctx: null,
    particles: [],
    animationId: null,

    init() {
        this.canvas = document.getElementById('particleCanvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.resize();
        this.createParticles();
        this.animate();

        window.addEventListener('resize', () => this.resize());
    },

    resize() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    },

    createParticles() {
        this.particles = [];
        const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 15000);

        for (let i = 0; i < Math.min(particleCount, 100); i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    },

    animate() {
        if (!this.ctx || !this.canvas) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        const particleColor = isDark ? '0, 212, 255' : '79, 70, 229';
        const lineColor = isDark ? '0, 212, 255' : '79, 70, 229';

        // Update and draw particles
        this.particles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;

            // Wrap around edges
            if (p.x < 0) p.x = this.canvas.width;
            if (p.x > this.canvas.width) p.x = 0;
            if (p.y < 0) p.y = this.canvas.height;
            if (p.y > this.canvas.height) p.y = 0;

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(${particleColor}, ${p.opacity})`;
            this.ctx.fill();

            // Draw connections
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 120) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `rgba(${lineColor}, ${0.15 * (1 - dist / 120)})`;
                    this.ctx.stroke();
                }
            }
        });

        this.animationId = requestAnimationFrame(() => this.animate());
    }
};

// Security utilities
const SecurityUtils = {
    /**
     * Safely set text content to prevent XSS
     */
    setTextContent: (element, text) => {
        if (element && text !== undefined && text !== null) {
            element.textContent = String(text);
        }
    },

    /**
     * Safely create HTML elements
     */
    createElement: (tag, className, textContent) => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (textContent) element.textContent = textContent;
        return element;
    },

    /**
     * Validate email content on client side
     */
    validateEmailContent: (content) => {
        if (!content || typeof content !== 'string') {
            return { valid: false, error: 'Email content is required' };
        }

        const trimmed = content.trim();
        if (trimmed.length < 10) {
            return { valid: false, error: 'Email content too short (minimum 10 characters)' };
        }

        if (trimmed.length > 50000) {
            return { valid: false, error: 'Email content too long (maximum 50,000 characters)' };
        }

        return { valid: true, content: trimmed };
    },

    /**
     * Get CSRF token from meta tag
     */
    getCSRFToken: () => {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : null;
    }
};

// Sample emails (secure, no XSS vectors)
const SAMPLE_EMAILS = {
    safe: `Hi John, I hope this email finds you well. I wanted to follow up on our meeting last week regarding the Q3 budget planning. Could we schedule a call this week to discuss the revised numbers? Let me know what works best for you.

Best regards,
Sarah Johnson
Project Manager`,

    spam: `CONGRATULATIONS!!! You have been SELECTED!!!

You are our LUCKY WINNER of $1,000,000!!!

ACT NOW!!! Click here IMMEDIATELY to claim your prize before it EXPIRES!!!

This is a LIMITED TIME OFFER!!! Only 3 SPOTS LEFT!!!

Make $5000 per week working from home! No experience needed!
FREE iPhone! FREE iPad! FREE EVERYTHING!!!

Call 1 800 SCAM NOW or click: http://totally-legit-prize.suspicious.net

DON'T MISS OUT!!! This offer EXPIRES in 10 MINUTES!!!`,

    phishing: `Dear Valued Customer,

We have detected unusual activity on your account from an unrecognized device in Eastern Europe. As a security measure, your account access has been temporarily restricted.

To restore full access to your account and prevent unauthorized use, please verify your identity immediately by clicking the secure link below:

https://secure-account-verify.phishing-site.net/login

You must complete this verification within 24 hours or your account will be permanently suspended. Please have your username, password, and billing information ready.

Our security team is standing by 24/7.

Best regards,
Account Security Team
support@legitimate-bank-totally.com`
};

// Application state
let currentAnalysis = null;
let isAnalyzing = false;

/* =============================================================================
   INITIALIZATION
============================================================================= */
document.addEventListener('DOMContentLoaded', () => {
    ParticleSystem.init();
    initializeTheme();
    setupEventListeners();
    updateWordCount();
    renderHistory();
    updateHistoryBadge();
});

/* =============================================================================
   THEME MANAGEMENT
============================================================================= */
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

/* =============================================================================
   EVENT LISTENERS
============================================================================= */
function setupEventListeners() {
    // Text input monitoring
    const emailInput = document.getElementById('emailInput');
    if (emailInput) {
        emailInput.addEventListener('input', updateWordCount);
        emailInput.addEventListener('paste', () => {
            setTimeout(updateWordCount, 100); // Delay for paste processing
        });
    }

    // File upload
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }

    // Navigation relies on inline onclick handlers in template:
    // showSection('detector'|'history'|'dashboard'|'bulk'|'about')
    // Avoid adding a second parser-based click handler here, because
    // labels like "How It Works" become "how" and hide all sections.

    // Sample email buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = e.target.textContent.toLowerCase();
            if (action === 'safe' || action === 'spam' || action === 'phish') {
                loadSample(action === 'phish' ? 'phishing' : action);
            } else if (action === 'clear' && e.target.id !== 'clearHistoryBtn') {
                clearAll();
            }
        });
    });

    // History Action Buttons
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearHistory);
    }
}

/* =============================================================================
   SECTION MANAGEMENT
============================================================================= */
function showSection(name) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.hidden = true;
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(`section-${name}`);
    if (targetSection) {
        targetSection.hidden = false;
        targetSection.classList.add('active');
    }

    // Handle HERO visibility
    const hero = document.getElementById('heroSection');
    if (hero) {
        hero.hidden = name !== 'detector';
    }

    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.removeAttribute('aria-current');
    });

    const sectionButtonMap = {
        detector: 'Detector',
        history: 'History',
        dashboard: 'Dashboard',
        bulk: 'Bulk Analyze',
        about: 'How It Works'
    };
    const activeButtonLabel = sectionButtonMap[name];
    const activeButton = [...document.querySelectorAll('.nav-btn')]
        .find(btn => btn.textContent.trim().includes(activeButtonLabel));

    if (activeButton) {
        activeButton.classList.add('active');
        activeButton.setAttribute('aria-current', 'page');
    }

    // Section-specific logic
    if (name === 'history') {
        renderHistory();
        updateHistoryStats();
    } else if (name === 'dashboard') {
        requestAnimationFrame(() => updateDashboard());
    }
}
// function showSection(name) {
//     // Hide all sections
//     document.querySelectorAll('.content-section').forEach(section => {
//         section.hidden = true;
//         section.classList.remove('active');
//     });

//     // Show target section
//     const targetSection = document.getElementById(`section-${name}`);
//     if (targetSection) {
//         targetSection.hidden = false;
//         targetSection.classList.add('active');
//     }

//     // Update navigation
//     document.querySelectorAll('.nav-btn').forEach(btn => {
//         btn.classList.remove('active');
//     });

//     const activeButton = [...document.querySelectorAll('.nav-btn')]
//         .find(btn => btn.textContent.toLowerCase().includes(name));
//     if (activeButton) {
//         activeButton.classList.add('active');
//     }

//     // Special handling for history section
//     if (name === 'history') {
//         renderHistory();
//     }
// }

/* =============================================================================
   INPUT HANDLING
============================================================================= */
function updateWordCount() {
    const emailInput = document.getElementById('emailInput');
    const wordCountElement = document.getElementById('wordCount');

    if (!emailInput || !wordCountElement) return;

    const text = emailInput.value.trim();
    const wordCount = text ? text.split(/\s+/).length : 0;

    SecurityUtils.setTextContent(wordCountElement, `${wordCount} words`);

    // Update analyze button state
    const analyzeBtn = document.getElementById('checkBtn');
    if (analyzeBtn) {
        const isValidLength = text.length >= 10;
        analyzeBtn.disabled = !isValidLength || isAnalyzing;

        if (!isValidLength && text.length > 0) {
            analyzeBtn.title = 'Minimum 10 characters required';
        } else {
            analyzeBtn.title = 'Click to analyze email';
        }
    }
}

function loadSample(type) {
    const emailInput = document.getElementById('emailInput');
    if (!emailInput || !SAMPLE_EMAILS[type]) return;

    emailInput.value = SAMPLE_EMAILS[type];
    updateWordCount();
}

function clearAll() {
    const emailInput = document.getElementById('emailInput');
    if (emailInput) {
        emailInput.value = '';
        updateWordCount();
    }

    // Reset results to default state
    showDefaultResults();
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['text/plain', 'message/rfc822'];
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.eml') && !file.name.endsWith('.txt')) {
        showError('Invalid file type. Please upload .txt or .eml files only.');
        return;
    }

    // Validate file size (1MB limit)
    if (file.size > 1024 * 1024) {
        showError('File too large. Maximum size is 1MB.');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': SecurityUtils.getCSRFToken()
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Upload failed');
        }

        const data = await response.json();

        // Safely set the content
        const emailInput = document.getElementById('emailInput');
        if (emailInput && data.content) {
            emailInput.value = data.content;
            updateWordCount();
        }

    } catch (error) {
        console.error('File upload error:', error);
        showError(`File upload failed: ${error.message}`);
    }

    // Clear file input
    event.target.value = '';
}

/* =============================================================================
   EMAIL ANALYSIS
============================================================================= */
async function analyzeEmail() {
    const emailInput = document.getElementById('emailInput');
    if (!emailInput) return;

    // Validate input
    const validation = SecurityUtils.validateEmailContent(emailInput.value);
    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    // Prevent multiple simultaneous requests
    if (isAnalyzing) return;

    try {
        isAnalyzing = true;
        showLoadingState();

        const requestBody = {
            text: validation.content
        };

        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': SecurityUtils.getCSRFToken()
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const data = await response.json();

        // Validate response data
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid response format');
        }

        // Store current analysis
        currentAnalysis = data;

        // Show results
        showResultState(data);

        // Save to history
        addToHistory(validation.content, data);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Analysis failed: ${error.message}`);
    } finally {
        isAnalyzing = false;
    }
}

/* =============================================================================
   RESULT DISPLAY
============================================================================= */
function showDefaultResults() {
    const sections = ['resultsDefault', 'resultsLoading', 'resultsContent', 'resultsError'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.hidden = id !== 'resultsDefault';
    });
}

function showLoadingState() {
    const sections = ['resultsDefault', 'resultsLoading', 'resultsContent', 'resultsError'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.hidden = id !== 'resultsLoading';
    });

    // Start loading animation
    startLoadingSteps();
}

function showResultState(data) {
    const sections = ['resultsDefault', 'resultsLoading', 'resultsContent', 'resultsError'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.hidden = id !== 'resultsContent';
    });

    // Safely update verdict badge
    const verdictBadge = document.getElementById('verdictBadge');
    if (verdictBadge && data.color) {
        verdictBadge.className = `verdict-badge ${data.color}`;
    }

    // Safely update text elements
    SecurityUtils.setTextContent(document.getElementById('verdictIcon'), data.icon || '[?]');
    SecurityUtils.setTextContent(document.getElementById('verdictName'), data.label || 'Unknown');
    SecurityUtils.setTextContent(document.getElementById('confValue'), `${data.confidence || 0}%`);
    SecurityUtils.setTextContent(document.getElementById('resultDescription'), data.description || 'No description available');

    // Update confidence bar
    const confBarFill = document.getElementById('confBarFill');
    if (confBarFill && data.color && typeof data.confidence === 'number') {
        confBarFill.className = `conf-bar-fill ${data.color}`;
        // Animate bar width
        requestAnimationFrame(() => {
            setTimeout(() => {
                confBarFill.style.width = `${Math.max(0, Math.min(100, data.confidence))}%`;
            }, 50);
        });
    }

    // Update probability bars
    updateProbabilityBars(data.class_probabilities || {});

    // Update risk features
    updateRiskFeatures(data.risk_features || []);

    // Update metadata
    SecurityUtils.setTextContent(document.getElementById('metaWords'), `${data.word_count || 0} words`);
    SecurityUtils.setTextContent(document.getElementById('metaTime'), data.timestamp || 'Unknown');
}

function updateProbabilityBars(probabilities) {
    const probBars = document.getElementById('probBars');
    if (!probBars) return;

    // Clear existing content
    probBars.innerHTML = '';

    const probColors = {
        'Safe': '#00e676',
        'Spam': '#ffb300',
        'AI Phishing': '#ff3d5a',
        'Uncertain': '#9c27b0'
    };

    Object.entries(probabilities).forEach(([label, percentage]) => {
        const row = SecurityUtils.createElement('div', 'prob-row');

        const labelSpan = SecurityUtils.createElement('span', 'prob-label', label);
        const barContainer = SecurityUtils.createElement('div', 'prob-bar-bg');
        const barFill = SecurityUtils.createElement('div', 'prob-bar-fill');
        const percentSpan = SecurityUtils.createElement('span', 'prob-pct', `${percentage}%`);

        // Safely set bar color and width
        const color = probColors[label] || '#666';
        barFill.style.background = color;
        barFill.style.width = '0%';

        barContainer.appendChild(barFill);
        row.appendChild(labelSpan);
        row.appendChild(barContainer);
        row.appendChild(percentSpan);
        probBars.appendChild(row);

        // Animate bar fill
        requestAnimationFrame(() => {
            setTimeout(() => {
                const safePercentage = Math.max(0, Math.min(100, parseFloat(percentage) || 0));
                barFill.style.width = `${safePercentage}%`;
            }, 100);
        });
    });
}

function updateRiskFeatures(features) {
    const riskList = document.getElementById('riskList');
    if (!riskList) return;

    // Clear existing content
    riskList.innerHTML = '';

    // Add each feature safely
    features.forEach(feature => {
        if (typeof feature === 'string') {
            const li = SecurityUtils.createElement('li', '', feature);
            riskList.appendChild(li);
        }
    });
}

function showError(message) {
    const sections = ['resultsDefault', 'resultsLoading', 'resultsContent', 'resultsError'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.hidden = id !== 'resultsError';
    });

    SecurityUtils.setTextContent(document.getElementById('errorMessage'), message || 'An error occurred');
}

/* =============================================================================
   LOADING ANIMATION
============================================================================= */
function startLoadingSteps() {
    const steps = ['ls1', 'ls2', 'ls3'];
    let stepIndex = 0;

    const stepInterval = setInterval(() => {
        if (stepIndex < steps.length) {
            const currentStep = document.getElementById(steps[stepIndex]);
            if (currentStep) {
                currentStep.classList.add('active');
            }

            if (stepIndex > 0) {
                const prevStep = document.getElementById(steps[stepIndex - 1]);
                if (prevStep) {
                    prevStep.classList.remove('active');
                    prevStep.classList.add('done');
                }
            }
            stepIndex++;
        } else {
            clearInterval(stepInterval);
        }
    }, 350);

    return stepInterval;
}

/* =============================================================================
   HISTORY MANAGEMENT
============================================================================= */
function addToHistory(emailText, result) {
    try {
        let history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        const createdAt = new Date();

        const entry = {
            id: Date.now(),
            createdAt: createdAt.toISOString(),
            timestamp: createdAt.toLocaleString(),
            preview: emailText.substring(0, 100) + (emailText.length > 100 ? '...' : ''),
            result: {
                label: result.short_label || 'Unknown',
                color: result.color || 'uncertain',
                confidence: result.confidence || 0
            },
            wordCount: result.word_count || 0
        };

        history.unshift(entry);

        // Keep only last 50 entries
        if (history.length > 50) {
            history = history.slice(0, 50);
        }

        localStorage.setItem('emailHistory', JSON.stringify(history));
        updateHistoryBadge();

    } catch (error) {
        console.error('Failed to save to history:', error);
    }
}

function renderHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        const historyList = document.getElementById('historyList');

        if (!historyList) return;

        if (history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">No analysis history yet. Analyze some emails to see them here!</div>';
            return;
        }

        historyList.innerHTML = '';

        history.forEach(entry => {
            const historyCard = SecurityUtils.createElement('div', 'history-card');

            // Create safe HTML structure
            const header = SecurityUtils.createElement('div', 'history-header');
            const badge = SecurityUtils.createElement('span', `history-badge ${entry.result.color}`, entry.result.label);
            const confidence = SecurityUtils.createElement('span', 'history-confidence', `${entry.result.confidence}%`);

            header.appendChild(badge);
            header.appendChild(confidence);

            const preview = SecurityUtils.createElement('div', 'history-preview', entry.preview);

            const meta = SecurityUtils.createElement('div', 'history-meta');
            const time = SecurityUtils.createElement('span', '', entry.timestamp);
            const words = SecurityUtils.createElement('span', '', `${entry.wordCount} words`);

            meta.appendChild(time);
            meta.appendChild(document.createTextNode(' \u2022 '));
            meta.appendChild(words);

            historyCard.appendChild(header);
            historyCard.appendChild(preview);
            historyCard.appendChild(meta);

            historyList.appendChild(historyCard);
        });

    } catch (error) {
        console.error('Failed to render history:', error);
        const historyList = document.getElementById('historyList');
        if (historyList) {
            historyList.innerHTML = '<div class="error-state">Failed to load history</div>';
        }
    }
}

function updateHistoryBadge() {
    try {
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        const badge = document.getElementById('historyBadge');
        if (badge) {
            SecurityUtils.setTextContent(badge, history.length.toString());
        }
    } catch (error) {
        console.error('Failed to update history badge:', error);
    }
}

function clearHistory() {
    if (confirm('Are you sure you want to clear all analysis history? This cannot be undone.')) {
        localStorage.removeItem('emailHistory');
        renderHistory();
        updateHistoryBadge();
    }
}

/* =============================================================================
   RETRY FUNCTIONALITY
============================================================================= */
function retryAnalysis() {
    if (currentAnalysis) {
        analyzeEmail();
    } else {
        showDefaultResults();
    }
}

/* =============================================================================
   COPY, EXPORT, AND SHARE FUNCTIONALITY
============================================================================= */
function copyResults() {
    if (!currentAnalysis) {
        showToast('No results to copy', 'error');
        return;
    }

    const results = `
AI Email Security Analysis Results
==================================
Verdict: ${currentAnalysis.label}
Confidence: ${currentAnalysis.confidence}%
Description: ${currentAnalysis.description}

Class Probabilities:
${Object.entries(currentAnalysis.class_probabilities || {}).map(([k, v]) => `  - ${k}: ${v}%`).join('\n')}

Risk Indicators:
${(currentAnalysis.risk_features || []).map(f => `  • ${f}`).join('\n')}

Analysis Time: ${currentAnalysis.timestamp}
Word Count: ${currentAnalysis.word_count}
    `.trim();

    navigator.clipboard.writeText(results).then(() => {
        showToast('Results copied to clipboard!', 'success');
        const btn = document.querySelector('.result-action-btn');
        if (btn) {
            btn.classList.add('copy-success');
            setTimeout(() => btn.classList.remove('copy-success'), 300);
        }
    }).catch(() => {
        showToast('Failed to copy results', 'error');
    });
}

function exportJSON() {
    if (!currentAnalysis) {
        showToast('No results to export', 'error');
        return;
    }

    const data = {
        ...currentAnalysis,
        exported_at: new Date().toISOString(),
        app_version: '2.0'
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadBlob(blob, `email-analysis-${Date.now()}.json`);
    showToast('JSON exported successfully!', 'success');
}

function exportCSV() {
    if (!currentAnalysis) {
        showToast('No results to export', 'error');
        return;
    }

    const headers = ['Label', 'Confidence', 'Safe%', 'Spam%', 'Phishing%', 'WordCount', 'Timestamp'];
    const probs = currentAnalysis.class_probabilities || {};
    const row = [
        currentAnalysis.label,
        currentAnalysis.confidence,
        probs['Safe'] || 0,
        probs['Spam'] || 0,
        probs['AI Phishing'] || 0,
        currentAnalysis.word_count,
        currentAnalysis.timestamp
    ];

    const csvContent = [headers.join(','), row.join(',')].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, `email-analysis-${Date.now()}.csv`);
    showToast('CSV exported successfully!', 'success');
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/* =============================================================================
   TOAST NOTIFICATIONS
============================================================================= */
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✓', error: '✗', info: 'ℹ' };
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ'}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 4000);
}

/* =============================================================================
   HISTORY SEARCH AND FILTER
============================================================================= */
function filterHistory() {
    const searchTerm = document.getElementById('historySearch')?.value.toLowerCase() || '';
    const filterType = document.getElementById('historyFilter')?.value || 'all';

    try {
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        const filtered = history.filter(entry => {
            const matchesSearch = entry.preview.toLowerCase().includes(searchTerm) ||
                entry.result.label.toLowerCase().includes(searchTerm);
            const matchesFilter = filterType === 'all' ||
                entry.result.color === filterType ||
                entry.result.label.toLowerCase().includes(filterType);
            return matchesSearch && matchesFilter;
        });

        renderFilteredHistory(filtered);
    } catch (error) {
        console.error('Failed to filter history:', error);
    }
}

function renderFilteredHistory(history) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    if (history.length === 0) {
        historyList.innerHTML = '<div class="empty-state"><span>🔍</span><p>No matching results found.</p></div>';
        return;
    }

    historyList.innerHTML = '';
    history.forEach(entry => {
        const historyCard = SecurityUtils.createElement('div', 'history-card');
        const header = SecurityUtils.createElement('div', 'history-header');
        const badge = SecurityUtils.createElement('span', `history-badge ${entry.result.color}`, entry.result.label);
        const confidence = SecurityUtils.createElement('span', 'history-confidence', `${entry.result.confidence}%`);

        header.appendChild(badge);
        header.appendChild(confidence);

        const preview = SecurityUtils.createElement('div', 'history-preview', entry.preview);
        const meta = SecurityUtils.createElement('div', 'history-meta');
        const time = SecurityUtils.createElement('span', '', entry.timestamp);
        const words = SecurityUtils.createElement('span', '', `${entry.wordCount} words`);

        meta.appendChild(time);
        meta.appendChild(document.createTextNode(' • '));
        meta.appendChild(words);

        historyCard.appendChild(header);
        historyCard.appendChild(preview);
        historyCard.appendChild(meta);
        historyList.appendChild(historyCard);
    });
}

function updateHistoryStats() {
    try {
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        const stats = { safe: 0, spam: 0, phishing: 0, uncertain: 0 };

        history.forEach(entry => {
            const color = entry.result.color || 'uncertain';
            if (stats.hasOwnProperty(color)) stats[color]++;
        });

        document.getElementById('statSafe')?.textContent && (document.getElementById('statSafe').textContent = stats.safe);
        document.getElementById('statSpam')?.textContent && (document.getElementById('statSpam').textContent = stats.spam);
        document.getElementById('statPhishing')?.textContent && (document.getElementById('statPhishing').textContent = stats.phishing);
        document.getElementById('statUncertain')?.textContent && (document.getElementById('statUncertain').textContent = stats.uncertain);
    } catch (error) {
        console.error('Failed to update history stats:', error);
    }
}

function exportHistoryCSV() {
    try {
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
        if (history.length === 0) {
            showToast('No history to export', 'error');
            return;
        }

        const headers = ['ID', 'Timestamp', 'Label', 'Confidence', 'WordCount', 'Preview'];
        const rows = history.map(entry => [
            entry.id,
            entry.timestamp,
            entry.result.label,
            entry.result.confidence,
            entry.wordCount,
            `"${entry.preview.replace(/"/g, '""')}"`
        ].join(','));

        const csvContent = [headers.join(','), ...rows].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        downloadBlob(blob, `email-history-${Date.now()}.csv`);
        showToast('History exported successfully!', 'success');
    } catch (error) {
        console.error('Failed to export history:', error);
        showToast('Failed to export history', 'error');
    }
}

/* =============================================================================
   DASHBOARD FUNCTIONALITY
============================================================================= */
function updateDashboard() {
    try {
        const period = document.getElementById('dashboardPeriod')?.value || '30';
        const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');

        // Filter by period
        const now = new Date();
        const filtered = period === 'all' ? history : history.filter(entry => {
            const entryDate = new Date(entry.createdAt || entry.timestamp);
            if (Number.isNaN(entryDate.getTime())) {
                return true;
            }
            const daysDiff = (now - entryDate) / (1000 * 60 * 60 * 24);
            return daysDiff <= parseInt(period);
        });

        // Calculate stats
        const stats = { total: filtered.length, safe: 0, spam: 0, phishing: 0, uncertain: 0 };
        let totalConfidence = 0;
        const confBuckets = { high: 0, med: 0, low: 0 };

        filtered.forEach(entry => {
            const color = entry.result.color || 'uncertain';
            if (stats.hasOwnProperty(color)) stats[color]++;

            const conf = entry.result.confidence || 0;
            totalConfidence += conf;

            if (conf >= 90) confBuckets.high++;
            else if (conf >= 70) confBuckets.med++;
            else confBuckets.low++;
        });

        const avgConf = stats.total > 0 ? (totalConfidence / stats.total).toFixed(1) : 0;
        const threatRate = stats.total > 0 ? ((stats.spam + stats.phishing) / stats.total * 100).toFixed(1) : 0;

        // Update UI
        SecurityUtils.setTextContent(document.getElementById('dashTotal'), stats.total);
        SecurityUtils.setTextContent(document.getElementById('dashSafe'), stats.safe);
        SecurityUtils.setTextContent(document.getElementById('dashSpam'), stats.spam);
        SecurityUtils.setTextContent(document.getElementById('dashPhishing'), stats.phishing);

        const safePercent = stats.total > 0 ? (stats.safe / stats.total * 100).toFixed(1) : 0;
        const spamPercent = stats.total > 0 ? (stats.spam / stats.total * 100).toFixed(1) : 0;
        const phishPercent = stats.total > 0 ? (stats.phishing / stats.total * 100).toFixed(1) : 0;

        SecurityUtils.setTextContent(document.getElementById('dashSafePercent'), `${safePercent}%`);
        SecurityUtils.setTextContent(document.getElementById('dashSpamPercent'), `${spamPercent}%`);
        SecurityUtils.setTextContent(document.getElementById('dashPhishingPercent'), `${phishPercent}%`);
        SecurityUtils.setTextContent(document.getElementById('dashAvgConf'), `${avgConf}%`);

        SecurityUtils.setTextContent(document.getElementById('confHigh'), confBuckets.high);
        SecurityUtils.setTextContent(document.getElementById('confMed'), confBuckets.med);
        SecurityUtils.setTextContent(document.getElementById('confLow'), confBuckets.low);

        // Update risk meter
        const riskLevel = document.getElementById('riskLevel');
        const riskFill = document.getElementById('riskFill');
        const riskNote = document.getElementById('riskNote');

        if (riskLevel && riskFill) {
            if (threatRate < 10) {
                riskLevel.textContent = 'LOW';
                riskLevel.style.color = 'var(--safe)';
                riskFill.style.width = '20%';
                riskFill.style.background = 'var(--safe)';
            } else if (threatRate < 30) {
                riskLevel.textContent = 'MEDIUM';
                riskLevel.style.color = 'var(--spam)';
                riskFill.style.width = '50%';
                riskFill.style.background = 'var(--spam)';
            } else {
                riskLevel.textContent = 'HIGH';
                riskLevel.style.color = 'var(--phishing)';
                riskFill.style.width = '80%';
                riskFill.style.background = 'var(--phishing)';
            }
            if (riskNote) riskNote.textContent = `${threatRate}% threat detection rate`;
        }

        // Update charts
        updateDistributionChart(stats);
        updateTrendChart(filtered);

        // Update recent threats
        updateRecentThreats(filtered);

    } catch (error) {
        console.error('Failed to update dashboard:', error);
    }
}

function updateDistributionChart(stats) {
    const canvas = document.getElementById('distributionChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.offsetWidth;
    const height = 200;

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    const data = [stats.safe, stats.spam, stats.phishing, stats.uncertain];
    const colors = ['#00e676', '#ffb300', '#ff3d5a', '#9c27b0'];
    const labels = ['Safe', 'Spam', 'Phishing', 'Uncertain'];
    const total = data.reduce((a, b) => a + b, 0);

    if (total === 0) {
        ctx.fillStyle = 'var(--text-muted)';
        ctx.font = '14px Space Mono';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', width / 2, height / 2);
        return;
    }

    // Draw bars
    const barWidth = (width - 100) / 4;
    const maxHeight = height - 60;
    const maxVal = Math.max(...data, 1);

    data.forEach((val, i) => {
        const x = 40 + i * (barWidth + 10);
        const barHeight = (val / maxVal) * maxHeight;
        const y = height - 40 - barHeight;

        ctx.fillStyle = colors[i];
        ctx.fillRect(x, y, barWidth - 10, barHeight);

        // Label
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-muted');
        ctx.font = '10px Space Mono';
        ctx.textAlign = 'center';
        ctx.fillText(labels[i], x + (barWidth - 10) / 2, height - 20);
        ctx.fillText(val.toString(), x + (barWidth - 10) / 2, y - 5);
    });
}

function updateTrendChart(history) {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.offsetWidth;
    const height = 200;

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    if (history.length === 0) {
        ctx.fillStyle = 'var(--text-muted)';
        ctx.font = '14px Space Mono';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', width / 2, height / 2);
        return;
    }

    // Group by day
    const dailyData = {};
    history.forEach(entry => {
        const rawDate = new Date(entry.createdAt || entry.timestamp);
        if (Number.isNaN(rawDate.getTime())) {
            return;
        }
        const date = rawDate.toLocaleDateString();
        dailyData[date] = (dailyData[date] || 0) + 1;
    });

    const dates = Object.keys(dailyData).slice(-7);
    const values = dates.map(d => dailyData[d]);
    const maxVal = Math.max(...values, 1);

    // Draw line chart
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    ctx.strokeStyle = 'var(--accent)';
    ctx.lineWidth = 2;
    ctx.beginPath();

    dates.forEach((date, i) => {
        const x = padding + (i / (dates.length - 1 || 1)) * chartWidth;
        const y = height - padding - (values[i] / maxVal) * chartHeight;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);

        // Draw point
        ctx.fillStyle = 'var(--accent)';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });

    ctx.stroke();

    // X-axis labels
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-muted');
    ctx.font = '9px Space Mono';
    ctx.textAlign = 'center';
    dates.forEach((date, i) => {
        const x = padding + (i / (dates.length - 1 || 1)) * chartWidth;
        ctx.fillText(date.slice(0, 5), x, height - 10);
    });
}

function updateRecentThreats(history) {
    const threatList = document.getElementById('threatList');
    if (!threatList) return;

    const threats = history.filter(e => e.result.color === 'spam' || e.result.color === 'phishing')
        .slice(0, 5);

    if (threats.length === 0) {
        threatList.innerHTML = '<div class="empty-state">No recent threats detected</div>';
        return;
    }

    threatList.innerHTML = '';
    threats.forEach(threat => {
        const item = SecurityUtils.createElement('div', 'threat-item');
        const type = SecurityUtils.createElement('span', 'threat-type', `[${String(threat.result.label || '').toUpperCase()}]`);
        const preview = SecurityUtils.createElement('span', 'threat-preview', `${threat.preview.substring(0, 40)}...`);
        const time = SecurityUtils.createElement('span', 'threat-time', threat.timestamp);

        item.appendChild(type);
        item.appendChild(preview);
        item.appendChild(time);
        threatList.appendChild(item);
    });
}

function refreshDashboard() {
    updateDashboard();
    showToast('Dashboard refreshed!', 'success');
}

/* =============================================================================
   BULK ANALYSIS FUNCTIONALITY
============================================================================= */
let bulkResults = [];

async function handleBulkUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    if (files.length > 50) {
        showToast('Maximum 50 files allowed', 'error');
        return;
    }

    const emails = [];

    for (const file of files) {
        try {
            const content = await readFileAsText(file);

            if (file.name.endsWith('.csv')) {
                // Parse CSV - assume one email per row
                const lines = content.split('\n').filter(l => l.trim());
                lines.forEach((line, i) => {
                    if (i > 0 && line.trim()) { // Skip header
                        emails.push({ filename: `${file.name}:row${i + 1}`, content: line });
                    }
                });
            } else {
                emails.push({ filename: file.name, content: content });
            }
        } catch (error) {
            console.error(`Failed to read ${file.name}:`, error);
        }
    }

    if (emails.length > 0) {
        document.getElementById('bulkEmailInput').value = emails.map(e => e.content).join('\n---\n');
        showToast(`Loaded ${emails.length} emails from ${files.length} files`, 'success');
    }

    event.target.value = '';
}

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
    });
}

async function analyzeBulk() {
    const input = document.getElementById('bulkEmailInput')?.value || '';
    if (!input.trim()) {
        showToast('Please enter emails to analyze', 'error');
        return;
    }
    let emails = [];
    try {
        if (input.trim().startsWith('[')) {
            emails = JSON.parse(input);
            if (!Array.isArray(emails)) emails = [];
        }
    } catch (e) { }

    if (emails.length === 0) {
        emails = input.split(/(?:\n\s*\n|---)/).map(e => String(e).trim()).filter(e => e.length >= 10);
    }
    if (emails.length === 0) {
        showToast('No valid emails found (minimum 10 characters each)', 'error');
        return;
    }

    if (emails.length > 100) {
        showToast('Maximum 100 emails per batch', 'error');
        return;
    }

    // Show progress
    const progressEl = document.getElementById('bulkProgress');
    const progressFill = document.getElementById('bulkProgressFill');
    const progressText = document.getElementById('bulkProgressText');
    const summaryEl = document.getElementById('bulkSummary');
    const resultsEl = document.getElementById('bulkResultsList');

    if (progressEl) progressEl.hidden = false;
    if (summaryEl) summaryEl.hidden = true;

    bulkResults = [];
    const summary = { safe: 0, spam: 0, phishing: 0, uncertain: 0 };

    if (progressFill) progressFill.style.width = '15%';
    if (progressText) progressText.textContent = `0 / ${emails.length} analyzed`;

    try {
        const response = await fetch('/bulk-predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': SecurityUtils.getCSRFToken()
            },
            body: JSON.stringify({ emails })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const data = await response.json();
        const results = Array.isArray(data.results) ? data.results : [];

        results.forEach((result, index) => {
            const previewText = `${emails[index].substring(0, 50)}...`;

            if (result.error) {
                bulkResults.push({
                    index: index + 1,
                    preview: previewText,
                    error: true
                });
                return;
            }

            bulkResults.push({
                index: index + 1,
                preview: previewText,
                result
            });

            const color = result.color || 'uncertain';
            if (summary.hasOwnProperty(color)) {
                summary[color]++;
            }

            addToHistory(emails[index], result);
        });

        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = `${results.length} / ${emails.length} analyzed`;
    } catch (error) {
        console.error('Bulk analysis failed:', error);
        if (progressEl) progressEl.hidden = true;
        showToast(`Bulk analysis failed: ${error.message}`, 'error');
        return;
    }

    // Show summary
    if (summaryEl) summaryEl.hidden = false;
    SecurityUtils.setTextContent(document.getElementById('bulkSafe'), String(summary.safe));
    SecurityUtils.setTextContent(document.getElementById('bulkSpam'), String(summary.spam));
    SecurityUtils.setTextContent(document.getElementById('bulkPhishing'), String(summary.phishing));
    SecurityUtils.setTextContent(document.getElementById('bulkUncertain'), String(summary.uncertain));

    // Enable export
    const exportBtn = document.getElementById('exportBulkBtn');
    if (exportBtn) exportBtn.disabled = false;

    // Render results
    renderBulkResults();

    showToast(`Analyzed ${emails.length} emails successfully!`, 'success');
}

function renderBulkResults() {
    const resultsEl = document.getElementById('bulkResultsList');
    if (!resultsEl) return;

    if (bulkResults.length === 0) {
        resultsEl.innerHTML = '<div class="empty-state"><span>[BATCH]</span><p>No results yet.</p></div>';
        return;
    }

    resultsEl.innerHTML = '';
    bulkResults.forEach(item => {
        const resultItem = SecurityUtils.createElement('div', `bulk-result-item ${item.error ? '' : item.result.color}`);

        if (item.error) {
            resultItem.innerHTML = `
                <div class="bulk-result-info">
                    <div class="bulk-result-preview">#${item.index}: ${item.preview}</div>
                </div>
                <div class="bulk-result-meta">
                    <span class="bulk-result-badge uncertain">ERROR</span>
                </div>
            `;
        } else {
            resultItem.innerHTML = `
                <div class="bulk-result-info">
                    <div class="bulk-result-preview">#${item.index}: ${item.preview}</div>
                </div>
                <div class="bulk-result-meta">
                    <span class="bulk-result-badge ${item.result.color}">${item.result.short_label}</span>
                    <span class="bulk-result-conf">${item.result.confidence}%</span>
                </div>
            `;
        }

        resultsEl.appendChild(resultItem);
    });
}

function clearBulkResults() {
    bulkResults = [];
    document.getElementById('bulkEmailInput').value = '';
    document.getElementById('bulkProgress').hidden = true;
    document.getElementById('bulkSummary').hidden = true;
    document.getElementById('bulkProgressFill').style.width = '0%';
    document.getElementById('bulkProgressText').textContent = '0 / 0 analyzed';
    SecurityUtils.setTextContent(document.getElementById('bulkSafe'), '0');
    SecurityUtils.setTextContent(document.getElementById('bulkSpam'), '0');
    SecurityUtils.setTextContent(document.getElementById('bulkPhishing'), '0');
    SecurityUtils.setTextContent(document.getElementById('bulkUncertain'), '0');
    document.getElementById('exportBulkBtn').disabled = true;
    document.getElementById('bulkResultsList').innerHTML = '<div class="empty-state"><span>[BATCH]</span><p>Upload files or paste emails to analyze multiple at once.</p></div>';
    showToast('Bulk results cleared', 'info');
}

function exportBulkCSV() {
    if (bulkResults.length === 0) {
        showToast('No results to export', 'error');
        return;
    }

    const headers = ['#', 'Label', 'Confidence', 'Safe%', 'Spam%', 'Phishing%', 'Preview'];
    const rows = bulkResults.filter(r => !r.error).map(item => {
        const probs = item.result.class_probabilities || {};
        return [
            item.index,
            item.result.label,
            item.result.confidence,
            probs['Safe'] || 0,
            probs['Spam'] || 0,
            probs['AI Phishing'] || 0,
            `"${item.preview.replace(/"/g, '""')}"`
        ].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, `bulk-analysis-${Date.now()}.csv`);
    showToast('Bulk results exported!', 'success');
}

/* =============================================================================
   KEYBOARD SHORTCUTS
============================================================================= */
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter = Analyze
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const activeSection = document.querySelector('.content-section.active');
        if (activeSection?.id === 'section-detector') {
            analyzeEmail();
        } else if (activeSection?.id === 'section-bulk') {
            analyzeBulk();
        }
    }

    // Ctrl/Cmd + K = Clear
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        clearAll();
    }

    // Ctrl/Cmd + Shift + C = Copy results
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        copyResults();
    }

    // Ctrl/Cmd + E = Export JSON
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportJSON();
    }

    // Number keys for navigation
    if (e.altKey) {
        switch (e.key) {
            case '1': showSection('detector'); break;
            case '2': showSection('history'); break;
            case '3': showSection('dashboard'); break;
            case '4': showSection('bulk'); break;
            case '5': showSection('about'); break;
        }
    }
});

/* =============================================================================
   ENHANCED INITIALIZATION
============================================================================= */
// Override the existing showSection to handle new sections
// const originalShowSection = typeof showSection === 'function' ? showSection : null;

// function showSection(name) {
//     // Hide all sections
//     document.querySelectorAll('.content-section').forEach(section => {
//         section.hidden = true;
//         section.classList.remove('active');
//     });

//     // Show target section
//     const targetSection = document.getElementById(`section-${name}`);
//     if (targetSection) {
//         targetSection.hidden = false;
//         targetSection.classList.add('active');
//     }

//     // Update navigation
//     document.querySelectorAll('.nav-btn').forEach(btn => {
//         btn.classList.remove('active');
//         btn.removeAttribute('aria-current');
//     });

//     const activeButton = [...document.querySelectorAll('.nav-btn')]
//         .find(btn => btn.textContent.toLowerCase().includes(name));
//     if (activeButton) {
//         activeButton.classList.add('active');
//         activeButton.setAttribute('aria-current', 'page');
//     }

//     // Section-specific initialization
//     if (name === 'history') {
//         renderHistory();
//         updateHistoryStats();
//     } else if (name === 'dashboard') {
//         updateDashboard();
//     }
// }

// Enhanced renderHistory to call stats update
const originalRenderHistory = typeof renderHistory === 'function' ? renderHistory : null;
