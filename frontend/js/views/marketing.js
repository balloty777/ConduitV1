import {api} from "../api.js";
import {state} from "../state.js";
import {badge,emptyState,esc,fmtDate,latestApprovalStatuses,shortId} from "../components.js";

export async function renderMarketing(){
  const page=document.querySelector("#page");
  page.innerHTML=`
    <div class="page-head"><div><span class="eyebrow">WORKFLOW · MARKETING</span><h1>Marketing</h1><p class="page-subtitle">Describe the content you need. Conduit drafts it, then sends it to Approvals for review and revision.</p></div></div>
    <section class="panel create-panel"><div class="panel-head"><div><h2>Create content</h2><small>Your brief goes to the Marketing worker.</small></div></div>
      <form id="marketing-form" class="form-grid">
        <label class="form-field form-wide">Content brief<textarea name="brief" required rows="4" placeholder="What should the post say? Include the product, audience, and goal…"></textarea></label>
        <label class="form-field">Platform<select name="platform"><option>LinkedIn</option><option>Instagram</option><option>X</option><option>Facebook</option></select></label>
        <label class="form-field">Audience<input name="audience" placeholder="e.g. startup founders"></label>
        <label class="form-field">Tone<input name="tone" placeholder="e.g. clear and confident"></label>
        <label class="form-field">Call to action<input name="cta" placeholder="Optional"></label>
        <div class="form-actions form-wide"><button class="primary" type="submit">Generate draft</button><span class="subtle">You’ll review or reject the generated draft in Approvals.</span></div>
      </form>
    </section>
    <div class="section-title"><div><span class="eyebrow">SAVED WORK</span><h2>Generated content</h2></div></div>
    <div id="marketing-page" class="page-loading"><div class="loading-ring"></div></div>`;
  document.querySelector("#marketing-form").onsubmit=createContent;
  await load();
}

async function createContent(event){
  event.preventDefault();
  const form=event.currentTarget;
  const values=Object.fromEntries(new FormData(form));
  const button=form.querySelector("[type=submit]");
  button.disabled=true;
  button.textContent="Starting…";
  try{
    const brief=`Create marketing content for ${values.platform}. Audience: ${values.audience||"as described in the brief"}. Tone: ${values.tone||"appropriate to the brief"}. Call to action: ${values.cta||"none specified"}. Brief: ${values.brief}`;
    const execution=await api.launch(brief,state.userId);
    window.app.toast("Draft generation started",`Project ${shortId(execution.execution_id)} is running.`);
    window.location.hash=`#/projects/${execution.execution_id}`;
  }catch(error){window.app.toast("Could not start draft",error.message,"error");}
  finally{button.disabled=false;button.textContent="Generate draft";}
}

async function load(){
  const target=document.querySelector("#marketing-page");
  try{
    const [content,approvals]=await Promise.all([api.content(),api.approvals()]);
    state.content=content;
    const contentApprovalStatus=latestApprovalStatuses(approvals,"marketing_content");
    target.className="";
    target.innerHTML=content.length?`<div class="list-stack">${content.map(item=>{
      const approved=contentApprovalStatus.get(item.content_id)==="approved";
      const displayStatus=item.scheduled_at?"scheduled":approved?"approved":item.status;
      return `<article class="list-card"><div class="list-card-head"><div><h3>${esc(item.platform)} · ${esc(item.tone)}</h3><p>${esc(item.audience)}${item.call_to_action?` · CTA: ${esc(item.call_to_action)}`:""}</p></div>${badge(displayStatus)}</div><div class="approval-preview">${esc(item.content)}</div><div class="action-row" style="margin-top:11px"><button class="button" data-open="${item.content_id}">Open content</button>${approved&&!item.scheduled_at?`<button class="button blue" data-schedule="${item.content_id}">Schedule</button>`:""}<span class="subtle" style="margin-left:auto">${item.scheduled_at?`Scheduled ${fmtDate(item.scheduled_at)}`:`Project ${shortId(item.execution_id)}`}</span></div></article>`;
    }).join("")}</div>`:emptyState("No content yet","Use the form above to generate your first marketing draft.","✦");
    target.querySelectorAll("[data-open]").forEach(button=>button.onclick=()=>openContent(button.dataset.open));
    target.querySelectorAll("[data-schedule]").forEach(button=>button.onclick=()=>schedule(button.dataset.schedule));
  }catch(error){target.className="";target.innerHTML=emptyState("Unable to load marketing",error.message,"!");}
}

async function openContent(id){
  const content=await api.contentOne(id);
  window.app.openDrawer("MARKETING CONTENT",`Content ${shortId(id)}`,`<div class="detail-grid"><div class="detail-item"><small>PLATFORM</small><strong>${esc(content.platform)}</strong></div><div class="detail-item"><small>STATUS</small><strong>${badge(content.status)}</strong></div><div class="detail-item"><small>TONE</small><strong>${esc(content.tone)}</strong></div><div class="detail-item"><small>AUDIENCE</small><strong>${esc(content.audience)}</strong></div></div><div style="margin:20px 0 8px"><span class="eyebrow">GENERATED CONTENT</span></div><div class="approval-preview" style="max-height:none">${esc(content.content)}</div>${content.call_to_action?`<div style="margin-top:13px"><span class="eyebrow">CALL TO ACTION</span><div class="approval-preview">${esc(content.call_to_action)}</div></div>`:""}`);
}

async function schedule(id){
  const value=prompt("Schedule time (ISO format, e.g. 2026-10-07T10:00:00+05:30)");
  if(!value)return;
  try{await api.scheduleContent(id,value);window.app.toast("Content scheduled","The backend accepted the schedule.");await load();}
  catch(error){window.app.toast("Scheduling failed",error.message,"error");}
}
