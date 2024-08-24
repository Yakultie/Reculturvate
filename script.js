// script.js
function showNextQuestion(nextQuestionId) {
    const currentQuestion = document.querySelector('.question:not(.hidden)');
    const nextQuestion = document.getElementById(nextQuestionId);

    if (currentQuestion) {
        currentQuestion.classList.add('hidden');
    }

    if (nextQuestion) {
        nextQuestion.classList.remove('hidden');

        const questionText = nextQuestion.querySelector('.question-text');
        const textContent = questionText.textContent;
        questionText.innerHTML = '';

        textContent.split('').forEach((char, index) => {
            const span = document.createElement('span');
            span.textContent = char;
            span.style.setProperty('--char-index', index);
            questionText.appendChild(span);
        });
    }
}