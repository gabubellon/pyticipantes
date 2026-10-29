const $ = (id) => document.getElementById(id);
let M = null;            // modelo atual
let colunas = [];
let fontes = [];
let focoTextarea = null;
let timerPrevia = null;
let timerSalvar = null;

async function api(url, opts = {}) {
  if (opts.json !== undefined) {
    opts.method = opts.method || "POST";
    opts.headers = { "Content-Type": "application/json" };
    opts.body = JSON.stringify(opts.json);
  }
  const r = await fetch(url, opts);
  if ((r.headers.get("content-type") || "").includes("json")) {
    const d = await r.json();
    if (!r.ok) throw new Error(d.erro || r.statusText);
    return d;
  }
  if (!r.ok) throw new Error(r.statusText);
  return r;
}
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const msg = (t, erro) => { $("status").textContent = t; $("status").className = erro ? "erro" : "mut"; };

// ---------- Modelos ----------
async function carregarLista(selecionar) {
  const lista = await api("/api/modelos");
  if (!lista.length) { const m = await api("/api/modelos", { json: { nome: "Certificado de participação" } }); return carregarLista(m.id); }
  $("selModelo").innerHTML = lista.map((m) => `<option value="${m.id}">${esc(m.nome)}</option>`).join("");
  const id = selecionar || localStorage.getItem("modelo") || lista[0].id;
  $("selModelo").value = lista.some((m) => m.id === id) ? id : lista[0].id;
  await abrirModelo($("selModelo").value);
}

function aplicarDetalhe(d) {
  M = d.modelo; colunas = d.colunas; fontes = d.fontes;
  $("app").classList.remove("hidden");
  $("nomeModelo").value = M.nome;
  $("pagina").value = M.pagina;
  $("nomeArquivo").value = M.nome_arquivo;
  $("colunaEmail").value = M.coluna_email;
  const e = M.email;
  $("smtpServidor").value = e.servidor; $("smtpPorta").value = e.porta; $("smtpUsuario").value = e.usuario;
  $("smtpRemetente").value = e.remetente; $("smtpCc").value = e.cc;
  $("mailAssunto").value = e.assunto; $("mailCorpo").value = e.corpo;
  $("linkExportar").href = `/api/modelos/${M.id}/exportar`;
  $("previa").className = M.pagina === "retrato" ? "retrato" : "";
  $("linhaPrevia").max = Math.max(d.total, 1);
  $("limiteQtd").max = Math.max(d.total, 1);
  if (Number($("limiteQtd").value) > d.total) $("limiteQtd").value = Math.max(d.total, 1);
  $("totalLinhas").textContent = d.total ? `(${d.total})` : "";

  $("cardAmostra").classList.toggle("hidden", !colunas.length);
  $("infoPlanilha").innerHTML = d.erro_planilha ? `<span class="erro">${esc(d.erro_planilha)}</span>`
    : M.planilha ? `✓ ${esc(M.planilha)} — ${d.total} participante(s), ${colunas.length} coluna(s). Para trocar, escolha outro arquivo.` : "Nenhuma planilha enviada ainda.";
  $("tabAmostra").innerHTML = colunas.length
    ? `<tr>${colunas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr>` +
      d.amostra.map((l) => `<tr>${colunas.map((c) => `<td>${esc(l[c])}</td>`).join("")}</tr>`).join("") +
      (d.total > d.amostra.length ? `<tr><td class="mut" colspan="${colunas.length}">… e mais ${d.total - d.amostra.length}</td></tr>` : "")
    : "";
  $("chips").innerHTML = colunas.map((c) => `<button class="chip" data-c="${esc(c)}">{${esc(c)}}</button>`).join("") || '<span class="mut">Envie uma planilha no passo 1.</span>';
  desenharBlocos();
}

async function abrirModelo(id) {
  localStorage.setItem("modelo", id);
  aplicarDetalhe(await api(`/api/modelos/${id}`));
  await listarCertificados();
  atualizarPrevia();
}

$("selModelo").onchange = () => abrirModelo($("selModelo").value);
$("btnNovo").onclick = async () => {
  const nome = prompt("Nome do novo certificado:", "Novo certificado");
  if (nome) { const m = await api("/api/modelos", { json: { nome } }); await carregarLista(m.id); }
};
$("btnExcluir").onclick = async () => {
  if (confirm(`Excluir "${M.nome}"? Os PDFs gerados são apagados; o layout vai para a lixeira (data/lixeira).`)) {
    await api(`/api/modelos/${M.id}`, { method: "DELETE" }); localStorage.removeItem("modelo"); await carregarLista();
  }
};

