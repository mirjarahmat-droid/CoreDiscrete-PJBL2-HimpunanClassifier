// app.js
const LABELS = { A: "UKM Olahraga", B: "UKM Seni & Budaya", C: "Penerima Beasiswa" };
const SYMBOL = { union: "∪", intersection: "∩", difference: "−", complement: "ᶜ" };

function buildSets() {
  const A = new Set(dataset.filter((d) => d.olahraga).map((d) => d.id));
  const B = new Set(dataset.filter((d) => d.seni).map((d) => d.id));
  const C = new Set(dataset.filter((d) => d.beasiswa).map((d) => d.id));
  const U = new Set(dataset.map((d) => d.id));
  return { A, B, C, U };
}

const setUnion        = (s1, s2) => new Set([...s1, ...s2]);
const setIntersection = (s1, s2) => new Set([...s1].filter((x) => s2.has(x)));
const setDifference   = (s1, s2) => new Set([...s1].filter((x) => !s2.has(x)));
const setComplement   = (s, u)   => new Set([...u].filter((x) => !s.has(x)));

function computeResultIds(op, label1, label2) {
  const { A, B, C, U } = buildSets();
  const map = { A, B, C };
  const s1 = map[label1];
  const s2 = label2 ? map[label2] : null;
  switch (op) {
    case "union": return setUnion(s1, s2);
    case "intersection": return setIntersection(s1, s2);
    case "difference": return setDifference(s1, s2);
    case "complement": return setComplement(s1, U);
    default: return new Set();
  }
}

function renderTable() {
  const tbody = document.querySelector("#dataset-table tbody");
  tbody.innerHTML = "";
  dataset.forEach((d) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.id}</td><td>${d.nama}</td><td>${d.nim}</td>
      <td>${d.olahraga ? "✔" : "–"}</td>
      <td>${d.seni ? "✔" : "–"}</td>
      <td>${d.beasiswa ? "✔" : "–"}</td>`;
    tbody.appendChild(tr);
  });
}

function regionMarkup(inA, inB, inC) {
  let el = `<rect x="0" y="0" width="400" height="300" fill="#f1c40f" opacity="0.55"/>`;
  if (inA) el = `<g clip-path="url(#clipA)">${el}</g>`; else el = `<g mask="url(#maskOutA)">${el}</g>`;
  if (inB) el = `<g clip-path="url(#clipB)">${el}</g>`; else el = `<g mask="url(#maskOutB)">${el}</g>`;
  if (inC) el = `<g clip-path="url(#clipC)">${el}</g>`; else el = `<g mask="url(#maskOutC)">${el}</g>`;
  return el;
}

function renderVenn(op, label1, label2) {
  const layer = document.getElementById("highlight-layer");
  const valOf = (flags, label) => ({ A: flags.a, B: flags.b, C: flags.c }[label]);
  let html = "";
  for (let a = 0; a <= 1; a++) {
    for (let b = 0; b <= 1; b++) {
      for (let c = 0; c <= 1; c++) {
        const flags = { a: !!a, b: !!b, c: !!c };
        const v1 = valOf(flags, label1);
        const v2 = label2 ? valOf(flags, label2) : null;
        let show = false;
        if (op === "union") show = v1 || v2;
        else if (op === "intersection") show = v1 && v2;
        else if (op === "difference") show = v1 && !v2;
        else if (op === "complement") show = !v1;
        if (show) html += regionMarkup(flags.a, flags.b, flags.c);
      }
    }
  }
  layer.innerHTML = html;
}

const opForm   = document.getElementById("op-form");
const set2Wrap = document.getElementById("set2-wrap");
const opSelect = document.getElementById("operation");

opSelect.addEventListener("change", () => {
  set2Wrap.style.display = opSelect.value === "complement" ? "none" : "";
});

opForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const op = opSelect.value;
  const s1 = document.getElementById("set1").value;
  const s2 = op === "complement" ? null : document.getElementById("set2").value;

  const resultIds = computeResultIds(op, s1, s2);
  const resultRows = dataset.filter((d) => resultIds.has(d.id));

  const formula =
    op === "complement"
      ? `${s1}ᶜ  (bukan anggota ${LABELS[s1]})`
      : `${s1} ${SYMBOL[op]} ${s2}  (${LABELS[s1]} vs ${LABELS[s2]})`;
  document.getElementById("result-formula").textContent = formula;

  const list = document.getElementById("result-list");
  list.innerHTML = resultRows.length
    ? resultRows.map((d) => `<li>${d.nama} (${d.nim})</li>`).join("")
    : "<li><em>Tidak ada anggota.</em></li>";

  renderVenn(op, s1, s2);
});

document.getElementById("add-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const nama = document.getElementById("f-nama").value.trim();
  const nim = document.getElementById("f-nim").value.trim() || "-";
  if (!nama) return;
  const newId = dataset.length ? Math.max(...dataset.map((d) => d.id)) + 1 : 1;
  dataset.push({
    id: newId, nama, nim,
    olahraga: document.getElementById("f-a").checked,
    seni: document.getElementById("f-b").checked,
    beasiswa: document.getElementById("f-c").checked,
  });
  e.target.reset();
  renderTable();
});

document.getElementById("import-json").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const imported = JSON.parse(reader.result);
      if (Array.isArray(imported)) {
        dataset = imported;
        renderTable();
        alert("Dataset berhasil diimpor (" + dataset.length + " record).");
      }
    } catch (err) {
      alert("File JSON tidak valid: " + err.message);
    }
  };
  reader.readAsText(file);
});

renderTable();
