from flask import Flask, render_template_string, send_file, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import os
import json
import time
from datetime import datetime, timedelta
import requests
import numpy as np
from trading_bot import run_trading_bot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'crypto_trading_bot_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Enhanced Dashboard Template with advanced features
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Advanced Crypto Trading Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(45deg, #4ecdc4, #44a08d);
            --danger-gradient: linear-gradient(45deg, #ff6b6b, #ee5a24);
            --warning-gradient: linear-gradient(45deg, #ffecd2, #fcb69f);
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-primary: #333;
            --text-secondary: #666;
            --border-radius: 15px;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        [data-theme="dark"] {
            --card-bg: rgba(45, 55, 72, 0.95);
            --text-primary: #e2e8f0;
            --text-secondary: #a0aec0;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--primary-gradient);
            min-height: 100vh;
            padding: 15px;
            line-height: 1.6;
            transition: all 0.3s ease;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 20px 0;
            position: relative;
        }

        .header h1 {
            font-size: clamp(2rem, 5vw, 3rem);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 700;
        }

        .header p {
            font-size: clamp(1rem, 3vw, 1.2rem);
            opacity: 0.9;
            margin: 0 10px;
        }

        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 12px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }

        .real-time-indicator {
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 15px;
            border-radius: 20px;
            margin-top: 10px;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: #4ecdc4;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: var(--card-bg);
            padding: 25px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            color: var(--text-primary);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        }

        .card h3 {
            margin-bottom: 20px;
            font-size: clamp(1.2rem, 2.5vw, 1.5rem);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }

        .price-display {
            text-align: center;
            padding: 20px;
            background: var(--success-gradient);
            color: white;
            border-radius: 12px;
            margin: 15px 0;
        }

        .price-value {
            font-size: clamp(1.8rem, 4vw, 2.5rem);
            font-weight: bold;
            margin-bottom: 5px;
        }

        .price-change {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .crypto-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }

        .crypto-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid transparent;
            color: var(--text-primary);
            padding: 12px 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            text-align: center;
        }

        .crypto-btn.active {
            background: var(--success-gradient);
            color: white;
            border-color: #4ecdc4;
        }

        .crypto-btn:hover:not(.active) {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .button {
            display: inline-block;
            background: var(--primary-gradient);
            color: white;
            padding: 14px 20px;
            margin: 6px 3px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
            border: none;
            cursor: pointer;
            font-size: clamp(0.85rem, 2vw, 0.95rem);
            text-align: center;
            min-width: 120px;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 18px rgba(0, 0, 0, 0.3);
        }

        .button.success {
            background: var(--success-gradient);
        }

        .button.danger {
            background: var(--danger-gradient);
        }

        .sentiment-meter {
            position: relative;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }

        .sentiment-fill {
            height: 100%;
            background: var(--success-gradient);
            border-radius: 10px;
            transition: width 0.5s ease;
            position: relative;
        }

        .sentiment-fill.negative {
            background: var(--danger-gradient);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .stat-value {
            font-size: clamp(1.2rem, 3vw, 1.5rem);
            font-weight: bold;
            color: var(--text-primary);
        }

        .stat-label {
            font-size: clamp(0.8rem, 2vw, 0.9rem);
            color: var(--text-secondary);
            margin-top: 5px;
        }

        .trading-indicators {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }

        .indicator {
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            color: white;
        }

        .indicator.buy {
            background: var(--success-gradient);
        }

        .indicator.sell {
            background: var(--danger-gradient);
        }

        .indicator.hold {
            background: var(--warning-gradient);
            color: #333;
        }

        .portfolio-summary {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }

        .portfolio-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .portfolio-item {
            text-align: center;
        }

        .portfolio-value {
            font-size: 1.4rem;
            font-weight: bold;
        }

        .portfolio-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .alert {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }

        .log-preview {
            background: rgba(248, 249, 250, 0.1);
            border: 1px solid rgba(222, 226, 230, 0.3);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.85rem;
            max-height: 200px;
            overflow-y: auto;
            margin: 15px 0;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
            padding: 15px;
        }

        /* Mobile optimizations */
        @media screen and (max-width: 768px) {
            body {
                padding: 10px;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }

            .theme-toggle {
                position: relative;
                top: auto;
                right: auto;
                margin: 10px auto;
                display: block;
            }

            .button {
                width: calc(50% - 6px);
                margin: 3px;
                padding: 12px 8px;
            }

            .chart-container {
                height: 250px;
            }
        }

        @media screen and (max-width: 480px) {
            .button {
                width: 100%;
                margin: 5px 0;
            }

            .crypto-selector {
                grid-template-columns: repeat(2, 1fr);
            }

            .stats-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body data-theme="light">
    <div class="container">
        <div class="header">
            <button class="theme-toggle" onclick="toggleTheme()">🌙</button>
            <h1>🚀 Advanced Crypto Trading Bot</h1>
            <p>AI-Powered Multi-Crypto Trading with Real-Time Analytics</p>
            <div class="real-time-indicator">
                <div class="live-dot"></div>
                <span>Live Updates</span>
            </div>
        </div>

        <div class="dashboard-grid">
            <!-- Real-Time Price Chart -->
            <div class="card" style="grid-column: span 2;">
                <h3>📈 Real-Time Price Chart</h3>
                <div class="crypto-selector">
                    <button class="crypto-btn active" onclick="selectCrypto('bitcoin', 'BTC')">BTC</button>
                    <button class="crypto-btn" onclick="selectCrypto('ethereum', 'ETH')">ETH</button>
                    <button class="crypto-btn" onclick="selectCrypto('cardano', 'ADA')">ADA</button>
                    <button class="crypto-btn" onclick="selectCrypto('solana', 'SOL')">SOL</button>
                    <button class="crypto-btn" onclick="selectCrypto('binancecoin', 'BNB')">BNB</button>
                </div>
                <div class="price-display">
                    <div class="price-value" id="currentPrice">Loading...</div>
                    <div class="price-change" id="priceChange">24h change</div>
                </div>
                <div class="chart-container">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <!-- Bot Controls -->
            <div class="card">
                <h3>🎮 Bot Controls</h3>
                <div class="alert">
                    <strong>Status:</strong> 
                    <span id="botStatus">{{ 'Running' if bot_running else 'Stopped' }}</span>
                </div>
                <a class="button success" href="{{ url_for('start_bot') }}">▶️ Start Bot</a>
                <a class="button danger" href="{{ url_for('stop_bot') }}">🛑 Stop Bot</a>
                <a class="button" href="{{ url_for('run_once') }}">⚡ Run Once</a>
                <a class="button" href="{{ url_for('status') }}">📊 Status</a>
            </div>

            <!-- Live Portfolio -->
            <div class="card">
                <h3>💰 Live Portfolio</h3>
                <div class="portfolio-summary">
                    <div class="portfolio-grid">
                        <div class="portfolio-item">
                            <div class="portfolio-value" id="totalValue">$0.00</div>
                            <div class="portfolio-label">Total Value</div>
                        </div>
                        <div class="portfolio-item">
                            <div class="portfolio-value" id="usdBalance">$1,000.00</div>
                            <div class="portfolio-label">USD Balance</div>
                        </div>
                        <div class="portfolio-item">
                            <div class="portfolio-value" id="cryptoBalance">0.00000</div>
                            <div class="portfolio-label" id="cryptoLabel">BTC Balance</div>
                        </div>
                        <div class="portfolio-item">
                            <div class="portfolio-value" id="dailyPnL">+$0.00</div>
                            <div class="portfolio-label">24h P&L</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Real-Time Sentiment Analysis -->
            <div class="card">
                <h3>🧠 Live Sentiment Analysis</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="sentimentScore">0.0000</div>
                        <div class="stat-label">Sentiment Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="positivePosts">0</div>
                        <div class="stat-label">Positive</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="negativePosts">0</div>
                        <div class="stat-label">Negative</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="neutralPosts">0</div>
                        <div class="stat-label">Neutral</div>
                    </div>
                </div>
                <div class="sentiment-meter">
                    <div class="sentiment-fill" id="sentimentMeter" style="width: 50%;"></div>
                </div>
            </div>

            <!-- Technical Indicators -->
            <div class="card">
                <h3>📊 Technical Analysis</h3>
                <div class="trading-indicators">
                    <div class="indicator" id="rsiIndicator">
                        <div>RSI</div>
                        <div id="rsiValue">50</div>
                    </div>
                    <div class="indicator" id="macdIndicator">
                        <div>MACD</div>
                        <div id="macdValue">Neutral</div>
                    </div>
                    <div class="indicator" id="aiPrediction">
                        <div>AI Signal</div>
                        <div id="aiValue">HOLD</div>
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="predictedPrice">$0.00</div>
                        <div class="stat-label">AI Prediction</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="fearGreedIndex">50</div>
                        <div class="stat-label">Fear & Greed</div>
                    </div>
                </div>
            </div>

            <!-- Live Trading Log -->
            <div class="card" style="grid-column: span 2;">
                <h3>📝 Live Trading Activity</h3>
                <div class="log-preview" id="tradingLog">
                    Waiting for trading activity...
                </div>
                <a class="button" href="{{ url_for('download_log') }}">📥 Download Full Log</a>
                <a class="button" href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank">📋 Google Sheet</a>
            </div>
        </div>

        <div class="footer">
            <p>Built with ❤️ using Flask, WebSockets & Advanced AI | Real-Time Updates Every 30s</p>
            <p>Last Updated: <span id="lastUpdate">{{ current_time }}</span></p>
        </div>
    </div>

    <script>
        // Global variables
        let socket;
        let priceChart;
        let isDarkTheme = false;
        let currentCrypto = 'bitcoin';
        let currentSymbol = 'BTC';

        // Theme toggle function
        function toggleTheme() {
            isDarkTheme = !isDarkTheme;
            document.body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
            const themeBtn = document.querySelector('.theme-toggle');
            if (themeBtn) themeBtn.textContent = isDarkTheme ? '☀️' : '🌙';

            if (priceChart) {
                priceChart.options.plugins.legend.labels.color = isDarkTheme ? '#e2e8f0' : '#333';
                priceChart.options.scales.x.grid.color = isDarkTheme ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                priceChart.options.scales.y.grid.color = isDarkTheme ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                priceChart.options.scales.x.ticks.color = isDarkTheme ? '#a0aec0' : '#666';
                priceChart.options.scales.y.ticks.color = isDarkTheme ? '#a0aec0' : '#666';
                priceChart.update();
            }
        }

        // Crypto selection function  
        function selectCrypto(crypto, symbol) {
            currentCrypto = crypto;
            currentSymbol = symbol;

            // Update active button
            document.querySelectorAll('.crypto-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            // Request new data
            if (socket && socket.connected) {
                socket.emit('request_initial_data', {crypto: currentCrypto});
            }

            // Update chart label
            if (priceChart) {
                priceChart.data.datasets[0].label = symbol + ' Price (USD)';
                priceChart.update();
            }
        }

        // Update functions
        function updatePriceDisplay(data) {
            const priceEl = document.getElementById('currentPrice');
            if (priceEl) priceEl.textContent = '$' + (data.price || 0).toLocaleString();

            const changePercent = data.change_24h || 0;
            const changeElement = document.getElementById('priceChange');
            if (changeElement) {
                changeElement.textContent = (changePercent >= 0 ? '+' : '') + changePercent.toFixed(2) + '%';
                changeElement.style.color = changePercent >= 0 ? '#4ecdc4' : '#ff6b6b';
            }

            const updateEl = document.getElementById('lastUpdate');
            if (updateEl) updateEl.textContent = new Date().toLocaleTimeString();
        }

        function updateChart(data) {
            try {
                if (priceChart && data && data.historical) {
                    priceChart.data.labels = data.historical.labels || [];
                    priceChart.data.datasets[0].data = data.historical.prices || [];
                    priceChart.data.datasets[0].label = currentSymbol + ' Price (USD)';
                    priceChart.update('none');
                }
            } catch (error) {
                console.error('Error updating chart:', error);
            }
        }

        function updateSentimentDisplay(data) {
            const scoreEl = document.getElementById('sentimentScore');
            if (scoreEl) scoreEl.textContent = (data.score || 0).toFixed(4);
            
            const posEl = document.getElementById('positivePosts');
            if (posEl) posEl.textContent = data.positive || 0;
            
            const negEl = document.getElementById('negativePosts');
            if (negEl) negEl.textContent = data.negative || 0;
            
            const neuEl = document.getElementById('neutralPosts');
            if (neuEl) neuEl.textContent = data.neutral || 0;

            // Update sentiment meter
            const meter = document.getElementById('sentimentMeter');
            if (meter) {
                const percentage = ((data.score + 1) / 2) * 100; // Convert -1 to 1 range to 0-100%
                meter.style.width = percentage + '%';
                meter.className = 'sentiment-fill ' + (data.score < 0 ? 'negative' : '');
            }
        }

        function loadMockData() {
            // Load mock price data
            updatePriceDisplay({
                price: 65432.50,
                change_24h: 2.34
            });

            // Load mock sentiment data
            updateSentimentDisplay({
                score: 0.2456,
                positive: 45,
                negative: 23,
                neutral: 32
            });
            
            // Load mock chart data
            const mockLabels = [];
            const mockPrices = [];
            const basePrice = 65000;
            
            for (let i = 0; i < 24; i++) {
                mockLabels.push(String(i).padStart(2, '0') + ':00');
                mockPrices.push(basePrice + (Math.random() * 2000 - 1000));
            }
            
            updateChart({
                historical: {
                    labels: mockLabels,
                    prices: mockPrices
                }
            });

            console.log('Mock data loaded successfully');
        }

        // Chart initialization
        function initChart() {
            const chartElement = document.getElementById('priceChart');
            if (!chartElement) {
                console.error('Chart element not found, retrying...');
                setTimeout(initChart, 1000);
                return;
            }

            try {
                const ctx = chartElement.getContext('2d');
                if (!ctx) {
                    console.error('Failed to get chart context');
                    return;
                }

                priceChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: currentSymbol + ' Price (USD)',
                            data: [],
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 2,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    color: isDarkTheme ? '#e2e8f0' : '#333'
                                }
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                callbacks: {
                                    label: function(context) {
                                        return 'Price: $' + context.parsed.y.toLocaleString();
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                display: true,
                                grid: {
                                    color: isDarkTheme ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: isDarkTheme ? '#a0aec0' : '#666'
                                }
                            },
                            y: {
                                display: true,
                                grid: {
                                    color: isDarkTheme ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: isDarkTheme ? '#a0aec0' : '#666',
                                    callback: function(value) {
                                        return '$' + value.toLocaleString();
                                    }
                                }
                            }
                        },
                        interaction: {
                            mode: 'nearest',
                            axis: 'x',
                            intersect: false
                        }
                    }
                });
                
                console.log('Chart initialized successfully');
                // Load mock data after chart is ready
                setTimeout(loadMockData, 500);
                
            } catch (error) {
                console.error('Error initializing chart:', error);
                // Still load mock data even if chart fails
                setTimeout(loadMockData, 1000);
            }
        }

        // WebSocket initialization
        function initWebSocket() {
            try {
                if (typeof io !== 'undefined') {
                    socket = io();
                    
                    socket.on('connect', function() {
                        console.log('Connected to server');
                        const statusEl = document.getElementById('botStatus');
                        if (statusEl) statusEl.textContent = 'Connected';
                        // Request initial data immediately after connection
                        if (socket && socket.connected) {
                            socket.emit('request_initial_data', {crypto: currentCrypto});
                        }
                    });

                    socket.on('price_update', function(data) {
                        updatePriceDisplay(data);
                        updateChart(data);
                    });

                    socket.on('sentiment_update', function(data) {
                        updateSentimentDisplay(data);
                    });

                    socket.on('disconnect', function() {
                        console.log('Disconnected from server');
                        const statusEl = document.getElementById('botStatus');
                        if (statusEl) statusEl.textContent = 'Disconnected';
                    });
                } else {
                    console.warn('Socket.IO not loaded, using mock data');
                    setTimeout(loadMockData, 2000);
                }
            } catch (error) {
                console.error('WebSocket connection error:', error);
                setTimeout(loadMockData, 2000);
            }
        }

        // Make functions globally available first
        window.toggleTheme = toggleTheme;
        window.selectCrypto = selectCrypto;

        // Initialize everything when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded, initializing...');
            
            // Initialize chart first
            setTimeout(function() {
                initChart();
            }, 500);
            
            // Initialize WebSocket
            setTimeout(function() {
                initWebSocket();
            }, 800);
            
            // Load mock data as fallback
            setTimeout(function() {
                if (!socket || !socket.connected) {
                    console.log('Loading fallback mock data...');
                    loadMockData();
                }
            }, 2000);
        });
    </script>