// ---------- Abas ----------
function irPara(a) {
  document.querySelectorAll("#abas button").forEach((b) => b.classList.toggle("on", b.dataset.aba === a));
  document.querySelectorAll("main > section").forEach((s) => s.classList.toggle("hidden", s.id !== `aba-${a}`));
  window.scrollTo(0, 0);
  if (a === "design") atualizarPrevia();
}
$("abas").onclick = (e) => { const b = e.target.closest("button"); if (b) irPara(b.dataset.aba); };
document.addEventListener("click", (e) => { if (e.target.dataset.ir) irPara(e.target.dataset.ir); });

// ---------- Salvar ----------
function coletar() {
  M.nome = $("nomeModelo").value; M.pagina = $("pagina").value;
  M.nome_arquivo = $("nomeArquivo").value; M.coluna_email = $("colunaEmail").value;
  M.email = {
    servidor: $("smtpServidor").value, porta: Number($("smtpPorta").value) || 587, usuario: $("smtpUsuario").value,
    remetente: $("smtpRemetente").value, cc: $("smtpCc").value, assunto: $("mailAssunto").value, corpo: $("mailCorpo").value,
  };
  return M;
}
async function salvar() {
  try { await api(`/api/modelos/${M.id}`, { method: "PUT", json: coletar() }); msg("Salvo."); } catch (e) { msg(e.message, true); }
}
function salvarDepois() { clearTimeout(timerSalvar); timerSalvar = setTimeout(salvar, 800); }
document.querySelectorAll("#aba-dados input[type=text], #aba-gerar input, #aba-email input:not([type=password]), #aba-email textarea")
  .forEach((el) => el.addEventListener("input", salvarDepois));
$("nomeModelo").addEventListener("change", async () => {
  await salvar();
  const opt = $("selModelo").selectedOptions[0]; if (opt) opt.textContent = M.nome;
});
$("pagina").onchange = () => { $("previa").className = $("pagina").value === "retrato" ? "retrato" : ""; mudou(); };

// ---------- Uploads ----------
async function enviarArquivo(url, input) {
  if (!input.files[0]) return;
  const fd = new FormData(); fd.append("arquivo", input.files[0]);
  try { await salvar(); aplicarDetalhe(await api(url, { method: "POST", body: fd })); atualizarPrevia(); msg("Arquivo enviado."); }
  catch (e) { msg(e.message, true); }
  input.value = "";
}
$("filePlanilha").onchange = (e) => enviarArquivo(`/api/modelos/${M.id}/planilha`, e.target);
$("fileFundo").onchange = (e) => enviarArquivo(`/api/modelos/${M.id}/fundo`, e.target);
$("fileLayout").onchange = async (e) => {
  const fd = new FormData(); fd.append("arquivo", e.target.files[0]);
  try { const m = await api("/api/modelos/importar", { method: "POST", body: fd }); await carregarLista(m.id); msg("Layout carregado como novo certificado."); }
  catch (er) { msg(er.message, true); }
  e.target.value = "";
};
$("fileFonte").onchange = async (e) => {
  const fd = new FormData(); fd.append("arquivo", e.target.files[0]);
  try { fontes = await api("/api/fontes", { method: "POST", body: fd }); desenharBlocos(); msg("Fonte adicionada."); }
  catch (er) { msg(er.message, true); }
  e.target.value = "";
};

