// ========================================
// CryptoNest Dashboard - FIXED Chart + Prices
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    initDeleteConfirmations();
    initFormEnhancements();
    initActionButtons();
    initAutoHideAlerts();
    initCurrencyChange();
});

// ========================================
// 1. CURRENCY HANDLER
// ========================================
function initCurrencyChange() {
    const currencySelect = document.getElementById('currency-select');
    if (currencySelect) {
        currencySelect.addEventListener('change', function() {
            changeCurrency(this.value);
        });
    }
}

window.changeCurrency = function(currency) {
    const url = new URL(window.location.href);
    url.searchParams.set('currency', currency);
    window.location.href = url.toString();
};

// ========================================
// 2. FIXED CHARTS - CLEAN NUMBER PARSING
// ========================================
function initCharts() {
    const portfolioChartCanvas = document.getElementById('portfolio-chart');
    if (portfolioChartCanvas) {
        initPortfolioChart(portfolioChartCanvas);
    }
}

function initPortfolioChart(canvas) {
    try {
        const currencySymbol = document.body.getAttribute('data-currency-symbol') || '$';
        
        const rows = document.querySelectorAll('.portfolio-row');
        if (rows.length === 0) {
            console.log('No portfolio rows');
            return;
        }
        
        const labels = [];
        const data = [];
        
        // Collect ALL coin data first
        rows.forEach((row, index) => {
            const coinName = row.querySelector('.coin-name')?.textContent.trim() || `Coin ${index + 1}`;
            const valueCell = row.querySelector('.value-cell');
            const quantityCell = row.querySelector('.number-cell');
            
            if (valueCell && quantityCell) {
                let valueText = valueCell.textContent || '0';
                valueText = valueText.replace(/[^\d.,-]/g, '').replace(/,/g, '');
                let value = parseFloat(valueText) || 0;
                
                let qtyText = quantityCell.textContent || '0';
                qtyText = qtyText.replace(/[^\d.]/g, '');
                const qty = parseFloat(qtyText) || 0;
                
                console.log(`${coinName}: value=${value}, qty=${qty}`);
                
                if (qty > 0) {
                    // Scale tiny values for visibility
                    if (value < 0.01) value = 0.01;
                    labels.push(coinName);
                    data.push(value);
                }
            }
        });
        
        console.log('RAINBOW CHART:', labels.length, 'coins');
        
        if (labels.length === 0) return;
        
        // ULTIMATE RAINBOW COLORS - 50+ UNIQUE COLORS!
        const rainbowColors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA', '#F1948A', '#85C1E9',
            '#F7DC6F', '#D7BDE2', '#A9DFBF', '#FAD7A8', '#D5A6BD', '#AED6F1', '#F9E79F',
            '#D2B4DE', '#A3E4D7', '#FAD5A5', '#D4A5A5', '#B2EBF2', '#F4D03F', '#E8DAEF',
            '#A9DFBF', '#FAD7A8', '#D5A6BD', '#AED6F1', '#F9E79F', '#D2B4DE', '#A3E4D7',
            '#F8C7CC', '#D0ECE7', '#FADBC9', '#E8F6F3', '#D5DBDB', '#FAD7A8', '#E6B0AA',
            '#C0EB75', '#F1948A', '#85C1E9', '#F7DC6F', '#D7BDE2', '#A9DFBF'
        ];
        
        // Generate DYNAMIC colors if more than 50 coins
        function getDynamicColor(index) {
            const hue = (index * 137.508) % 360; // Golden angle for max variety
            return `hsl(${hue}, 70%, 55%)`;
        }
        
        const colors = labels.map((_, index) => {
            return index < rainbowColors.length ? rainbowColors[index] : getDynamicColor(index);
        });
        
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 12,
                    spacing: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            padding: 25,
                            usePointStyle: true,
                            font: { size: 13, weight: 'bold' },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label} (${percentage}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: '#ffffff',
                                        lineWidth: 3,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ffffff',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${currencySymbol}${context.parsed.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 2000
                }
            }
        });
        
        console.log('RAINBOW CHART LOADED! ', colors.length, 'colors');
    } catch (error) {
        console.error('Chart error:', error);
    }
}



// ========================================
// 4. FORM ENHANCEMENTS
// ========================================
function initFormEnhancements() {
    const symbolInput = document.getElementById('coin-symbol');
    const buyPriceInput = document.getElementById('buy-price');
    const quantityInput = document.getElementById('coin-quantity');
    const dateInput = document.getElementById('buy-date');

    if (symbolInput) {
        symbolInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z]/g, '');
        });
    }

    if (buyPriceInput) {
        buyPriceInput.addEventListener('input', function() {
            if (this.value && parseFloat(this.value) <= 0) {
                this.value = '';
            }
        });
    }

    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            if (this.value && parseFloat(this.value) <= 0) {
                this.value = '';
            }
        });
    }

    if (dateInput) {
        dateInput.valueAsDate = new Date();
    }

    const inputs = [buyPriceInput, quantityInput];
    inputs.forEach(input => {
        if (input) {
            input.addEventListener('input', calculatePortfolioValue);
        }
    });
}

function calculatePortfolioValue() {
    const buyPrice = parseFloat(document.getElementById('buy-price')?.value) || 0;
    const quantity = parseFloat(document.getElementById('coin-quantity')?.value) || 0;
    const totalValue = buyPrice * quantity;
    console.log(`Preview value: ${totalValue.toLocaleString()}`);
}

// ========================================
// 5. ACTION BUTTONS
// ========================================
function initActionButtons() {
    const walletBtn = document.getElementById('connect-wallet-btn');
    const exchangeBtn = document.getElementById('connect-exchange-btn');
    const exportCsvBtn = document.getElementById('export-csv');
    const logoutBtn = document.getElementById('logout-btn');

    if (walletBtn) {
        walletBtn.addEventListener('click', function() {
            this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Connecting...';
            this.disabled = true;
            setTimeout(() => {
                this.innerHTML = '<i class="fa-solid fa-check-circle"></i> Wallet Connected';
                this.className = 'btn-success btn-large';
            }, 2000);
        });
    }

    if (exchangeBtn) {
        exchangeBtn.addEventListener('click', function() {
            this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Connecting...';
            this.disabled = true;
            setTimeout(() => {
                this.innerHTML = '<i class="fa-solid fa-check-circle"></i> Exchange Connected';
                this.className = 'btn-success btn-large';
            }, 2000);
        });
    }

    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function(e) {
            const currency = document.getElementById('currency-select')?.value || 'USD';
            const filename = `cryptonest-portfolio-${currency}-${new Date().toISOString().split('T')[0]}.csv`;
            this.download = filename;
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }
}

// ========================================
// 6. AUTO-HIDE ALERTS
// ========================================
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}