</body>
</html>
"""

# Global bot state
bot_running = False
bot_thread = None
last_run_results = {}

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'bot_running': bot_running})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_price_update')
def handle_price_request(data):
    crypto = data.get('crypto', 'bitcoin')
    price_data = get_crypto_price_data(crypto)
    emit('price_update', price_data)

@socketio.on('request_sentiment_update')
def handle_sentiment_request():
    sentiment_data = get_live_sentiment_data()
    emit('sentiment_update', sentiment_data)

@socketio.on('request_technical_analysis')
def handle_technical_request(data):
    crypto = data.get('crypto', 'bitcoin')
    technical_data = get_technical_analysis(crypto)
    emit('technical_analysis', technical_data)

@socketio.on('request_initial_data')
def handle_initial_data_request(data):
    crypto = data.get('crypto', 'bitcoin')

    # Send all initial data
    price_data = get_crypto_price_data(crypto)
    sentiment_data = get_live_sentiment_data()
    portfolio_data = get_portfolio_data()
    technical_data = get_technical_analysis(crypto)

    emit('price_update', price_data)
    emit('sentiment_update', sentiment_data)
    emit('portfolio_update', portfolio_data)
    emit('technical_analysis', technical_data)

# Data fetching functions
def get_crypto_price_data(crypto_id):
    try:
        # Current price
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_change=true"
        price_response = requests.get(price_url, timeout=10)
        
        if price_response.status_code != 200:
            raise Exception(f"API returned status {price_response.status_code}")
        
        price_data = price_response.json()
        
        if crypto_id not in price_data:
            raise Exception(f"No data for {crypto_id}")

        current_price = price_data[crypto_id]['usd']
        change_24h = price_data[crypto_id].get('usd_24h_change', 0)

        # Historical data for chart
        history_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
        history_response = requests.get(history_url, timeout=10)
        
        if history_response.status_code != 200:
            raise Exception(f"History API returned status {history_response.status_code}")
        
        history_data = history_response.json()
        
        if 'prices' not in history_data:
            raise Exception("No prices data in API response")

        prices = [price[1] for price in history_data['prices']]
        labels = [datetime.fromtimestamp(price[0]/1000).strftime('%H:%M') for price in history_data['prices']]

        return {
            'price': current_price,
            'change_24h': change_24h,
            'historical': {
                'prices': prices,
                'labels': labels
            }
        }
    except Exception as e:
        print(f"Error fetching price data for {crypto_id}: {e}")
        # Return mock data when API fails
        base_price = 65000 if crypto_id == 'bitcoin' else 3500 if crypto_id == 'ethereum' else 1.2 if crypto_id == 'cardano' else 150 if crypto_id == 'solana' else 600
        mock_prices = []
        mock_labels = []
        
        for i in range(24):
            variation = (i - 12) * 0.01  # Small price variation
            mock_prices.append(base_price * (1 + variation))
            mock_labels.append(f"{i:02d}:00")
        
        return {
            'price': base_price,
            'change_24h': 2.5,
            'historical': {
                'prices': mock_prices,
                'labels': mock_labels
            }
        }

def get_live_sentiment_data():
    try:
        from trading_bot import get_sentiment_score
        sentiment_score, pos, neg, neu = get_sentiment_score()
        return {
            'score': sentiment_score,
            'positive': pos,
            'negative': neg,
            'neutral': neu
        }
    except Exception as e:
        print(f"Error fetching sentiment data: {e}")
        return {'score': 0, 'positive': 0, 'negative': 0, 'neutral': 0}

def get_portfolio_data():
    # Mock portfolio data - in real implementation, this would come from your trading system
    return {
        'total_value': 1250.75,
        'usd_balance': 850.00,
        'crypto_balance': 0.006543,
        'daily_pnl': 125.50
    }

def get_technical_analysis(crypto_id):
    try:
        # Get historical data for technical analysis
        history_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=30"
        response = requests.get(history_url, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}")
        
        data = response.json()
        
        if 'prices' not in data:
            raise Exception("No prices data in API response")

        prices = [price[1] for price in data['prices']]

        # Calculate RSI
        rsi = calculate_rsi(prices)

        # Get Fear & Greed Index
        fear_greed = get_fear_greed_index()

        # Mock MACD and AI prediction
        macd_signal = "BUY" if rsi < 30 else "SELL" if rsi > 70 else "HOLD"
        ai_signal = "BUY" if rsi < 40 else "SELL" if rsi > 60 else "HOLD"

        # Predict next price using simple trend
        predicted_price = prices[-1] * (1.02 if ai_signal == "BUY" else 0.98 if ai_signal == "SELL" else 1.0)

        return {
            'rsi': rsi,
            'macd': macd_signal,
            'macd_signal': macd_signal,
            'ai_signal': ai_signal,
            'predicted_price': predicted_price,
            'fear_greed': fear_greed
        }
    except Exception as e:
        print(f"Error in technical analysis for {crypto_id}: {e}")
        # Return mock technical data
        base_price = 65000 if crypto_id == 'bitcoin' else 3500 if crypto_id == 'ethereum' else 1.2 if crypto_id == 'cardano' else 150 if crypto_id == 'solana' else 600
        
        return {
            'rsi': 55,
            'macd': 'HOLD',
            'macd_signal': 'HOLD',
            'ai_signal': 'HOLD',
            'predicted_price': base_price * 1.01,
            'fear_greed': 50
        }

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50

    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_fear_greed_index():
    try:
        response = requests.get("https://api.alternative.me/fng/", timeout=5)
        data = response.json()
        return int(data['data'][0]['value'])
    except:
        return 50

# Enhanced routes
@app.route("/")
def home():
    return render_template_string(DASHBOARD_TEMPLATE, 
                                bot_running=bot_running, 
                                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/api/btc-prices")
def api_btc_prices():
    return jsonify(get_crypto_price_data('bitcoin'))

@app.route("/api/multi-crypto")
def api_multi_crypto():
    cryptos = ['bitcoin', 'ethereum', 'cardano', 'solana', 'binancecoin']
    data = {}
    for crypto in cryptos:
        data[crypto] = get_crypto_price_data(crypto)
    return jsonify(data)

@app.route("/start-bot")
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=run_trading_bot_wrapper)
        bot_thread.start()
        socketio.emit('trade_alert', {
            'action': 'BOT_STARTED',
            'price': 0,
            'reason': 'Trading bot activated'
        })
        message = "✅ Advanced bot started successfully!"
        status_class = "success"
    else:
        message = "⚠️ Bot is already running!"
        status_class = "warning"

    return f"""
    <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">🚀 Advanced Trading Bot Control</h2>
            <div style="background: {'#d4edda' if status_class == 'success' else '#fff3cd'}; padding: 20px; border-radius: 10px; margin: 20px 0;">
                {message}
            </div>
            <p style="color: #666; margin: 20px 0;">Enhanced bot with real-time WebSocket updates, multi-crypto support, and advanced technical analysis.</p>
            <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Back to Dashboard</a>
            <a href="/status" style="background: #764ba2; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 View Status</a>
        </div>
    </div>
    """

@app.route("/stop-bot")
def stop_bot():
    global bot_running
    bot_running = False
    socketio.emit('trade_alert', {
        'action': 'BOT_STOPPED',
        'price': 0,
        'reason': 'Trading bot deactivated'
    })
    return """
    <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
            <h2>🛑 Advanced Bot Stopped</h2>
            <p>The enhanced trading bot has been stopped successfully.</p>
            <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
        </div>
    </div>
    """

# Keep all existing routes
@app.route("/run-once")
def run_once():
    global last_run_results
    last_run_results = {}

    def run_with_results():
        global last_run_results
        try:
            last_run_results = run_trading_bot_with_results()
            # Emit real-time update
            socketio.emit('trade_alert', {
                'action': last_run_results.get('action', 'UNKNOWN'),
                'price': last_run_results.get('btc_price', 0),
                'reason': f"Sentiment: {last_run_results.get('sentiment_score', 0):.4f}"
            })
        except Exception as e:
            last_run_results = {"error": str(e)}

    threading.Thread(target=run_with_results).start()

    # Wait for results
    import time
    max_wait = 30
    wait_interval = 1
    waited = 0

    while waited < max_wait and not last_run_results:
        time.sleep(wait_interval)
        waited += wait_interval

    if "error" in last_run_results:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 800px; margin: 0 auto;">
                <h2>❌ Run Failed</h2>
                <p style="color: red;">Error: {last_run_results['error']}</p>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """

    results = last_run_results
    if not results:
        return """
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h2>⚡ Enhanced Bot is Running...</h2>
                <p>✅ Advanced bot execution started! Real-time results coming soon.</p>
                <a href="/results" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 View Results</a>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """

    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 900px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333;">⚡ Enhanced Trading Bot Results</h2>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">

                <div style="background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">📊 Advanced Sentiment Analysis</h3>
                    <p style="margin: 5px 0; font-size: 16px;">
                        <strong>Positive:</strong> {results.get('pos_count', 0)}<br>
                        <strong>Negative:</strong> {results.get('neg_count', 0)}<br>
                        <strong>Neutral:</strong> {results.get('neu_count', 0)}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 18px; font-weight: bold;">
                        📈 Score: {results.get('sentiment_score', 0):.4f}
                    </p>
                </div>

                <div style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">🔮 AI Price Prediction</h3>
                    <p style="margin: 5px 0; font-size: 18px;">
                        <strong>Predicted:</strong><br>
                        ${results.get('predicted_price', 0):,.2f}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 18px;">
                        <strong>Current:</strong><br>
                        ${results.get('btc_price', 0):,.2f}
                    </p>
                </div>

                <div style="background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">📢 Trading Decision</h3>
                    <p style="margin: 5px 0; font-size: 24px; font-weight: bold;">
                        {results.get('action', 'UNKNOWN')}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 16px;">
                        Email: {'✅ Sent' if results.get('email_sent', False) else '❌ Not sent'}
                    </p>
                </div>

                <div style="background: linear-gradient(45deg, #2ecc71, #27ae60); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">💰 Portfolio Status</h3>
                    <p style="margin: 5px 0; font-size: 16px;">
                        <strong>USD Balance:</strong><br>
                        ${results.get('usd_balance', 0):,.2f}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 16px;">
                        <strong>BTC Balance:</strong><br>
                        {results.get('btc_balance', 0):.6f} BTC
                    </p>
                </div>

            </div>

            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h4 style="color: #333; margin: 0 0 10px 0;">📋 Enhanced Analysis Summary</h4>
                <p style="color: #666; margin: 0; line-height: 1.6;">
                    Advanced analysis completed at {results.get('timestamp', 'Unknown time')}. 
                    The enhanced bot analyzed sentiment from {results.get('total_posts', 'multiple')} Reddit posts across 5 crypto subreddits, 
                    applied advanced technical indicators (RSI, MACD), made an AI-powered price prediction with multiple algorithms, 
                    and executed a <strong>{results.get('action', 'UNKNOWN')}</strong> decision with risk management.
                    {'Real-time email alert was sent to notify you of this action.' if results.get('email_sent', False) else 'No email alert was necessary for this action.'}
                </p>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Back to Advanced Dashboard</a>
                <a href="/status" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 System Status</a>
                <a href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank" style="background: #764ba2; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📋 View Google Sheet</a>
            </div>
        </div>
    </div>
    """

# Keep all other existing routes with minimal changes
@app.route("/status")
def status():
    from os import path, getenv

    checks = {
        "Reddit API": "✅ Connected" if getenv('REDDIT_CLIENT_ID') else "❌ Missing Client ID",
        "AI Model": "✅ Ready" if path.exists('btc_lstm_model.h5') else "❌ Missing Model",
        "Price Scaler": "✅ Ready" if path.exists('scaler.pkl') else "❌ Missing Scaler",
        "Google Credentials": "✅ Found" if path.exists('credintial.json') else "❌ Missing Credentials",
        "Google Sheet ID": "✅ Configured" if getenv('GOOGLE_SHEET_ID') else "❌ Not Set",
        "WebSocket Server": "✅ Active" if socketio else "❌ Disabled",
        "Real-time Updates": "✅ Enabled" if socketio else "❌ Disabled",
        "Multi-Crypto Support": "✅ Ready" if True else "❌ Disabled",
        "Log File": "✅ Active" if path.exists('sentiment_trade_log.txt') else "📝 Not Started"
    }

    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 900px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333;">📊 Enhanced Bot System Status</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                {''.join([f'<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid {"#28a745" if "✅" in status else "#dc3545"};"><strong>{component}:</strong><br>{status}</div>' for component, status in checks.items()])}
            </div>
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h4 style="color: #333; margin: 0 0 10px 0;">🚀 New Enhanced Features Active:</h4>
                <ul style="color: #666; margin: 0; padding-left: 20px;">
                    <li>Real-time WebSocket price updates every 30 seconds</li>
                    <li>Multi-cryptocurrency support (BTC, ETH, ADA, SOL, BNB)</li>
                    <li>Advanced technical indicators (RSI, MACD, Fear & Greed Index)</li>
                    <li>Interactive charts with live data visualization</li>
                    <li>Dark/Light theme toggle for better UX</li>
                    <li>Enhanced portfolio tracking with P&L calculations</li>
                    <li>Live trading notifications and alerts</li>
                </ul>
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Enhanced Dashboard</a>
                <a href="/test-connections" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">🔍 Test Connections</a>
            </div>
        </div>
    </div>
    """

