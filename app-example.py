#!/usr/bin/env python3
# backend/app.py - Backend Flask adaptado para Fly.io

import os
import psycopg2
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Variables de entorno inyectadas por Fly.io
DB_HOST = os.getenv('DATABASE_URL_HOST', 'localhost')
DB_PORT = os.getenv('DATABASE_URL_PORT', 5432)
DB_NAME = os.getenv('DATABASE_URL_NAME', 'tallerdb')
DB_USER = os.getenv('DATABASE_URL_USER', 'talleruser')
DB_PASSWORD = os.getenv('DATABASE_URL_PASSWORD', 'tallerpass')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "backend-flask",
        "timestamp": datetime.now().isoformat(),
        "environment": FLASK_ENV
    }), 200

@app.route('/health')
def health():
    """Endpoint para Fly.io health checks"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/info')
def info():
    """API endpoint con información de los servicios"""
    try:
        # Intentar conectar a PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        db_status = "conectada"
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "base_datos": db_status,
        "estado": "activo",
        "puerto": 5000,
        "servicio": "backend-flask",
        "tecnologia": "Python 3.11 + Flask"
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # En desarrollo: modo debug
    # En producción: FLASK_ENV=production desactiva debug
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(FLASK_ENV == 'development')
    )
