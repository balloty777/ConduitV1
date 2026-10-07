import {api} from "../api.js";
import {state} from "../state.js";
import {badge,emptyState,esc,fmtDate,latestApprovalStatuses,shortId} from "../components.js";

export async function renderSales(){
  const page=document.querySelector("#page");
  page.innerHTML=`
    <div class="page-head"><div><span class="eyebrow">WORKFLOW · SALES</span><h1>Sales</h1><p class="page-subtitle">Add a lead or draft a follow-up for an existing lead. Follow-up messages go through approval before scheduling.</p></div></div>
    <div class="split form-split">
      <section class="panel"><div class="panel-head"><div><h2>Add a lead</h2><small>Conduit creates the lead from these details.</small></div></div>
        <form id="lead-form" class="form-grid single-column">
          <label class="form-field">Name<input name="name" required placeholder="Full name"></label>
          <label class="form-field">Email<input name="email" type="email" required placeholder="name@company.com"></label>
          <label class="form-field">Phone<input name="phone" type="tel" placeholder="Optional"></label>
          <div class="form-actions"><button class="primary" type="submit">Create lead</button></div>
        </form>
      </section>
      <section class="panel"><div class="panel-head"><div><h2>Follow up</h2><small>Select a saved lead and tell Conduit what to cover.</small></div></div>
        <form id="follow-up-form" class="form-grid single-column">
          <label class="form-field">Lead<select name="lead_id" id="follow-up-lead" required><option value="">Loading leads…</option></select></label>
          <label class="form-field">Follow-up instructions<textarea name="instructions" rows="3" required placeholder="What should the message cover?"></textarea></label>
          <div class="form-actions"><button class="primary" type="submit">Draft follow-up</button></div>
        </form>
      </section>
    </div>
    <div class="split" style="margin-top:16px"><div>${panel("Leads",`<div id="sales-leads" class="page-loading"><div class="loading-ring"></div></div>`)}</div><div>${panel("Follow-ups",`<div id="sales-follow-ups" class="page-loading"><div class="loading-ring"></div></div>`)}</div></div>`;
  document.querySelector("#lead-form").onsubmit=createLead;
  document.querySelector("#follow-up-form").onsubmit=createFollowUp;
  await load();
}

async function createLead(event){
  event.preventDefault();
  const form=event.currentTarget;
  const value=Object.fromEntries(new FormData(form));
  const button=form.querySelector("[type=submit]");
  button.disabled=true;
  try{
    const request=`Create a new sales lead named ${value.name}, with email ${value.email}${value.phone?` and phone ${value.phone}`:""}.`;
    const execution=await api.launch(request,state.userId);
    window.app.toast("Lead creation started",`Project ${shortId(execution.execution_id)} is running.`);
    window.location.hash=`#/projects/${execution.execution_id}`;
  }catch(error){window.app.toast("Could not create lead",error.message,"error");}
  finally{button.disabled=false;}
}

async function createFollowUp(event){
  event.preventDefault();
  const form=event.currentTarget;
  const value=Object.fromEntries(new FormData(form));
  if(!value.lead_id)return window.app.toast("Choose a lead first","A saved lead is required to create a follow-up.","error");
  const button=form.querySelector("[type=submit]");
  button.disabled=true;
  try{
    const lead=state.leads.find(item=>item.lead_id===value.lead_id);
    const request=`Follow up with existing sales lead id ${value.lead_id}${lead?` (${lead.name}, ${lead.email})`:""}. Follow-up instructions: ${value.instructions}`;
    const execution=await api.launch(request,state.userId);
    window.app.toast("Follow-up draft started",`Project ${shortId(execution.execution_id)} is running.`);
    window.location.hash=`#/projects/${execution.execution_id}`;
  }catch(error){window.app.toast("Could not draft follow-up",error.message,"error");}
  finally{button.disabled=false;}
}

