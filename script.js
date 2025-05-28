document.addEventListener("DOMContentLoaded", function () {
    let currentQuestionIndex = 0;
    let score = 0;
    let startTime;
    let timerInterval;
    let selectedTheme = "";  
    let userAnswers = [];
    let questions = {}; // Agora só carrega do JSON externo

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

    // Função para carregar as perguntas do JSON externo
    function loadExternalQuestions() {
        fetch("https://raw.githubusercontent.com/arthurantonoff/SuperQuiz/main/questions-arthur.json")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro ao carregar perguntas.");
                }
                return response.json();
            })
            .then(data => {
                questions = data;
                populateThemes(); // Atualiza os temas dinamicamente
            })
            .catch(error => {
                console.error("Erro ao carregar questões externas:", error);
                alert("Não foi possível carregar as perguntas. Tente novamente mais tarde.");
            });
    }

    // Preenche o seletor de temas dinamicamente
    function populateThemes() {
        themeSelector.innerHTML = ""; // Limpa o seletor antes de preencher

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

    // Converte nomes de temas para um formato mais legível
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
    fetch("https://raw.githubusercontent.com/arthurantonoff/SuperQuiz/main/questions.json")
        .then(response => response.json())
        .then(data => {
            if (data[selectedTheme]) {
                const allQuestions = data[selectedTheme];
                currentQuestions = shuffleArray(allQuestions).slice(10, 50); // Seleciona 25 questões aleatórias

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
            } else {
                console.error("Tema não encontrado no JSON");
            }
        })
        .catch(error => console.error("Erro ao carregar as questões:", error));
}

// Função para embaralhar as questões
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

    // Aplica a classe para transição antes de trocar o conteúdo
    quizContainer.classList.add("hidden");

    setTimeout(() => {
        quizContainer.innerHTML = `<h2>${questionData.question}</h2>`;

        questionData.options.forEach((option, index) => {
            const button = document.createElement("button");
            button.classList.add("option");
            button.textContent = option;

            button.addEventListener("click", function () {
                // Efeito de clique antes da transição
                button.classList.add("selected");
                setTimeout(() => {
                    checkAnswer(index);
                }, 200); // Pequeno atraso para a transição ser perceptível
            });

            quizContainer.appendChild(button);
        });

        // Remove a classe para exibir a questão suavemente
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

    // Carrega as perguntas externas ao iniciar
    loadExternalQuestions();
});
