// ================= MAIN LANDING PAGE JS =================
document.addEventListener('DOMContentLoaded', function() {
    // Preloader - Updated ID
    const preloader = document.getElementById('preloader');
    if (preloader) {
        window.addEventListener('load', () => {
            preloader.style.opacity = '0';
            preloader.style.transition = 'opacity 0.5s';
            setTimeout(() => preloader.remove(), 500);
        });
    }

    // Navbar scroll effect - Updated ID
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('main-navbar');
        if (navbar) {
            if (window.scrollY > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    });

    // Smooth scrolling for nav links - Updated href targets
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    });

    // Mobile menu toggle - Updated ID
    const mobileToggle = document.getElementById('mobile-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            const navbar = document.getElementById('main-navbar');
            navbar.classList.toggle('mobile-open');
        });
    }

    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 🚀 CURRENCY SELECTOR FUNCTION
    window.changeCurrency = function(currency) {
        // Update URL with currency param
        const url = new URL(window.location);
        url.searchParams.set('currency', currency);
        window.location.href = url.toString();
    }
});

// Global HomePageTracker class - WITH CURRENCY SUPPORT
class HomePageTracker {
    constructor() {
        this.currentCurrency = 'USD';
        this.currencySymbol = '$';
        this.init();
    }

    async init() {
        // Get currency from HTML data attribute or default USD
        const currencySelect = document.getElementById('currency-select');
        if (currencySelect) {
            this.currentCurrency = currencySelect.value;
            this.updateCurrencySymbol();
            currencySelect.addEventListener('change', (e) => {
                this.currentCurrency = e.target.value;
                this.updateCurrencySymbol();
                this.loadTop50Coins(); // Reload with new currency
            });
        }
        
        await this.loadTop50Coins();
        this.loadTrendingCoins();
        this.startAutoRefresh();
    }

    updateCurrencySymbol() {
        const symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 
            'INR': '₹', 'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$'
        };
        this.currencySymbol = symbols[this.currentCurrency] || '$';
    }

    async loadTop50Coins() {
        try {
            // ✅ CURRENCY SUPPORT - Uses selected currency!
            const url = `https://api.coingecko.com/api/v3/coins/markets?vs_currency=${this.currentCurrency.toLowerCase()}&order=market_cap_desc&per_page=50&page=1&sparkline=false&price_change_percentage=24h`;
            const response = await fetch(url);
            const coins = await response.json();
            
            const container = document.getElementById('coins-list');
            if (container) {
                container.innerHTML = coins.map((coin, index) => `
                    <div class="coin-row">
                        <span class="rank">${index + 1}</span>
                        <div class="coin-info">
                            <img src="${coin.image}" alt="${coin.name}" width="24" height="24" loading="lazy">
                            <div>
                                <div class="coin-name">${coin.name}</div>
                                <div class="coin-symbol">${coin.symbol.toUpperCase()}</div>
                            </div>
                        </div>
                        <span class="price">${this.currencySymbol}${coin.current_price.toLocaleString()}</span>
                        <span class="change ${coin.price_change_percentage_24h >= 0 ? 'positive' : 'negative'}">
                            ${coin.price_change_percentage_24h ? coin.price_change_percentage_24h.toFixed(2) + '%' : '0.00%'}
                        </span>
                        <span class="market-cap">${this.currencySymbol}${this.formatMarketCap(coin.market_cap)}</span>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading top 50:', error);
        }
    }

    loadTrendingCoins() {
        const trending = [
            { name: 'PEPE', symbol: 'PEPE', change: '+15.2%', price: `${this.currencySymbol}0.000012` },
            { name: 'WIF', symbol: 'WIF', change: '+12.8%', price: `${this.currencySymbol}2.45` },
            { name: 'BONK', symbol: 'BONK', change: '-8.3%', price: `${this.currencySymbol}0.000034` },
            { name: 'FLOKI', symbol: 'FLOKI', change: '+9.7%', price: `${this.currencySymbol}0.00023` },
        ];
        
        const container = document.getElementById('trending-coins');
        if (container) {
            container.innerHTML = trending.map(coin => `
                <div class="trending-card">
                    <div class="trending-header">
                        <span class="trending-emoji">🔥</span>
                        <div>
                            <div class="coin-name">${coin.name}</div>
                            <div class="coin-symbol">${coin.symbol}</div>
                        </div>
                    </div>
                    <div class="trending-price">${coin.price}</div>
                    <span class="trending-change ${coin.change.startsWith('+') ? 'positive' : 'negative'}">${coin.change}</span>
                </div>
            `).join('');
        }
    }

    formatMarketCap(cap) {
        if (cap > 1e12) return (cap / 1e12).toFixed(2) + 'T';
        if (cap > 1e9) return (cap / 1e9).toFixed(2) + 'B';
        if (cap > 1e6) return (cap / 1e6).toFixed(0) + 'M';
        return cap.toLocaleString();
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadTop50Coins();
        }, 30000); // 30 seconds
    }
}

// Initialize tracker on home page
if (document.getElementById('coins-list')) {
    new HomePageTracker();
}
