document.addEventListener("DOMContentLoaded", function () {
    let nquestions = 20;
    let currentQuestionIndex = 0;
    let score = 0;
    let startTime;
    let timerInterval;
    let selectedTheme = "";  
    let userAnswers = [];
    let questions = {}; // Agora carrega do Supabase

    const SUPABASE_URL = "__SUPABASE_URL__";
    const SUPABASE_ANON_KEY = "__SUPABASE_ANON_KEY__";

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

    async function loadQuizzesFromSupabase() {
        try {
            const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=id,titulo,perguntas&ativo=eq.true`, {
                headers: {
                    apikey: SUPABASE_ANON_KEY,
                    Authorization: `Bearer ${SUPABASE_ANON_KEY}`
                }
            });
            const data = await res.json();
            data.forEach(quiz => {
                questions[quiz.id] = quiz.perguntas;
            });
            populateThemes();
        } catch (error) {
            console.error("Erro ao carregar quizzes do Supabase:", error);
            alert("Não foi possível carregar os temas. Tente novamente mais tarde.");
        }
    }

    function populateThemes() {
        themeSelector.innerHTML = "";
        if (Object.keys(questions).length === 0) {
            let option = document.createElement("option");
            option.value = "";
            option.textContent = "Nenhum tema disponível";
            option.disabled = true;
            option.selected = true;
            themeSelector.appendChild(option);
            return;
        }
        Object.keys(questions).forEach(theme => {
            let option = document.createElement("option");
            option.value = theme;
            option.textContent = formatThemeName(theme);
            themeSelector.appendChild(option);
        });
    }

    function formatThemeName(theme) {
        return theme.replace(/\d+/, '').replace(/_/g, ' ').trim().toUpperCase();
    }

    startQuizButton.addEventListener("click", function () {
        selectedTheme = themeSelector.value;
        if (!questions[selectedTheme]) {
            alert("Tema não encontrado. Tente outro.");
            return;
        }
        title.textContent = formatThemeName(selectedTheme);
        modal.style.display = "none";
        container.style.display = "block";
        startQuiz();
    });

    function startQuiz() {
        const allQuestions = questions[selectedTheme];
        currentQuestions = shuffleArray(allQuestions).slice(0, nquestions);

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

    function shuffleArray(array) {
        return array.sort(() => Math.random() - 0.5);
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
        quizContainer.classList.add("hidden");

        setTimeout(() => {
            quizContainer.innerHTML = `<h2>${questionData.question}</h2>`;
            questionData.options.forEach((option, index) => {
                const button = document.createElement("button");
                button.classList.add("option");
                button.textContent = option;
                button.addEventListener("click", function () {
                    button.classList.add("selected");
                    setTimeout(() => {
                        checkAnswer(index);
                    }, 200);
                });
                quizContainer.appendChild(button);
            });
            setTimeout(() => {
                quizContainer.classList.remove("hidden");
            }, 100);
        }, 200);
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

    loadQuizzesFromSupabase();
});
