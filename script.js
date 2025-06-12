// script.js com busca sob demanda de títulos, subtemas e perguntas

const SUPABASE_URL = "https://jszlastvwxefajjuquxt.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impzemxhc3R2d3hlZmFqanVxdXh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1ODMwODUsImV4cCI6MjA2NTE1OTA4NX0.onXBoSa9j6EeVBZxWncZ5uAGDIONHJQBajAzzgzCz18";
const LIMITE_QUESTOES = 20;
const TEMPO_POR_PERGUNTA = 20; // segundos

let perguntasAtuais = [];
let currentIndex = 0;
let score = 0;
let respostas = [];
let timer;

function mostrarEtapa(id) {
  document.querySelectorAll("section").forEach(sec => sec.classList.remove("active"));
  const destino = document.getElementById(id);
  if (destino) destino.classList.add("active");
}

function mostrarLoading(ativo) {
  document.getElementById("loading").classList.toggle("hidden", !ativo);
}

document.addEventListener("DOMContentLoaded", function () {
  const tituloSelector = document.getElementById("titulo-selector");
  const subtemaSelector = document.getElementById("subtema-selector");

  document.getElementById("carregar-subtemas").addEventListener("click", async () => {
    const tituloSelecionado = tituloSelector.value;
    if (!tituloSelecionado) return;
    mostrarLoading(true);
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=subtema&titulo=eq.${tituloSelecionado}`, {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const dados = await res.json();
      const subtemasUnicos = [...new Set(dados.map(q => q.subtema))];
      subtemaSelector.innerHTML = "<option disabled selected>Selecione um subtema</option>";
      subtemasUnicos.forEach(subtema => {
        const option = document.createElement("option");
        option.value = subtema;
        option.textContent = subtema;
        subtemaSelector.appendChild(option);
      });
      mostrarEtapa("subtema-section");
    } catch (e) {
      alert("Erro ao carregar subtemas.");
      console.error(e);
    }
    mostrarLoading(false);
  });

  document.getElementById("abrir-instrucoes").addEventListener("click", () => {
    document.getElementById("instrucoes-modal").classList.remove("hidden");
  });
  document.getElementById("fechar-instrucoes").addEventListener("click", () => {
    document.getElementById("instrucoes-modal").classList.add("hidden");
  });
  document.getElementById("voltar-tema").addEventListener("click", () => {
    mostrarEtapa("tema-section");
  });

  document.getElementById("start-quiz").addEventListener("click", async () => {
    const subtemaSelecionado = subtemaSelector.value;
    const tituloSelecionado = document.getElementById("titulo-selector").value;
    if (!subtemaSelecionado || !tituloSelecionado) return;
    mostrarLoading(true);
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=perguntas&titulo=eq.${tituloSelecionado}&subtema=eq.${subtemaSelecionado}`, {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const data = await res.json();
      perguntasAtuais = shuffleArray(data[0]?.perguntas || []).slice(0, LIMITE_QUESTOES);
      score = 0;
      currentIndex = 0;
      respostas = [];
      mostrarEtapa("quiz-section");
      exibirPergunta();
    } catch (e) {
      alert("Erro ao carregar perguntas.");
      console.error(e);
    }
    mostrarLoading(false);
  });

  document.getElementById("reiniciar").addEventListener("click", () => {
    window.location.reload();
  });

  mostrarEtapa("tema-section");
  carregarTitulos();
});

async function carregarTitulos() {
  mostrarLoading(true);
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/quizzes?select=titulo`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`
      }
    });
    const data = await res.json();
    const titulosUnicos = [...new Set(data.map(q => q.titulo))];
    const selector = document.getElementById("titulo-selector");
    selector.innerHTML = "<option disabled selected>Selecione um tema</option>";
    titulosUnicos.forEach(titulo => {
      const option = document.createElement("option");
      option.value = titulo;
      option.textContent = titulo;
      selector.appendChild(option);
    });
  } catch (e) {
    alert("Erro ao carregar títulos.");
    console.error(e);
  }
  mostrarLoading(false);
}

function exibirPergunta() {
  clearInterval(timer);
  const container = document.getElementById("quiz");
  container.innerHTML = "";
  if (currentIndex >= perguntasAtuais.length) {
    mostrarResultado();
    return;
  }
  atualizarBarra();
  iniciarTimer();
  const atual = perguntasAtuais[currentIndex];
  const h2 = document.createElement("h2");
  h2.textContent = atual.question;
  container.appendChild(h2);
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
    container.appendChild(btn);
  });
}

function mostrarResultado() {
  mostrarEtapa("result-section");
  clearInterval(timer);
  document.getElementById("result").innerHTML = `<h2>Você acertou ${score} de ${perguntasAtuais.length} perguntas.</h2>`;
  const relatorioContainer = document.getElementById("relatorio");
  relatorioContainer.innerHTML = "";
  respostas.forEach((r, index) => {
    const div = document.createElement("div");
    div.className = "relatorio-item";
    div.innerHTML = `<strong>${index + 1}.</strong> ${r.pergunta}<br>Sua resposta: ${r.op} (${r.marcada})<br>`;
    relatorioContainer.appendChild(div);
  });
}

function iniciarTimer() {
  let tempo = TEMPO_POR_PERGUNTA;
  const display = document.getElementById("time-counter");
  display.textContent = tempo;
  timer = setInterval(() => {
    tempo--;
    display.textContent = tempo;
    if (tempo <= 0) {
      clearInterval(timer);
      respostas.push({ pergunta: perguntasAtuais[currentIndex].question, correta: perguntasAtuais[currentIndex].answer, marcada: -1, op: "(sem resposta)" });
      currentIndex++;
      exibirPergunta();
    }
  }, 1000);
}

function atualizarBarra() {
  const barra = document.getElementById("progress-bar");
  barra.textContent = `Pergunta ${currentIndex + 1} de ${perguntasAtuais.length}`;
}

function shuffleArray(arr) {
  return arr.sort(() => Math.random() - 0.5);
}