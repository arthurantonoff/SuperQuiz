const quizData = [
    { question: "Qual é a capital do Brasil?", options: ["Rio de Janeiro", "Brasília", "São Paulo", "Belo Horizonte"], correct: "Brasília" },
    { question: "Quem descobriu o Brasil?", options: ["Pedro Álvares Cabral", "Cristóvão Colombo", "Vasco da Gama", "Dom Pedro I"], correct: "Pedro Álvares Cabral" },
    { question: "Qual é o maior planeta do sistema solar?", options: ["Terra", "Júpiter", "Marte", "Saturno"], correct: "Júpiter" }
];

const quizContainer = document.getElementById("quiz");
const submitButton = document.getElementById("submit");
const resultText = document.getElementById("result");
const progressBar = document.getElementById("progress-bar");

function loadQuiz() {
    quizContainer.innerHTML = "";
    let questionCount = 0;

    quizData.forEach((q, index) => {
        questionCount++;
        const questionBlock = document.createElement("div");
        questionBlock.classList.add("question-block");

        const questionTitle = document.createElement("h3");
        questionTitle.textContent = `${index + 1}. ${q.question}`;
        questionBlock.appendChild(questionTitle);

        q.options.forEach(option => {
            const label = document.createElement("label");
            const input = document.createElement("input");
            input.type = "radio";
            input.name = `question${index}`;
            input.value = option;
            label.appendChild(input);
            label.appendChild(document.createTextNode(option));
            questionBlock.appendChild(label);
        });

        quizContainer.appendChild(questionBlock);
    });
}

submitButton.addEventListener("click", () => {
    progressBar.style.width = "100%";
    alert("Processando resultados...");
});

loadQuiz();
