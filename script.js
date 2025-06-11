document.addEventListener("DOMContentLoaded", function () {
    const SUPABASE_URL = "https://jszlastvwxefajjuquxt.supabase.co";
    const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impzemxhc3R2d3hlZmFqanVxdXh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1ODMwODUsImV4cCI6MjA2NTE1OTA4NX0.onXBoSa9j6EeVBZxWncZ5uAGDIONHJQBajAzzgzCz18";
    const LIMITE_QUESTOES = 20;

    const tituloSelector = document.getElementById("titulo-selector");
    const subtemaSelector = document.getElementById("subtema-selector");
    const carregarSubtemasBtn = document.getElementById("carregar-subtemas");
    const iniciarQuizButton = document.getElementById("start-quiz");

    let quizzes = [];
    let quizzesFiltrados = [];
    let perguntasAtuais = [];
    let currentIndex = 0;
    let score = 0;
    let respostas = [];

    document.getElementById("pagar-button").addEventListener("click", () => {
        localStorage.setItem("acesso-liberado", "true");
        mostrarEtapa("tema-section");
        carregarTitulos();
    });

    async function carregarTitulos() {
        try {
            const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=id,titulo,subtema,perguntas&ativo=eq.true`, {
                headers: {
                    apikey: SUPABASE_ANON_KEY,
                    Authorization: `Bearer ${SUPABASE_ANON_KEY}`
                }
            });

            quizzes = await res.json();

            const titulosUnicos = [...new Set(quizzes.map(q => q.titulo))];
            tituloSelector.innerHTML = "<option value='' disabled selected>Selecione um tema</option>";
            titulosUnicos.forEach(titulo => {
                const option = document.createElement("option");
                option.value = titulo;
                option.textContent = titulo;
                tituloSelector.appendChild(option);
            });
        } catch (e) {
            alert("Erro ao carregar títulos.");
        }
    }

    carregarSubtemasBtn.addEventListener("click", () => {
        const tituloSelecionado = tituloSelector.value;
        if (!tituloSelecionado) return;

        quizzesFiltrados = quizzes.filter(q => q.titulo === tituloSelecionado);

        const subtemasUnicos = [...new Set(quizzesFiltrados.map(q => q.subtema))];
        subtemaSelector.innerHTML = "<option value='' disabled selected>Selecione um subtema</option>";
        subtemasUnicos.forEach(subtema => {
            const option = document.createElement("option");
            option.value = subtema;
            option.textContent = subtema;
            subtemaSelector.appendChild(option);
        });

        mostrarEtapa("subtema-section");
    });

    iniciarQuizButton.addEventListener("click", () => {
        const subtemaSelecionado = subtemaSelector.value;
        if (!subtemaSelecionado) return;

        const quizSelecionado = quizzesFiltrados.find(q => q.subtema === subtemaSelecionado);
        perguntasAtuais = shuffleArray(quizSelecionado.perguntas).slice(0, LIMITE_QUESTOES);

        score = 0;
        currentIndex = 0;
        respostas = [];

        mostrarEtapa("quiz-section");
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
                respostas.push({ pergunta: atual.question, correta: atual.answer, marcada: i, op });
                if (i === atual.answer) score++;
                currentIndex++;
                exibirPergunta();
            };
            quizContainer.appendChild(btn);
        });
    }

    function mostrarResultado() {
        mostrarEtapa("result-section");
        const resultContainer = document.getElementById("result");
        resultContainer.innerHTML = `<h2>Você acertou ${score} de ${perguntasAtuais.length} perguntas.</h2>`;

        const relatorioContainer = document.getElementById("relatorio");
        relatorioContainer.innerHTML = "";
        respostas.forEach((r, index) => {
            const div = document.createElement("div");
            div.className = "relatorio-item";
            div.innerHTML = `<strong>${index + 1}.</strong> ${r.pergunta}<br>
                Sua resposta: ${r.op} (${r.marcada})<br>`;
            relatorioContainer.appendChild(div);
        });
    }

    function shuffleArray(arr) {
        return arr.sort(() => Math.random() - 0.5);
    }

    if (localStorage.getItem("acesso-liberado") === "true") {
        mostrarEtapa("tema-section");
        carregarTitulos();
    } else {
        mostrarEtapa("qr-section");
    }
});
