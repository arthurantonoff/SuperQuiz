document.addEventListener("DOMContentLoaded", function () {
    const SUPABASE_URL = "https://jszlastvwxefajjuquxt.supabase.co";
    const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impzemxhc3R2d3hlZmFqanVxdXh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1ODMwODUsImV4cCI6MjA2NTE1OTA4NX0.onXBoSa9j6EeVBZxWncZ5uAGDIONHJQBajAzzgzCz18";
    const LIMITE_QUESTOES = 20;

    const etapas = {
        qr: document.getElementById("qr-section"),
        tema: document.getElementById("tema-section"),
        quiz: document.getElementById("quiz-section"),
        resultado: document.getElementById("result-section")
    };

    function mostrarEtapa(nome) {
        Object.values(etapas).forEach(sec => sec.style.display = "none");
        etapas[nome].style.display = "block";
    }

    const pagarButton = document.getElementById("pagar-button");
    pagarButton.addEventListener("click", () => {
        localStorage.setItem("acesso-liberado", "true");
        mostrarEtapa("tema");
        carregarTítulos();
    });

    const tituloSelector = document.getElementById("titulo-selector");
    const iniciarQuizButton = document.getElementById("start-quiz");

    let quizzesPorTitulo = {}; // agrupamento por titulo
    let quizzesSelecionados = [];
    let perguntasAtuais = [];
    let currentIndex = 0;
    let score = 0;
    let respostas = [];

    async function carregarTítulos() {
        try {
            const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=id,titulo,perguntas&ativo=eq.true`, {
                headers: {
                    apikey: SUPABASE_ANON_KEY,
                    Authorization: `Bearer ${SUPABASE_ANON_KEY}`
                }
            });
            const quizzes = await res.json();

            quizzesPorTitulo = quizzes.reduce((acc, quiz) => {
                if (!acc[quiz.titulo]) acc[quiz.titulo] = [];
                acc[quiz.titulo].push(quiz);
                return acc;
            }, {});

            tituloSelector.innerHTML = "<option value='' disabled selected>Escolha um tema</option>";
            Object.keys(quizzesPorTitulo).forEach(titulo => {
                const option = document.createElement("option");
                option.value = titulo;
                option.textContent = titulo;
                tituloSelector.appendChild(option);
            });
        } catch (e) {
            alert("Erro ao carregar temas.");
        }
    }

    iniciarQuizButton.addEventListener("click", () => {
        const titulo = tituloSelector.value;
        if (!titulo || !quizzesPorTitulo[titulo]) return;

        quizzesSelecionados = quizzesPorTitulo[titulo];
        perguntasAtuais = shuffleArray(quizzesSelecionados.flatMap(q => q.perguntas)).slice(0, LIMITE_QUESTOES);

        score = 0;
        currentIndex = 0;
        respostas = [];

        mostrarEtapa("quiz");
        exibirPergunta();
    });

    function exibirPergunta() {
        const quizContainer = document.getElementById("quiz");
        quizContainer.innerHTML = "";

        if (currentIndex >= perguntasAtuais.length) {
            mostrarResultado();
            return;
        }

        const atual = perguntasAtuais[currentIndex];

        const h2 = document.createElement("h2");
        h2.textContent = atual.question;
        quizContainer.appendChild(h2);

        atual.options.forEach((op, i) => {
            const btn = document.createElement("button");
            btn.textContent = op;
            btn.className = "option";
            btn.onclick = () => {
                respostas.push({ pergunta: atual.question, correta: atual.answer, marcada: i });
                if (i === atual.answer) score++;
                currentIndex++;
                exibirPergunta();
            };
            quizContainer.appendChild(btn);
        });
    }

    function mostrarResultado() {
        mostrarEtapa("resultado");
        const resultContainer = document.getElementById("result");
        resultContainer.innerHTML = `<h2>Você acertou ${score} de ${perguntasAtuais.length} perguntas.</h2>`;
    }

    function shuffleArray(arr) {
        return arr.sort(() => Math.random() - 0.5);
    }

    // Inicialização
    if (localStorage.getItem("acesso-liberado") === "true") {
        mostrarEtapa("tema");
        carregarTítulos();
    } else {
        mostrarEtapa("qr");
    }
});