// ---------- Blocos de texto ----------
function desenharBlocos() {
  $("blocos").innerHTML = M.blocos.map((b, i) => `
    <div class="bloco" data-i="${i}">
      <textarea data-k="texto" rows="2" placeholder="Texto">${esc(b.texto)}</textarea>
      <div class="grid">
        <div><label>Fonte</label><select data-k="fonte">${fontes.map((f) => `<option ${f === b.fonte ? "selected" : ""}>${esc(f)}</option>`).join("")}</select></div>
        <div><label>Tamanho</label><input type="number" data-k="tamanho" value="${b.tamanho}" min="4" max="200"></div>
        <div><label>Cor</label><input type="color" data-k="cor" value="${b.cor}" style="width:100%;height:38px"></div>
        <div><label>Alinhamento</label><select data-k="alinhamento">${["esquerda", "centro", "direita", "justificado"].map((a) => `<option ${a === b.alinhamento ? "selected" : ""}>${a}</option>`).join("")}</select></div>
      </div>
      <details>
        <summary>Posição</summary>
        <div class="grid">
          <div><label>Esquerda (%)</label><input type="number" data-k="x" value="${b.x}" min="0" max="100" step="0.5"></div>
          <div><label>Topo (%)</label><input type="number" data-k="y" value="${b.y}" min="0" max="100" step="0.5"></div>
          <div><label>Largura (%)</label><input type="number" data-k="largura" value="${b.largura}" min="1" max="100" step="0.5"></div>
        </div>
      </details>
      <div class="bar" style="margin-top:10px">
        <button class="link" data-acao="sobe" ${i === 0 ? "disabled" : ""}>↑ Subir</button>
        <button class="link" data-acao="desce" ${i === M.blocos.length - 1 ? "disabled" : ""}>↓ Descer</button>
        <span class="grow"></span>
        <button class="link del" data-acao="rm">Remover</button>
      </div>
    </div>`).join("");
}
$("blocos").addEventListener("input", (e) => {
  const k = e.target.dataset.k; if (!k) return;
  const i = e.target.closest(".bloco").dataset.i;
  M.blocos[i][k] = e.target.type === "number" ? Number(e.target.value) : e.target.value;
  mudou();
});
$("blocos").addEventListener("focusin", (e) => { if (e.target.tagName === "TEXTAREA") focoTextarea = e.target; });
$("blocos").addEventListener("click", (e) => {
  const acao = e.target.dataset.acao; if (!acao) return;
  const i = Number(e.target.closest(".bloco").dataset.i);
  if (acao === "rm") M.blocos.splice(i, 1);
  else { const j = acao === "sobe" ? i - 1 : i + 1; [M.blocos[i], M.blocos[j]] = [M.blocos[j], M.blocos[i]]; }
  desenharBlocos(); mudou();
});
$("btnAddBloco").onclick = () => {
  M.blocos.push({ texto: "Novo texto", fonte: "Helvetica", tamanho: 16, cor: "#185666", alinhamento: "centro", x: 10, y: 50, largura: 80 });
  desenharBlocos(); mudou();
};
$("chips").onclick = (e) => {
  const c = e.target.dataset.c; if (!c || !focoTextarea) return;
  const t = focoTextarea, f = $("formato").value, ins = `{${c}${f ? "|" + f : ""}}`;
  t.setRangeText(ins, t.selectionStart, t.selectionEnd, "end");
  t.dispatchEvent(new Event("input", { bubbles: true })); t.focus();
};

function mudou() { clearTimeout(timerPrevia); timerPrevia = setTimeout(atualizarPrevia, 400); salvarDepois(); }

// ---------- Prévia ----------
let urlPrevia = null;
async function atualizarPrevia() {
  if (!M) return;
  try {
    const r = await api(`/api/modelos/${M.id}/previa`, { json: { modelo: coletar(), linha: Number($("linhaPrevia").value) - 1 } });
    const blob = await r.blob();
    if (urlPrevia) URL.revokeObjectURL(urlPrevia);
    urlPrevia = URL.createObjectURL(blob);
    $("previa").src = urlPrevia + "#toolbar=0&navpanes=0";
  } catch (e) { msg("Prévia: " + e.message, true); }
}
$("linhaPrevia").oninput = mudou;

// ---------- Gerar e listar ----------
let certificados = [];
async function listarCertificados() {
  certificados = await api(`/api/modelos/${M.id}/certificados`);
  const url = (c) => `/api/modelos/${M.id}/arquivo/${encodeURIComponent(c.arquivo)}`;
  $("tabCert").innerHTML = certificados.length
    ? "<tr><th>#</th><th>Nome</th><th>E-mail</th><th>Arquivo</th></tr>" + certificados.map((c) =>
        `<tr><td>${c.linha}</td><td>${esc(c.nome)}</td><td>${esc(c.email)}</td><td><a href="${url(c)}" target="_blank">${esc(c.arquivo)}</a></td></tr>`).join("")
    : '<tr><td class="mut">Nenhum certificado gerado ainda.</td></tr>';
  desenharEnvio();
}
$("btnGerar").onclick = async () => {
  $("btnGerar").disabled = true; $("msgGerar").textContent = "Gerando…";
  try { const limite = document.querySelector('input[name="qtd"]:checked').value === "limite" ? Number($("limiteQtd").value) : null;
    await api(`/api/modelos/${M.id}/gerar`, { json: { ...coletar(), limite } }); await listarCertificados(); $("msgGerar").innerHTML = `<span class="ok">${certificados.length} certificado(s) gerado(s).</span>`; }
  catch (e) { $("msgGerar").innerHTML = `<span class="erro">${esc(e.message)}</span>`; }
  $("btnGerar").disabled = false;
};
$("limiteQtd").onfocus = () => (document.querySelector('input[name="qtd"][value="limite"]').checked = true);
$("btnPasta").onclick = () => api(`/api/modelos/${M.id}/abrir-pasta`, { json: {} });

