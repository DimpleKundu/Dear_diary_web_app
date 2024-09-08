document.addEventListener('DOMContentLoaded', function() {
    const click_to_convert = document.getElementById('click_to_convert');
    const convert_text = document.getElementById('raw_text'); // Changed to 'raw_text' as per your HTML
    
    if (click_to_convert) {
        click_to_convert.addEventListener('click', function() {
            var speech = true;
            window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();

            recognition.interimResults = true;

            recognition.addEventListener('result', e => { 
                const transcript = Array.from(e.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');

                convert_text.value = transcript; // Changed to 'value' to set the textarea value
            });

            if (speech == true) {
                recognition.start();
            }
        });
    }
});
