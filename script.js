const SUPABASE_URL = "https://jszlastvwxefajjuquxt.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impzemxhc3R2d3hlZmFqanVxdXh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1ODMwODUsImV4cCI6MjA2NTE1OTA4NX0.onXBoSa9j6EeVBZxWncZ5uAGDIONHJQBajAzzgzCz18";

const LIMITE_QUESTOES = 20;
const TEMPO_POR_PERGUNTA = 20;

let perguntasAtuais = [];
let currentIndex = 0;
let score = 0;
let respostas = [];
let timer = null;

function mostrarEtapa(id) {
  document.querySelectorAll("section").forEach(sec => sec.classList.remove("active"));
  document.getElementById(id)?.classList.add("active");
}

function mostrarLoading(ativo) {
  document.getElementById("loading")?.classList.toggle("hidden", !ativo);
}

document.addEventListener("DOMContentLoaded", () => {
  const tituloSelector = document.getElementById("titulo-selector");
  const subtemaSelector = document.getElementById("subtema-selector");

  document.getElementById("carregar-subtemas").onclick = async () => {
    const titulo = tituloSelector.value;
    if (!titulo) return;
    mostrarLoading(true);
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=subtema&titulo=eq.${titulo}`, {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
          "Content-Type": "application/json",
          "Accept": "application/json"
        }
      });
      const dados = await res.json();
      const subtemas = [...new Set(dados.map(d => d.subtema))];
      subtemaSelector.innerHTML = `<option disabled selected>Selecione um subtema</option>`;
      subtemas.forEach(sub => {
        const opt = document.createElement("option");
        opt.value = sub;
        opt.textContent = sub;
        subtemaSelector.appendChild(opt);
      });
      mostrarEtapa("subtema-section");
    } catch (e) {
      console.error("Erro ao carregar subtemas:", e);
      alert("Erro ao carregar subtemas.");
    }
    mostrarLoading(false);
  };

  document.getElementById("start-quiz").onclick = async () => {
    const titulo = tituloSelector.value;
    const subtema = subtemaSelector.value;
    if (!titulo || !subtema) return;
    mostrarLoading(true);
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=perguntas&titulo=eq.${titulo}&subtema=eq.${subtema}`, {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
          "Content-Type": "application/json",
          "Accept": "application/json"
        }
      });
      const data = await res.json();
      perguntasAtuais = shuffleArray(data[0]?.perguntas || []).slice(0, LIMITE_QUESTOES);
      currentIndex = 0;
      score = 0;
      respostas = [];
      mostrarEtapa("quiz-section");
      exibirPergunta();
    } catch (e) {
      console.error("Erro ao carregar perguntas:", e);
      alert("Erro ao carregar perguntas.");
    }
    mostrarLoading(false);
  };

  document.getElementById("reiniciar").onclick = () => location.reload();

  document.getElementById("abrir-instrucoes").onclick = () => {
    document.getElementById("instrucoes-modal")?.classList.remove("hidden");
  };
  document.getElementById("fechar-instrucoes").onclick = () => {
    document.getElementById("instrucoes-modal")?.classList.add("hidden");
  };
  document.getElementById("voltar-tema").onclick = () => {
    mostrarEtapa("tema-section");
  };

  carregarTitulos();
  mostrarEtapa("tema-section");

  // Mostra a tela de doação QR ao carregar a página pela primeira vez
  document.getElementById("loadingQR").classList.remove("hidden");

    // Botão de fechar
  document.getElementById("fechar-loading").addEventListener("click", () => {
    document.getElementById("loadingQR").classList.add("hidden");
  });
});

async function carregarTitulos() {
  mostrarLoading(true);
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=titulo`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    const data = await res.json();
    const titulos = [...new Set(data.map(q => q.titulo))];
    const selector = document.getElementById("titulo-selector");
    selector.innerHTML = `<option disabled selected>Selecione um tema</option>`;
    titulos.forEach(titulo => {
      const opt = document.createElement("option");
      opt.value = titulo;
      opt.textContent = titulo;
      selector.appendChild(opt);
    });
  } catch (e) {
    console.error("Erro ao carregar títulos:", e);
    alert("Erro ao carregar títulos.");
  }
  mostrarLoading(false);
}

function exibirPergunta() {
  clearInterval(timer);
  const quiz = document.getElementById("quiz");
  quiz.innerHTML = "";
  if (currentIndex >= perguntasAtuais.length) return mostrarResultado();
  const pergunta = perguntasAtuais[currentIndex];
  quiz.innerHTML = `<h2>${pergunta.question}</h2>`;
  pergunta.options.forEach((op, i) => {
    const btn = document.createElement("button");
    btn.className = "option";
    btn.textContent = op;
    btn.onclick = () => {
      respostas.push({ pergunta: pergunta.question, correta: pergunta.answer, marcada: i, op });
      if (i === pergunta.answer) score++;
      currentIndex++;
      exibirPergunta();
    };
    quiz.appendChild(btn);
  });
  atualizarBarra();
}

function mostrarResultado() {
  clearInterval(timer);
  mostrarEtapa("result-section");

  document.getElementById("result").innerHTML = `<h2>Você acertou ${score} de ${perguntasAtuais.length} perguntas.</h2>`;

  const relatorio = document.getElementById("relatorio");
  relatorio.innerHTML = "";

  respostas.forEach((r, index) => {
    const isCorrect = r.marcada === r.correta;
    const marker = isCorrect ? "✅" : "❌";

    const div = document.createElement("div");
    div.className = "relatorio-item " + (isCorrect ? "correto" : "incorreto");

    div.innerHTML = `
      <p><strong>${marker} Pergunta ${index + 1}:</strong> ${r.pergunta}</p>
      <p><strong>Sua resposta:</strong> ${r.op}</p>
    `;

    relatorio.appendChild(div);
  });
}

function atualizarBarra() {
  const barra = document.getElementById("progress-bar");
  barra.textContent = `Pergunta ${currentIndex + 1} de ${perguntasAtuais.length}`;
}

function shuffleArray(arr) {
  return arr.sort(() => Math.random() - 0.5);
}
