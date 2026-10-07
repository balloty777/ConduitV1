export const esc = (value = "") => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[c]));
export const shortId = (value = "") => value ? `${value.slice(0,8)}…${value.slice(-4)}` : "—";
export const fmtDate = (value) => value ? new Intl.DateTimeFormat(undefined,{dateStyle:"medium",timeStyle:"short"}).format(new Date(value)) : "—";
export const fmtTime = (value) => value ? new Intl.DateTimeFormat(undefined,{timeStyle:"short"}).format(new Date(value)) : "—";
export const statusTone = (status = "") => { const s=status.toLowerCase(); if(["completed","approved","scheduled","healthy"].some(x=>s.includes(x))) return "green"; if(["pending","waiting","running","draft","open"].some(x=>s.includes(x))) return s.includes("running") ? "blue" : "amber"; if(["failed","rejected","error"].some(x=>s.includes(x))) return "red"; return ""; };
export function latestApprovalStatuses(approvals, subjectType) {
  const latest = new Map();
  const ordered = approvals
    .filter(item => item.subject_type === subjectType)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  for (const item of ordered) {
    if (!latest.has(item.subject_id)) latest.set(item.subject_id, item.status);
  }
  return latest;
}
export const badge = (status) => `<span class="badge ${statusTone(status)}"><span class="status-dot ${statusTone(status)==="green"?"healthy":statusTone(status)==="red"?"bad":""}"></span>${esc(status || "unknown")}</span>`;
export const emptyState = (title, text, icon="·") => `<div class="empty"><div class="empty-icon">${icon}</div><h3>${esc(title)}</h3><p>${esc(text)}</p></div>`;
export const panel = (title, body, meta="") => `<section class="panel"><div class="panel-head"><div><h2>${esc(title)}</h2>${meta?`<small>${esc(meta)}</small>`:""}</div></div>${body}</section>`;
export function executionFlow(execution) {
  const nodes = ["entry","router"];
  if(execution?.workflow){ nodes.push(execution.workflow.toLowerCase()==="marketing"?"marketing_worker":execution.workflow.toLowerCase()==="sales"?(execution.action==="follow_up_lead"?"sales_follow_up_worker":"sales_worker"):execution.action==="create_ticket_fix"?"tech_fix_worker":"tech_worker"); }
  if(execution?.steps?.some(s=>s.node==="approval_wait") || execution?.status==="waiting") nodes.push("approval_wait");
  if(execution?.status==="completed") nodes.push("complete");
  if(execution?.status==="failed") nodes.push("failed");
  const labels={entry:["ENTRY","Accepted"],router:["ROUTER","Decision"],marketing_worker:["MARKETING","Worker"],sales_worker:["SALES","Worker"],sales_follow_up_worker:["FOLLOW-UP","Worker"],tech_worker:["TECH","Worker"],tech_fix_worker:["TECH FIX","Worker"],approval_wait:["APPROVAL","Human gate"],complete:["COMPLETE","Finished"],failed:["FAILED","Error"]};
  const completed=new Set((execution?.steps||[]).filter(s=>s.status==="completed").map(s=>s.node));
  return `<div class="flow">${nodes.map((node,i)=>{const [label,sub]=labels[node]||[node,node]; const done=completed.has(node)||node==="complete"; const active=!done && node!="failed" && execution?.status!=="failed"; const cls=done?"done":node==="approval_wait"?"wait":active?"active":""; return `${i?`<span class="flow-arrow">›</span>`:""}<div class="flow-node ${cls}"><div class="node-icon">${done?"✓":node==="approval_wait"?"!":"•"}</div><strong>${label}</strong><small>${sub}</small></div>`}).join("")}</div>`;
}
export function timeline(steps=[]) { if(!steps.length) return emptyState("No execution steps yet","The workflow has not emitted any persisted node history.","≋"); return `<div class="timeline">${steps.map(step=>`<div class="timeline-item ${esc(step.status)}"><span class="timeline-dot"></span><div class="timeline-head"><strong>${esc(step.node)}</strong><small>${fmtDate(step.created_at)}</small></div><div class="timeline-meta">${badge(step.status)} <span class="mono">${shortId(step.step_id)}</span></div>${step.output_data?.error?`<div class="approval-preview">${esc(step.output_data.error)}</div>`:""}</div>`).join("")}</div>`; }
