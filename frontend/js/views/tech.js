import {api} from "../api.js";
import {state} from "../state.js";
import {badge,emptyState,esc,fmtDate,shortId} from "../components.js";

export async function renderTech(){
  const page=document.querySelector("#page");
  page.innerHTML=`
    <div class="page-head"><div><span class="eyebrow">WORKFLOW · TECH</span><h1>Tech</h1><p class="page-subtitle">Describe the problem and include code or an error if you have it. Approving the ticket starts the Tech Fix worker; its generated code then waits for your approval or correction.</p></div></div>
    <section class="panel create-panel"><div class="panel-head"><div><h2>Create a technical ticket</h2><small>Problem details and code context help the worker propose a concrete fix.</small></div></div>
      <form id="ticket-form" class="form-grid">
        <label class="form-field form-wide">What is broken?<textarea name="problem" required rows="4" placeholder="Describe what happens, what you expected, and how to reproduce it…"></textarea></label>
        <label class="form-field form-wide">Relevant code, error, or logs<textarea name="code" rows="5" placeholder="Paste code or an error trace if available"></textarea></label>
        <div class="form-actions form-wide"><button class="primary" type="submit">Create ticket</button><span class="subtle">After ticket approval, Conduit generates code for review.</span></div>
      </form>
    </section>
    <div class="split" style="margin-top:16px"><div>${panel("Tickets",`<div id="tech-tickets" class="page-loading"><div class="loading-ring"></div></div>`)}</div><div>${panel("Generated code fixes",`<div id="tech-fixes" class="page-loading"><div class="loading-ring"></div></div>`)}</div></div>`;
  document.querySelector("#ticket-form").onsubmit=createTicket;
  await load();
}

async function createTicket(event){
  event.preventDefault();
  const form=event.currentTarget;
  const fields=Object.fromEntries(new FormData(form));
  const button=form.querySelector("[type=submit]");
  button.disabled=true;
  try{
    const request=`Create a technical support ticket for this problem: ${fields.problem}${fields.code.trim()?`\nRelevant code, error, or logs:\n${fields.code}`:""}`;
    const execution=await api.launch(request,state.userId);
    window.app.toast("Ticket creation started",`Project ${shortId(execution.execution_id)} is running.`);
    window.location.hash=`#/projects/${execution.execution_id}`;
  }catch(error){window.app.toast("Could not create ticket",error.message,"error");}
  finally{button.disabled=false;}
}

async function load(){
  const ticketTarget=document.querySelector("#tech-tickets");
  const fixTarget=document.querySelector("#tech-fixes");
  try{
    const [tickets,fixes]=await Promise.all([api.tickets(),api.fixes()]);
    state.tickets=tickets;
    state.fixes=fixes;
    ticketTarget.className="";
    ticketTarget.innerHTML=tickets.length?`<div class="list-stack">${tickets.map(ticket=>`<article class="list-card"><div class="list-card-head"><div><h3>${esc(ticket.title)}</h3><p>${esc(ticket.category)} · Priority ${esc(ticket.priority)}</p></div>${badge(ticket.status)}</div><div class="approval-preview">${esc(ticket.description)}</div><div class="action-row" style="margin-top:11px"><button class="button" data-ticket="${ticket.ticket_id}">Open ticket</button><button class="button blue" data-fix="${ticket.ticket_id}">Request code fix</button><span class="subtle" style="margin-left:auto">${shortId(ticket.ticket_id)}</span></div></article>`).join("")}</div>`:emptyState("No tickets yet","Describe a problem in the form above to create a ticket.","⌘");
    fixTarget.className="";
    fixTarget.innerHTML=fixes.length?`<div class="list-stack">${fixes.map(fix=>`<article class="list-card"><div class="list-card-head"><div><h3>Fix ${shortId(fix.fix_id)}</h3><p>Ticket ${shortId(fix.ticket_id)}</p></div>${badge(fix.status)}</div><div class="code-view" style="margin-top:10px"><div class="code-toolbar"><span>PROPOSED CODE</span><span>${fmtDate(fix.updated_at)}</span></div><pre>${esc(fix.proposed_fix)}</pre></div><div class="action-row" style="margin-top:10px"><button class="button" data-open-fix="${fix.fix_id}">Open fix</button></div></article>`).join("")}</div>`:emptyState("No code fixes yet","Approving a Tech ticket starts the Tech Fix worker.","⌘");
    ticketTarget.querySelectorAll("[data-ticket]").forEach(button=>button.onclick=()=>openTicket(button.dataset.ticket));
    ticketTarget.querySelectorAll("[data-fix]").forEach(button=>button.onclick=()=>generateFix(button.dataset.fix));
    fixTarget.querySelectorAll("[data-open-fix]").forEach(button=>button.onclick=()=>openFix(button.dataset.openFix));
  }catch(error){
    for(const target of [ticketTarget,fixTarget]){target.className="";target.innerHTML=emptyState("Unable to load Tech",error.message,"!");}
  }
}

function panel(title,body){return `<section class="panel"><div class="panel-head"><h2>${esc(title)}</h2></div><div class="panel-body">${body}</div></section>`;}

async function openTicket(id){
  const ticket=await api.ticket(id);
  window.app.openDrawer("TECH TICKET",ticket.title,`<div class="detail-grid"><div class="detail-item"><small>TICKET ID</small><strong class="mono">${esc(ticket.ticket_id)}</strong></div><div class="detail-item"><small>CATEGORY</small><strong>${esc(ticket.category)}</strong></div><div class="detail-item"><small>PRIORITY</small><strong>${esc(ticket.priority)}</strong></div><div class="detail-item"><small>STATUS</small><strong>${badge(ticket.status)}</strong></div></div><div style="margin-top:18px"><span class="eyebrow">PROBLEM</span><div class="approval-preview" style="max-height:none">${esc(ticket.description)}</div></div><div style="margin-top:18px"><span class="eyebrow">PROPOSED APPROACH</span><div class="code-view" style="margin-top:7px"><pre>${esc(ticket.proposed_fix)}</pre></div></div><div class="subtle" style="margin-top:12px">Approve the ticket in Approvals to generate a code fix.</div>`);
}

async function openFix(id){
  const fix=await api.fix(id);
  window.app.openDrawer("TECH FIX",`Fix ${shortId(id)}`,`<div class="detail-grid"><div class="detail-item"><small>FIX ID</small><strong class="mono">${esc(fix.fix_id)}</strong></div><div class="detail-item"><small>TICKET</small><strong class="mono">${esc(fix.ticket_id)}</strong></div><div class="detail-item"><small>STATUS</small><strong>${badge(fix.status)}</strong></div><div class="detail-item"><small>PROJECT</small><strong class="mono">${esc(fix.execution_id)}</strong></div></div><div style="margin-top:18px"><span class="eyebrow">GENERATED CODE</span><div class="code-view" style="margin-top:7px"><pre>${esc(fix.proposed_fix)}</pre></div></div>`);
}

async function generateFix(ticketId){
  const request=`Fix the existing technical support ticket id ${ticketId}. Generate corrected code for the issue described in that ticket.`;
  try{
    const execution=await api.launch(request,state.userId);
    window.app.toast("Fix generation started",`Project ${shortId(execution.execution_id)} is running.`);
    window.location.hash=`#/projects/${execution.execution_id}`;
  }catch(error){window.app.toast("Could not start fix",error.message,"error");}
}
