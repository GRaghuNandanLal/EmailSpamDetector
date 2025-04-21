from flask import Blueprint, render_template, request, jsonify
from app.models.spam_detector import SpamDetector
from app.models.detection_history import db, DetectionHistory
from datetime import datetime, timedelta
from collections import Counter
import re
from sqlalchemy import func

# Create Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@main.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text for spam and save to history"""
    content = request.form.get('content', '')
    
    if not content:
        return jsonify({'error': 'No content provided'}), 400
    
    try:
        # Get spam detector instance
        detector = SpamDetector()
        
        # Get prediction
        result = detector.predict(content)
        
        # Save to history
        history_entry = DetectionHistory(
            text=content,
            prediction=result['prediction'],
            confidence=result['confidence'],
            is_spam=result['is_spam']
        )
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/history')
def history():
    """Show detection history"""
    # Get all history entries, ordered by date (newest first)
    entries = DetectionHistory.query.order_by(DetectionHistory.date.desc()).all()
    return render_template('history.html', history=entries)

@main.route('/dashboard')
def dashboard():
    """Show analytics dashboard"""
    # Get all detection history
    entries = DetectionHistory.query.all()
    
    # Calculate spam/ham statistics
    total = len(entries)
    spam_count = sum(1 for entry in entries if entry.is_spam)
    ham_count = total - spam_count
    
    stats = {
        'total': total,
        'spam': spam_count,
        'ham': ham_count,
        'spam_percentage': round((spam_count / total * 100) if total > 0 else 0, 2),
        'ham_percentage': round((ham_count / total * 100) if total > 0 else 0, 2)
    }
    
    # Calculate detection trends (last 5 months)
    today = datetime.utcnow()
    months = []
    trend_data = []
    
    for i in range(4, -1, -1):  # Last 5 months
        start_date = (today - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Query for this month's data
        month_entries = DetectionHistory.query.filter(
            DetectionHistory.date.between(start_date, end_date)
        ).all()
        
        month_total = len(month_entries)
        month_spam = sum(1 for e in month_entries if e.is_spam)
        
        # Calculate spam percentage
        spam_percentage = round((month_spam / month_total * 100) if month_total > 0 else 0, 2)
        
        months.append(start_date.strftime('%b'))  # Month abbreviation
        trend_data.append(spam_percentage)
    
    # Extract common spam words
    spam_entries = [entry.text.lower() for entry in entries if entry.is_spam]
    words = []
    for text in spam_entries:
        words.extend(re.findall(r'\b\w+\b', text))
    
    # Count word frequencies
    word_counter = Counter(words)
    
    # Filter out common English words and get top 10 spam words
    common_words = set(['the', 'and', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'for'])
    spam_words = [(word, count) for word, count in word_counter.most_common(20)
                  if word not in common_words and len(word) > 2][:10]
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         spam_words=spam_words,
                         trend_months=months,
                         trend_data=trend_data) 