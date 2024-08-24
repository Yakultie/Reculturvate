// script.js
function showNextQuestion(nextQuestionId) {
    const currentQuestion = document.querySelector('.question.visible');
    const nextQuestion = document.getElementById(nextQuestionId);
    
    if (currentQuestion) {
        // Start by hiding the current question
        currentQuestion.classList.remove('visible'); 
        currentQuestion.classList.add('hidden'); // Move to hidden state after visibility is removed

        // Wait for the hide transition to complete
        setTimeout(() => {
            // Remove hidden state from the next question
            nextQuestion.classList.remove('hidden');
            // Trigger the animation by adding visible class
            setTimeout(() => {
                nextQuestion.classList.add('visible');
            }, 10); // Delay for the next animation
        }, 300); // Wait for the fade-out transition to complete
    } else if (nextQuestion) {
        // If no current question, simply show the next question
        nextQuestion.classList.remove('hidden');
        setTimeout(() => {
            nextQuestion.classList.add('visible');
        }, 10);
    }
}

function selectOption(selectedValue, nextQuestionId) {
    const currentQuestion = document.querySelector('.question.visible');
    const nextQuestion = document.getElementById(nextQuestionId);

    if (currentQuestion && nextQuestion) {
        currentQuestion.classList.remove('visible');
        currentQuestion.classList.add('hidden');
        nextQuestion.classList.remove('hidden');
        setTimeout(() => {
            nextQuestion.classList.add('visible');
        }, 10);
    }
}