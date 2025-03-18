document.addEventListener("DOMContentLoaded", function () {
    let currentQuestionIndex = 0;
    let score = 0;
    let startTime;
    let timerInterval;
    let selectedTheme = "Quiz Interativo"; 
    let userAnswers = [];
    let questions = {};

    const modal = document.getElementById("theme-selection");
    const themeSelector = document.getElementById("theme-selector");
    const startQuizButton = document.getElementById("start-quiz");
    const container = document.querySelector(".container");
    const title = document.querySelector("h1");
    const quizContainer = document.getElementById("quiz");
    const timerDisplay = document.getElementById("time-counter");
    const restartButton = document.getElementById("restart");
    const resultContainer = document.getElementById("result");
    const viewReportButton = document.getElementById("view-report");
    const reportContainer = document.getElementById("report-container");

    let currentQuestions = [];

    // Função para carregar o JSON externo
    async function loadQuestions() {
        try {
            const response = await fetch('https://raw.githubusercontent.com/arthurantonoff/SuperQuiz/main/questions.json');
            if (!response.ok) {
                throw new Error('Erro ao carregar o arquivo JSON');
            }
            questions = await response.json();
        } catch (error) {
            console.error('Erro:', error);
        }
    }

    startQuizButton.addEventListener("click", function () {
        selectedTheme = themeSelector.value;
        title.textContent = selectedTheme.charAt(0).toUpperCase() + selectedTheme.slice(1);
        modal.style.display = "none";
        container.style.display = "block";
        startQuiz();
    });

    async function startQuiz() {
        await loadQuestions();
        currentQuestions = questions[selectedTheme];
        currentQuestionIndex = 0;
        score = 0;
        userAnswers = [];
        startTime = new Date().getTime();
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);

        restartButton.style.display = "none";
        viewReportButton.style.display = "none";
        reportContainer.style.display = "none";
        resultContainer.innerHTML = "";
        
        showQuestion();
    }

    function updateTimer() {
        let elapsedTime = Math.floor((new Date().getTime() - startTime) / 1000);
        timerDisplay.textContent = elapsedTime;
    }

    function showQuestion() {
        if (currentQuestionIndex >= currentQuestions.length) {
            endQuiz();
            return;
        }

        const questionData = currentQuestions[currentQuestionIndex];
        quizContainer.innerHTML = `<h2>${questionData.question}</h2>`;

        questionData.options.forEach((option, index) => {
            const button = document.createElement("button");
            button.classList.add("option");
            button.textContent = option;
            button.addEventListener("click", function () {
                checkAnswer(index);
            });
            quizContainer.appendChild(button);
        });
    }

    function checkAnswer(selectedIndex) {
        userAnswers.push({
            question: currentQuestions[currentQuestionIndex].question,
            options: currentQuestions[currentQuestionIndex].options,
            correctAnswer: currentQuestions[currentQuestionIndex].answer,
            userAnswer: selectedIndex
        });

        if (selectedIndex === currentQuestions[currentQuestionIndex].answer) {
            score++;
        }
        currentQuestionIndex++;
        showQuestion();
    }

    function endQuiz() {
        clearInterval(timerInterval);
        quizContainer.innerHTML = "";
        resultContainer.innerHTML = `<h2>Resultado Final</h2>
                                     <p>Pontuação: ${score} / ${currentQuestions.length}</p>
                                     <p>Tempo total: ${timerDisplay.textContent} segundos</p>`;

        restartButton.style.display = "block";
        viewReportButton.style.display = "block";
    }

    restartButton.addEventListener("click", function () {
        container.style.display = "none";
        modal.style.display = "flex";
        modal.style.justifyContent = "center";
        modal.style.alignItems = "center";
        restartButton.style.display = "none";
        viewReportButton.style.display = "none";
        resultContainer.innerHTML = "";
    });

    viewReportButton.addEventListener("click", function () {
        if (reportContainer.style.display === "none") {
            reportContainer.style.display = "block";
            generateReport();
        } else {
            reportContainer.style.display = "none";
        }
    });

    function generateReport() {
        reportContainer.innerHTML = "<h2>Relatório</h2>";
        userAnswers.forEach((entry, index) => {
            const questionBlock = document.createElement("div");
            questionBlock.classList.add("report-item");

            const isCorrect = entry.userAnswer === entry.correctAnswer;
            const marker = isCorrect ? "✅" : "❌";

            questionBlock.innerHTML = `
                <p><strong>${marker} Pergunta ${index + 1}:</strong> ${entry.question}</p>
                <p><strong>Sua Resposta:</strong> ${entry.options[entry.userAnswer]}</p>
                <hr>
            `;
            reportContainer.appendChild(questionBlock);
        });
    }
});