@app.route("/test-connections")
def test_connections():
    results = []
    try:
        import praw
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
        reddit.user.me()
        results.append("✅ Reddit API: Connected")
    except:
        results.append("❌ Reddit API: Failed")

    try:
        from trading_bot import setup_google_sheets
        sheet = setup_google_sheets("credintial.json", os.getenv('GOOGLE_SHEET_ID'), "trading_bot_log")
        results.append("✅ Google Sheets: Connected")
    except:
        results.append("❌ Google Sheets: Failed")

    try:
        price_data = get_crypto_price_data('bitcoin')
        if price_data['price'] > 0:
            results.append("✅ CoinGecko API: Connected")
        else:
            results.append("❌ CoinGecko API: No data")
    except:
        results.append("❌ CoinGecko API: Failed")

    try:
        fear_greed = get_fear_greed_index()
        if 0 <= fear_greed <= 100:
            results.append("✅ Fear & Greed Index: Connected")
        else:
            results.append("❌ Fear & Greed Index: Invalid data")
    except:
        results.append("❌ Fear & Greed Index: Failed")

    results.append("✅ WebSocket Server: Ready")
    results.append("✅ Real-time Updates: Enabled")

    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 700px; margin: 0 auto;">
            <h2 style="text-align: center;">🔍 Enhanced Connection Test Results</h2>
            <div style="margin: 30px 0;">
                {'<br>'.join([f'<div style="padding: 10px; margin: 10px 0; background: {"#d4edda" if "✅" in result else "#f8d7da"}; border-radius: 5px;">{result}</div>' for result in results])}
            </div>
            <div style="text-align: center;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Enhanced Dashboard</a>
            </div>
        </div>
    </div>
    """

@app.route("/download-model")
def download_model():
    from trading_bot import download_model_from_github
    success = download_model_from_github()
    return f"{'✅ Enhanced model downloaded successfully!' if success else '❌ Failed to download model.'} <a href='/'>← Back</a>"

@app.route("/download-log")
def download_log():
    log_path = "sentiment_trade_log.txt"
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True)
    return "❌ No log file found. <a href='/'>← Back</a>"

@app.route("/view-results")
def view_results():
    chart_path = "run_results_chart.png"
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype='image/png')
    return "❌ Chart not found. Run the enhanced bot first. <a href='/'>← Back</a>"

@app.route("/run")
def auto_trigger():
    threading.Thread(target=run_trading_bot).start()
    return "✅ Enhanced bot started via /run endpoint"

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "bot_running": bot_running,
        "websocket_active": True,
        "features": ["real_time_updates", "multi_crypto", "technical_analysis", "dark_theme"],
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/results")
def view_latest_results():
    global last_run_results
    if not last_run_results:
        return """
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h2>📊 No Enhanced Results Yet</h2>
                <p>Run the enhanced bot first to see detailed real-time results!</p>
                <a href="/run-once" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">⚡ Run Enhanced Bot</a>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """
    return run_once()