// ---------- Envio ----------
function desenharEnvio() {
  $("tabEnvio").innerHTML = certificados.length
    ? "<tr><th></th><th>Nome</th><th>E-mail</th><th>Situação</th></tr>" + certificados.map((c) =>
        `<tr data-busca="${esc((c.nome + " " + c.email).toLowerCase())}"><td><input type="checkbox" class="sel" value="${esc(c.arquivo)}" ${c.email ? "" : "disabled"}></td><td>${esc(c.nome)}</td><td>${esc(c.email) || '<span class="erro">sem e-mail</span>'}</td>
         <td>${c.enviado_em ? `<span class="ok">enviado ${esc(c.enviado_em.replace("T", " "))}</span>` : c.erro ? `<span class="erro" title="${esc(c.erro)}">erro</span>` : '<span class="mut">pendente</span>'}</td></tr>`).join("")
    : '<tr><td class="mut">Gere os certificados primeiro (passo 3).</td></tr>';
  filtrarEnvio();
}
// linhas visíveis da tabela de destinatários (checkbox habilitado)
const visiveis = () => [...document.querySelectorAll("#tabEnvio tr[data-busca]:not(.hidden) .sel:not(:disabled)")];
function filtrarEnvio() {
  const q = $("filtroEnvio").value.trim().toLowerCase();
  document.querySelectorAll("#tabEnvio tr[data-busca]").forEach((tr) => tr.classList.toggle("hidden", !tr.dataset.busca.includes(q)));
  contarEnvio();
}
function contarEnvio() {
  const total = certificados.length, mostrados = document.querySelectorAll("#tabEnvio tr[data-busca]:not(.hidden)").length;
  const marcados = document.querySelectorAll(".sel:checked").length;
  $("contaEnvio").textContent = total ? `Mostrando ${mostrados} de ${total} · ${marcados} marcado(s) para envio` : "";
  $("btnEnviar").textContent = marcados ? `Enviar ${marcados} selecionado(s)` : "Enviar selecionados";
}
$("filtroEnvio").oninput = filtrarEnvio;
$("tabEnvio").addEventListener("change", contarEnvio);
$("btnTodos").onclick = () => { const cbs = visiveis(); const marcar = cbs.some((c) => !c.checked); cbs.forEach((c) => (c.checked = marcar)); contarEnvio(); };
$("btnPendentes").onclick = () => {
  const pend = new Set(certificados.filter((c) => !c.enviado_em).map((c) => c.arquivo));
  visiveis().forEach((cb) => (cb.checked = pend.has(cb.value)));
  contarEnvio();
};

$("btnEnviar").onclick = async () => {
  const arquivos = [...document.querySelectorAll(".sel:checked")].map((c) => c.value);
  if (!arquivos.length) return alert("Selecione ao menos um certificado.");
  if (!confirm(`Enviar ${arquivos.length} e-mail(s) agora?`)) return;
  $("log").innerHTML = ""; $("btnEnviar").disabled = true;
  try {
    const { job } = await api(`/api/modelos/${M.id}/enviar`, { json: { email: coletar().email, senha: $("smtpSenha").value, arquivos } });
    acompanhar(job);
  } catch (e) { $("log").innerHTML = `<div class="erro">${esc(e.message)}</div>`; $("btnEnviar").disabled = false; }
};
async function acompanhar(job) {
  let vistos = 0;
  while (true) {
    const d = await api(`/api/envios/${job}`);
    d.log.slice(vistos).forEach((l) => $("log").insertAdjacentHTML("beforeend", `<div class="${l.nivel}">[${l.hora}] ${esc(l.msg)}</div>`));
    vistos = d.log.length; $("log").scrollTop = $("log").scrollHeight;
    if (d.fim) break;
    await new Promise((r) => setTimeout(r, 800));
  }
  $("btnEnviar").disabled = false;
  await listarCertificados();
}

carregarLista().then(() => { const a = location.hash.slice(1); if (a) irPara(a); }).catch((e) => msg(e.message, true));
