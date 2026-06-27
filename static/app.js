const pdfFile = document.querySelector("#pdfFile");
const qualificationFile = document.querySelector("#qualificationFile");
const pdfName = document.querySelector("#pdfName");
const qualificationName = document.querySelector("#qualificationName");
const analyzeBtn = document.querySelector("#analyzeBtn");
const demoBtn = document.querySelector("#demoBtn");
const statusBox = document.querySelector("#status");
const decision = document.querySelector("#decision");
const agentGrid = document.querySelector("#agentGrid");
const exportsBox = document.querySelector("#exports");
const exportLinks = document.querySelector("#exportLinks");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindDrop(label, input, nameNode) {
  input.addEventListener("change", () => {
    nameNode.textContent = input.files[0] ? input.files[0].name : "拖拽或点击选择文件";
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    label.addEventListener(eventName, (event) => {
      event.preventDefault();
      label.classList.add("drag");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    label.addEventListener(eventName, (event) => {
      event.preventDefault();
      label.classList.remove("drag");
    });
  });

  label.addEventListener("drop", (event) => {
    input.files = event.dataTransfer.files;
    nameNode.textContent = input.files[0] ? input.files[0].name : "拖拽或点击选择文件";
  });
}

bindDrop(document.querySelector("#pdfDrop"), pdfFile, pdfName);
bindDrop(document.querySelector("#qualificationDrop"), qualificationFile, qualificationName);

function downloadUrl(path) {
  return `/download?path=${encodeURIComponent(path)}`;
}

function renderJsonBlock(data) {
  return escapeHtml(JSON.stringify(data || {}, null, 2));
}

function renderReport(report) {
  const decisionData = report.decision || {};
  decision.hidden = false;
  document.querySelector("#recommendation").textContent = decisionData.recommendation || "-";
  document.querySelector("#score").textContent = decisionData.score ?? "-";
  document.querySelector("#highRisk").textContent = decisionData.high_risk_count ?? "-";

  const agents = report.agents || {};
  const parser = agents.skill1_pdf_parser || {};
  const matcher = agents.skill2_qualification_matcher || {};
  const risk = agents.skill3_risk_reviewer || {};
  const writer = agents.skill4_bid_writer || {};

  const missingTags = (matcher.missing_materials || [])
    .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
    .join("");

  agentGrid.innerHTML = `
    <article class="card">
      <h2>Skill1 PDF文档解析Agent</h2>
      <pre>${renderJsonBlock(parser.key_info || {})}</pre>
      <p>${escapeHtml((parser.notes || []).join("；"))}</p>
    </article>
    <article class="card">
      <h2>Skill2 资质匹配打分Agent</h2>
      <p><strong>${escapeHtml(matcher.overall_status || "-")}</strong></p>
      ${missingTags}
      <pre>${renderJsonBlock(matcher.checks || [])}</pre>
    </article>
    <article class="card">
      <h2>Skill3 投标风险审查Agent</h2>
      <pre>${renderJsonBlock(risk.summary || {})}</pre>
      <pre>${renderJsonBlock((risk.risks || []).slice(0, 4))}</pre>
    </article>
    <article class="card">
      <h2>Skill4 投标方案生成Agent</h2>
      <pre>${escapeHtml((writer.markdown_draft || "").slice(0, 1800))}</pre>
    </article>
  `;

  exportsBox.hidden = false;
  exportLinks.innerHTML = Object.entries(report.exports || {})
    .map(([key, value]) => `<a href="${downloadUrl(value)}">${escapeHtml(key)}</a>`)
    .join("");
}

async function analyzeUpload() {
  if (!pdfFile.files[0] || !qualificationFile.files[0]) {
    statusBox.textContent = "请先选择招标PDF和企业资质文件";
    return;
  }
  const form = new FormData();
  form.append("tender_pdf", pdfFile.files[0]);
  form.append("qualification_file", qualificationFile.files[0]);
  await requestReport("/api/analyze", { method: "POST", body: form });
}

async function requestReport(url, options = {}) {
  analyzeBtn.disabled = true;
  demoBtn.disabled = true;
  statusBox.textContent = "Agent分析中";
  try {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(await response.text());
    const report = await response.json();
    renderReport(report);
    statusBox.textContent = "研判完成";
  } catch (error) {
    statusBox.textContent = "分析失败";
    agentGrid.innerHTML = `<article class="card"><h2>错误</h2><pre>${escapeHtml(String(error))}</pre></article>`;
  } finally {
    analyzeBtn.disabled = false;
    demoBtn.disabled = false;
  }
}

analyzeBtn.addEventListener("click", analyzeUpload);
demoBtn.addEventListener("click", () => requestReport("/api/demo"));
