// script.js
function selectOption(selectedValue, nextQuestionId) {
    // Optionally, you can store the selectedValue if needed

    const currentQuestion = document.querySelector('.question:not(.hidden)');
    const nextQuestion = document.getElementById(nextQuestionId);

    if (currentQuestion && nextQuestion) {
        currentQuestion.classList.add('hidden');
        nextQuestion.classList.remove('hidden');
    }
}