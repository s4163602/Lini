function getCsrfToken() {
  const el = document.querySelector("input[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

async function postJson(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function qs(sel, root = document) {
  return root.querySelector(sel);
}

function qsa(sel, root = document) {
  return Array.from(root.querySelectorAll(sel));
}

function listIdFromEl(el) {
  return Number(el.getAttribute("data-list-id"));
}

function cardIdFromEl(el) {
  return Number(el.getAttribute("data-card-id"));
}

function reloadWithSearch(q) {
  const url = new URL(location.href);
  if (q && q.trim()) url.searchParams.set("q", q.trim());
  else url.searchParams.delete("q");
  location.href = url.toString();
}

const ctx = window.BOARD_CTX;
const endpoints = ctx.endpoints;

function roleCanManageLists() {
  return ctx.role === "admin" || ctx.role === "mentor";
}

function roleCanManageCards() {
  return ctx.role === "admin" || ctx.role === "mentor" || ctx.role === "student";
}

const listsEl = qs("#lists");
const newListBtn = qs("#newListBtn");
const searchInput = qs("#searchInput");
const exportBtn = qs("#exportBtn");
const resetBtn = qs("#resetBtn");

// Modal
const modal = qs("#modal");
const modalBackdrop = qs("#modalBackdrop");
const modalClose = qs("#modalClose");
const modalCancel = qs("#modalCancel");
const modalSave = qs("#modalSave");
const deleteCardBtn = qs("#deleteCardBtn");
const cardTitleInput = qs("#cardTitleInput");
const cardDescInput = qs("#cardDescInput");
const cardTagInput = qs("#cardTagInput");
const modalMeta = qs("#modalMeta");

let modalCardId = null;

function openModal(cardEl) {
  if (!roleCanManageCards()) return;

  modalCardId = cardIdFromEl(cardEl);

  const listEl = cardEl.closest("[data-list-id]");
  const listTitle = qs('[data-role="list-title"]', listEl)?.value || "List";

  const title = qs('[data-role="card-title"]', cardEl)?.textContent || "";
  const desc = qs('[data-role="card-desc"]', cardEl)?.textContent || "";
  const tag = cardEl.getAttribute("data-card-tag") || "not_started";

  cardTitleInput.value = title;
  cardDescInput.value = desc;
  if (cardTagInput) cardTagInput.value = tag;

  modalMeta.textContent = listTitle;

  modal.classList.remove("hidden");
  modal.classList.add("flex");
  cardTitleInput.focus();
  cardTitleInput.select();
}

function closeModal() {
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  modalCardId = null;
}

function applyRoleUI() {
  if (!roleCanManageLists()) {
    if (newListBtn) newListBtn.style.display = "none";
    qsa('[data-role="list-delete"]').forEach((b) => (b.style.display = "none"));
    qsa('[data-role="list-title"]').forEach((i) => i.setAttribute("disabled", "disabled"));
  }

  if (!roleCanManageCards()) {
    qsa('[data-role="add-card-btn"]').forEach((b) => (b.style.display = "none"));
    qsa('[data-role="new-card-input"]').forEach((i) => i.setAttribute("disabled", "disabled"));
    qsa('[data-role="quick-delete"]').forEach((b) => (b.style.display = "none"));

    if (modalSave) modalSave.setAttribute("disabled", "disabled");
    if (deleteCardBtn) deleteCardBtn.setAttribute("disabled", "disabled");
    if (modalSave) modalSave.classList.add("opacity-50");
    if (deleteCardBtn) deleteCardBtn.classList.add("opacity-50");
  }
}

function wireListsAndCards() {
  qsa('[data-role="list-title"]').forEach((input) => {
    input.addEventListener("change", async (e) => {
      if (!roleCanManageLists()) return;
      const listEl = e.target.closest("[data-list-id]");
      const id = listIdFromEl(listEl);
      await postJson(endpoints.listRenamePrefix + id + "/rename/", { title: e.target.value });
    });
  });

  qsa('[data-role="list-delete"]').forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      if (!roleCanManageLists()) return;
      const listEl = e.target.closest("[data-list-id]");
      const id = listIdFromEl(listEl);
      const ok = confirm("Delete this list and its cards?");
      if (!ok) return;
      await postJson(endpoints.listDeletePrefix + id + "/delete/", {});
      location.reload();
    });
  });

  qsa('[data-role="add-card-btn"]').forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      if (!roleCanManageCards()) return;
      const listEl = e.target.closest("[data-list-id]");
      const listId = listIdFromEl(listEl);
      const input = qs('[data-role="new-card-input"]', listEl);
      const title = (input.value || "").trim();
      if (!title) return;
      await postJson(endpoints.cardCreate, { list_id: listId, title });
      location.reload();
    });
  });

  qsa('[data-role="new-card-input"]').forEach((input) => {
    input.addEventListener("keydown", async (e) => {
      if (!roleCanManageCards()) return;
      if (e.key !== "Enter") return;
      e.preventDefault();
      const listEl = e.target.closest("[data-list-id]");
      const listId = listIdFromEl(listEl);
      const title = (e.target.value || "").trim();
      if (!title) return;
      await postJson(endpoints.cardCreate, { list_id: listId, title });
      location.reload();
    });
  });

  qsa("[data-card-id]").forEach((cardEl) => {
    cardEl.addEventListener("click", (e) => {
      const del = e.target.closest('[data-role="quick-delete"]');
      if (del) return;
      openModal(cardEl);
    });

    const qd = qs('[data-role="quick-delete"]', cardEl);
    if (qd) {
      qd.addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!roleCanManageCards()) return;
        const id = cardIdFromEl(cardEl);
        await postJson(endpoints.cardDeletePrefix + id + "/delete/", {});
        location.reload();
      });
    }
  });
}

