document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('question-form');
    const questions = document.querySelectorAll('.question');
    let currentQuestion = 0;

    function showQuestion(index) {
        questions.forEach((question, i) => {
            question.style.display = i === index ? 'block' : 'none';
        });
    
        // Focus the first input or select element in the current question
        const currentInputs = questions[index].querySelectorAll('input, select');
        if (currentInputs.length > 0) {
            currentInputs[0].focus();
        }
    }

    function showNextQuestion() {
        const inputs = questions[currentQuestion].querySelectorAll('input, select');
        let allValid = true;

        inputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                allValid = false;
            }
        });

        if (allValid) {
            currentQuestion++;
            if (currentQuestion < questions.length) {
                showQuestion(currentQuestion);
            } else {
                form.submit();
            }
        }
    }

    function showPreviousQuestion() {
        if (currentQuestion > 0) {
            currentQuestion--;
            showQuestion(currentQuestion);
        }
    }

    showQuestion(currentQuestion);

    document.getElementById('next-button').addEventListener('click', function (event) {
        event.preventDefault();
        showNextQuestion();
    });

    document.getElementById('back-button').addEventListener('click', function (event) {
        event.preventDefault();
        showPreviousQuestion();
    });

    // Listen for Enter key press to move to the next question
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default form submission
            showNextQuestion(); // Move to the next question
        }
    });

});