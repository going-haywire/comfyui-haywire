// SPDX-License-Identifier: GPL-3.0-or-later
// Publishes the open workflow to haywire whenever it changes and holds a Haywire Output.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const DELAY_MS = 500;
let timer = null;

function workflowName() {
  try {
    const wf = app.extensionManager?.workflow?.activeWorkflow;
    if (wf?.filename) return wf.filename;
  } catch (e) {
    // older frontends have no workflow store
  }
  return "Untitled";
}

async function publish() {
  timer = null;
  const hasOutput = app.graph?.findNodesByType?.("HaywireOutput")?.length > 0;
  if (!hasOutput) return;
  const { output } = await app.graphToPrompt();
  await api.fetchApi("/haywire/workflow/publish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: api.clientId, name: workflowName(), workflow: output }),
  });
}

app.registerExtension({
  name: "haywire.workflowExchange",
  setup() {
    api.addEventListener("graphChanged", () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => publish().catch((e) => console.warn("haywire publish", e)), DELAY_MS);
    });
  },
});