async function load(){
  const leadTarget=document.querySelector("#sales-leads");
  const followTarget=document.querySelector("#sales-follow-ups");
  try{
    const [leads,followUps,approvals]=await Promise.all([api.leads(),api.followUps(),api.approvals()]);
    state.leads=leads;
    state.followUps=followUps;
    const followUpApprovalStatus=latestApprovalStatuses(approvals,"sales_follow_up");
    const select=document.querySelector("#follow-up-lead");
    const previous=select.value;
    select.innerHTML=`<option value="">Select a lead…</option>${leads.map(lead=>`<option value="${lead.lead_id}">${esc(lead.name)} · ${esc(lead.email)}</option>`).join("")}`;
    if(leads.some(lead=>lead.lead_id===previous))select.value=previous;
    leadTarget.className="";
    leadTarget.innerHTML=leads.length?`<div class="list-stack">${leads.map(lead=>`<article class="list-card"><div class="list-card-head"><div><h3>${esc(lead.name)}</h3><p>${esc(lead.email)}${lead.phone?` · ${esc(lead.phone)}`:""}</p></div>${badge(lead.status)}</div><div class="action-row" style="margin-top:10px"><button class="button" data-lead="${lead.lead_id}">Open lead</button><span class="subtle" style="margin-left:auto">${shortId(lead.lead_id)} · ${fmtDate(lead.created_at)}</span></div></article>`).join("")}</div>`:emptyState("No leads yet","Add a lead using the form above.","◎");
    followTarget.className="";
    followTarget.innerHTML=followUps.length?`<div class="list-stack">${followUps.map(item=>{
      const approved=followUpApprovalStatus.get(item.follow_up_id)==="approved";
      const displayStatus=item.scheduled_at?"scheduled":approved?"approved":item.status;
      return `<article class="list-card"><div class="list-card-head"><div><h3>${esc(item.channel)} follow-up</h3><p>${esc(item.message)}</p></div>${badge(displayStatus)}</div><div class="action-row" style="margin-top:10px"><button class="button" data-follow="${item.follow_up_id}">Open</button>${approved&&!item.scheduled_at?`<button class="button blue" data-schedule="${item.follow_up_id}">Schedule</button>`:""}<span class="subtle" style="margin-left:auto">Lead ${shortId(item.lead_id)}${item.scheduled_at?` · ${fmtDate(item.scheduled_at)}`:""}</span></div></article>`;
    }).join("")}</div>`:emptyState("No follow-ups yet","Choose a lead above to draft a follow-up.","◎");
    leadTarget.querySelectorAll("[data-lead]").forEach(button=>button.onclick=()=>openLead(button.dataset.lead));
    followTarget.querySelectorAll("[data-follow]").forEach(button=>button.onclick=()=>openFollow(button.dataset.follow));
    followTarget.querySelectorAll("[data-schedule]").forEach(button=>button.onclick=()=>schedule(button.dataset.schedule));
  }catch(error){
    for(const target of [leadTarget,followTarget]){target.className="";target.innerHTML=emptyState("Unable to load Sales",error.message,"!");}
  }
}

function panel(title,body){return `<section class="panel"><div class="panel-head"><h2>${esc(title)}</h2></div><div class="panel-body">${body}</div></section>`;}

async function openLead(id){
  const lead=await api.lead(id);
  window.app.openDrawer("SALES LEAD",lead.name,`<div class="detail-grid"><div class="detail-item"><small>EMAIL</small><strong>${esc(lead.email)}</strong></div><div class="detail-item"><small>PHONE</small><strong>${esc(lead.phone||"—")}</strong></div><div class="detail-item"><small>STATUS</small><strong>${badge(lead.status)}</strong></div><div class="detail-item"><small>PROJECT</small><strong class="mono">${esc(lead.execution_id)}</strong></div></div>`);
}

async function openFollow(id){
  const item=await api.followUp(id);
  window.app.openDrawer("SALES FOLLOW-UP",`Follow-up ${shortId(id)}`,`<div class="detail-grid"><div class="detail-item"><small>CHANNEL</small><strong>${esc(item.channel)}</strong></div><div class="detail-item"><small>STATUS</small><strong>${badge(item.status)}</strong></div><div class="detail-item"><small>LEAD</small><strong class="mono">${esc(item.lead_id)}</strong></div><div class="detail-item"><small>SCHEDULED</small><strong>${fmtDate(item.scheduled_at)}</strong></div></div><div style="margin-top:18px"><span class="eyebrow">MESSAGE</span><div class="approval-preview" style="max-height:none">${esc(item.message)}</div></div>`);
}

async function schedule(id){
  const value=prompt("Schedule time (ISO format, e.g. 2026-10-08T10:00:00+05:30)");
  if(!value)return;
  try{await api.scheduleFollowUp(id,value);window.app.toast("Follow-up scheduled","The schedule was saved.");await load();}
  catch(error){window.app.toast("Scheduling failed",error.message,"error");}
}
