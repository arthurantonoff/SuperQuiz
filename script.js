document.addEventListener("DOMContentLoaded", function () {
    let currentQuestionIndex = 0;
    let score = 0;
    let startTime;
    let timerInterval;
    let selectedTheme = "Quiz Interativo"; 
    let userAnswers = [];

    const questions = {
        geral: [
            { question: "Qual é a capital do Brasil?", options: ["Rio de Janeiro", "Brasília", "São Paulo", "Salvador"], answer: 1 },
            { question: "Quanto é 2 + 2?", options: ["3", "4", "5", "6"], answer: 1 }
        ],
        ciencia: [
            { question: "Qual o símbolo químico da água?", options: ["H2O", "O2", "CO2", "NaCl"], answer: 0 },
            { question: "Quem formulou a teoria da relatividade?", options: ["Newton", "Einstein", "Tesla", "Galileu"], answer: 1 }
        ],
        historia: [
            { question: "Em que ano o Brasil foi descoberto?", options: ["1492", "1500", "1822", "1889"], answer: 1 },
            { question: "Quem foi o primeiro presidente do Brasil?", options: ["Juscelino Kubitschek", "Getúlio Vargas", "Deodoro da Fonseca", "Dom Pedro II"], answer: 2 }
        ]
    };

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

    startQuizButton.addEventListener("click", function () {
        selectedTheme = themeSelector.value;
        title.textContent = selectedTheme.charAt(0).toUpperCase() + selectedTheme.slice(1);
        modal.style.display = "none";
        container.style.display = "block";
        startQuiz();
    });

    function startQuiz() {
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
        modal.style.display = "flex"; // ✅ Agora o modal volta visível e centralizado
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