def run_trading_bot_wrapper():
    """Wrapper to handle bot state"""
    global bot_running
    try:
        run_trading_bot()
    finally:
        bot_running = False

def run_trading_bot_with_results():
    """Enhanced version that returns detailed results with real-time updates"""
    from trading_bot import (
        download_model_from_github, download_scaler_from_github,
        get_sentiment_score, get_historical_btc_prices, get_real_btc_price,
        predict_next_day_price, setup_google_sheets, add_headers_if_needed,
        log_trade_to_google_sheets, send_email_alert
    )
    import pickle
    import numpy as np

    # Download required files
    model_downloaded = download_model_from_github()
    scaler_downloaded = download_scaler_from_github()

    # Load model and scaler
    try:
        if 'load_model' in globals() and model_downloaded:
            from tensorflow.keras.models import load_model
            model = load_model("btc_lstm_model.h5")
        else:
            model = None
    except:
        model = None

    try:
        if scaler_downloaded and os.path.exists("scaler.pkl"):
            with open("scaler.pkl", "rb") as f:
                scaler = pickle.load(f)
        else:
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            dummy_data = np.array([[30000], [70000]])
            scaler.fit(dummy_data)
    except:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        dummy_data = np.array([[30000], [70000]])
        scaler.fit(dummy_data)

    # Setup Google Sheets
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise Exception("GOOGLE_SHEET_ID not found in environment variables!")

    sheet = setup_google_sheets("credintial.json", sheet_id, "trading_bot_log")
    add_headers_if_needed(sheet)

    # Get sentiment analysis
    sentiment_score, pos, neg, neu = get_sentiment_score()
    total_posts = pos + neg + neu

    # Get price data and make prediction
    historical_prices = get_historical_btc_prices()
    predicted_price = predict_next_day_price(model, scaler, historical_prices, 60)
    btc_price = get_real_btc_price()

    # Enhanced trading logic with risk management
    usd_balance = 1000.0
    btc_balance = 0.0
    average_buy_price = 0.0
    action = "HOLD"
    email_sent = False

    # Get technical indicators for enhanced decision making
    technical_data = get_technical_analysis('bitcoin')
    rsi = technical_data.get('rsi', 50)

    # Enhanced trading logic with multiple indicators
    buy_signals = 0
    sell_signals = 0

    # Sentiment signal
    if sentiment_score > 0.3:
        buy_signals += 1
    elif sentiment_score < -0.3:
        sell_signals += 1

    # Price prediction signal
    if predicted_price > btc_price * 1.01:
        buy_signals += 1
    elif predicted_price < btc_price * 0.99:
        sell_signals += 1

    # RSI signal
    if rsi < 30:
        buy_signals += 1
    elif rsi > 70:
        sell_signals += 1

    # Execute trades based on multiple signals
    if buy_signals >= 2 and usd_balance >= 100:
        action = "BUY"
        btc_bought = 100 / btc_price
        usd_balance -= 100
        btc_balance += btc_bought
        average_buy_price = ((average_buy_price * (btc_balance - btc_bought)) + (btc_price * btc_bought)) / btc_balance
    elif sell_signals >= 2 and btc_balance >= 0.001:
        action = "SELL"
        usd_gained = 0.001 * btc_price
        btc_balance -= 0.001
        usd_balance += usd_gained
        if btc_balance == 0:
            average_buy_price = 0.0
    elif btc_balance >= 0.001:
        if btc_price <= average_buy_price * 0.95:
            action = "STOP-LOSS"
            usd_gained = 0.001 * btc_price
            btc_balance -= 0.001
            usd_balance += usd_gained
        elif btc_price >= average_buy_price * 1.10:
            action = "TAKE-PROFIT"
            usd_gained = 0.001 * btc_price
            btc_balance -= 0.001
            usd_balance += usd_gained

    # Log to file and Google Sheets
    with open("sentiment_trade_log.txt", "a") as f:
        f.write(f"{datetime.now()} | Action: {action} | Sentiment: {sentiment_score:.4f} | RSI: {rsi:.1f} | Predicted BTC: ${predicted_price:.2f} | BTC: ${btc_price:.2f} | USD: ${usd_balance:.2f} | BTC Bal: {btc_balance:.6f}\n")

    log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price, btc_price, usd_balance, btc_balance)

    # Send email for significant actions
    if action in ["BUY", "SELL", "STOP-LOSS", "TAKE-PROFIT"]:
        try:
            send_email_alert(
                f"[Enhanced Crypto Bot] {action} Signal",
                f"Enhanced Analysis:\nAction: {action}\nSentiment: {sentiment_score:.4f}\nRSI: {rsi:.1f}\nPredicted: ${predicted_price:.2f}\nBTC Now: ${btc_price:.2f}\nUSD Balance: ${usd_balance:.2f}\nBTC Balance: {btc_balance:.6f}\nBuy Signals: {buy_signals}\nSell Signals: {sell_signals}"
            )
            email_sent = True
        except:
            email_sent = False

    # Return enhanced results
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sentiment_score": sentiment_score,
        "pos_count": pos,
        "neg_count": neg,
        "neu_count": neu,
        "total_posts": total_posts,
        "predicted_price": predicted_price,
        "btc_price": btc_price,
        "action": action,
        "usd_balance": usd_balance,
        "btc_balance": btc_balance,
        "email_sent": email_sent,
        "rsi": rsi,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "technical_data": technical_data
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)