function wireDragAndDrop() {
  if (roleCanManageLists()) {
    new Sortable(listsEl, {
      animation: 150,
      draggable: "[data-list-id]",
      onEnd: async () => {
        const order = qsa("[data-list-id]", listsEl).map((el) => listIdFromEl(el));
        await postJson(endpoints.listReorder, { order });
      },
    });
  }

  if (roleCanManageCards()) {
    qsa('[data-role="card-dropzone"]').forEach((zone) => {
      new Sortable(zone, {
        group: "cards",
        animation: 150,
        draggable: "[data-card-id]",
        onEnd: async (evt) => {
          const cardId = cardIdFromEl(evt.item);
          const toListId = Number(evt.to.getAttribute("data-list-id"));
          const toIndex = evt.newIndex;
          await postJson(endpoints.cardMove, { card_id: cardId, to_list_id: toListId, to_index: toIndex });
        },
      });
    });
  }
}

function initTopActions() {
  if (newListBtn) {
    newListBtn.addEventListener("click", async () => {
      if (!roleCanManageLists()) return;
      const name = prompt("List name?");
      if (!name) return;
      await postJson(endpoints.listCreate, { title: name });
      location.reload();
    });
  }

  if (searchInput) {
    let t = null;
    searchInput.addEventListener("input", () => {
      if (t) clearTimeout(t);
      t = setTimeout(() => reloadWithSearch(searchInput.value), 250);
    });
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", async () => {
      const res = await fetch(endpoints.exportJson);
      const json = await res.text();
      try {
        await navigator.clipboard.writeText(json);
        alert("Copied JSON to clipboard.");
      } catch {
        const w = window.open("", "_blank");
        if (w) w.document.write("<pre>" + json.replaceAll("<", "&lt;") + "</pre>");
      }
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      if (ctx.role !== "admin") {
        alert("Only admin can reset.");
        return;
      }
      const ok = confirm("Reset board?");
      if (!ok) return;
      await postJson(endpoints.reset, {});
      location.reload();
    });
  }
}

function initModal() {
  function save() {
    if (!roleCanManageCards()) return;
    if (!modalCardId) return;

    const title = (cardTitleInput.value || "").trim() || "Untitled";
    const desc = (cardDescInput.value || "").trim();
    const tag = (cardTagInput ? cardTagInput.value : "not_started");

    postJson(endpoints.cardUpdatePrefix + modalCardId + "/update/", { title, desc, tag })
      .then(() => location.reload())
      .catch(() => {});
  }

  if (modalSave) modalSave.addEventListener("click", save);
  if (modalCancel) modalCancel.addEventListener("click", closeModal);
  if (modalClose) modalClose.addEventListener("click", closeModal);
  if (modalBackdrop) modalBackdrop.addEventListener("click", closeModal);

  if (deleteCardBtn) {
    deleteCardBtn.addEventListener("click", async () => {
      if (!roleCanManageCards()) return;
      if (!modalCardId) return;
      const ok = confirm("Delete this card?");
      if (!ok) return;
      await postJson(endpoints.cardDeletePrefix + modalCardId + "/delete/", {});
      closeModal();
      location.reload();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (modal.classList.contains("hidden")) return;
    if (e.key === "Escape") closeModal();
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "enter") save();
  });
}

(function main() {
  applyRoleUI();
  wireListsAndCards();
  wireDragAndDrop();
  initTopActions();
  initModal();
})();
