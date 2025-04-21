document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('spam-detection-form');
    const resultDiv = document.getElementById('result');
    const predictionText = document.getElementById('prediction-text');
    const confidenceBar = document.getElementById('confidence-bar');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Update UI with results
            resultDiv.style.display = 'block';
            
            // Set prediction text
            let predictionMessage = data.prediction;
            if (data.spam_indicators) {
                predictionMessage += '<br><small class="text-muted">Spam indicators: ' + 
                    data.spam_indicators.join(', ') + '</small>';
            }
            predictionText.innerHTML = predictionMessage;
            
            // Update confidence bar
            confidenceBar.style.width = `${data.confidence}%`;
            confidenceBar.textContent = `${data.confidence}%`;
            
            // Set appropriate alert class based on prediction
            const alertDiv = resultDiv.querySelector('.alert');
            alertDiv.className = 'alert ' + 
                (data.is_spam ? 'alert-danger' : 'alert-success');
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the email.');
        }
    });
}); 