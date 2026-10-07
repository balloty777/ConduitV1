import {api} from "../api.js";
import {state} from "../state.js";
import {badge,emptyState,esc,fmtDate,shortId} from "../components.js";

export async function renderApprovals(){
  const page=document.querySelector("#page");
  page.innerHTML=`<div class="page-head"><div><span class="eyebrow">HUMAN REVIEW</span><h1>Approvals</h1><p class="page-subtitle">Review generated content, Sales actions, tickets, and code. Rejecting asks for your correction and sends it back to the worker.</p></div></div><div id="approval-page" class="page-loading"><div class="loading-ring"></div></div>`;
  await load();
}

async function previewFor(approval){
  try{
    let item;
    switch(approval.subject_type){
      case "marketing_content":
        item=await api.contentOne(approval.subject_id);
        return `${item.platform} · ${item.tone}\nAudience: ${item.audience}\n\n${item.content}${item.call_to_action?`\n\nCall to action: ${item.call_to_action}`:""}`;
      case "sales_lead":
        item=await api.lead(approval.subject_id);
        return `${item.name}\n${item.email}${item.phone?` · ${item.phone}`:""}`;
      case "sales_follow_up":
        item=await api.followUp(approval.subject_id);
        return `To lead ${shortId(item.lead_id)} · ${item.channel}\n\n${item.message}`;
      case "tech_ticket":
        item=await api.ticket(approval.subject_id);
        return `${item.title} · ${item.category} · ${item.priority} priority\n\nProblem: ${item.description}\n\nProposed approach: ${item.proposed_fix}`;
      case "tech_ticket_fix":
        item=await api.fix(approval.subject_id);
        return `Generated code for ticket ${shortId(item.ticket_id)}:\n\n${item.proposed_fix}`;
      default:
        return approval.reason||"This item is ready for review.";
    }
  }catch(error){return `Could not load the item preview: ${error.message}`;}
}

async function load(){
  const target=document.querySelector("#approval-page");
  try{
    const approvals=await api.approvals();
    state.approvals=approvals;
    window.app.updateApprovalCount();
    const previews=await Promise.all(approvals.map(previewFor));
    target.className="";
    const pending=approvals.filter(item=>item.status==="pending").length;
    target.innerHTML=`<div class="filter-row" style="margin-bottom:13px"><span class="filter active">All ${approvals.length}</span><span class="filter">Waiting ${pending}</span><span class="filter">Resolved ${approvals.length-pending}</span></div>${approvals.length?`<div class="list-stack">${approvals.map((item,index)=>`<article class="list-card approval-card approval-card-clickable" data-open-approval="${item.approval_request_id}" tabindex="0" aria-label="Open ${esc(item.subject_type.replaceAll("_"," "))} approval details"><div class="approval-main"><div class="approval-title">${badge(item.status)}<strong>${esc(item.subject_type.replaceAll("_"," "))}</strong></div><div class="approval-meta"><span>Item ${shortId(item.subject_id)}</span><span>Project ${shortId(item.execution_id)}</span><span>${fmtDate(item.created_at)}</span></div><div class="approval-preview" style="max-height:220px;white-space:pre-wrap">${esc(previews[index])}</div>${item.status==="rejected"&&item.reason?`<div class="approval-meta" style="margin-top:8px">Correction: ${esc(item.reason)}</div>`:""}</div><div class="approval-actions">${item.status==="pending"?`<button class="button approve" data-approve="${item.approval_request_id}">Approve</button><button class="button reject" data-reject="${item.approval_request_id}">Reject and correct</button>`:`<button class="button" data-open-project="${item.execution_id}">Open project</button>`}</div></article>`).join("")}</div>`:emptyState("Nothing to review","When a workflow creates something for human review, it will appear here.","✓")}`;
    target.querySelectorAll("[data-open-approval]").forEach(card=>{
      card.onclick=event=>{
        if(event.target.closest("button,a")) return;
        openApproval(card.dataset.openApproval);
      };
      card.onkeydown=event=>{
        if((event.key==="Enter"||event.key===" ")&&event.target===card){
          event.preventDefault();
          openApproval(card.dataset.openApproval);
        }
      };
    });
    target.querySelectorAll("[data-approve]").forEach(button=>button.onclick=()=>decide(button.dataset.approve,"approve"));
    target.querySelectorAll("[data-reject]").forEach(button=>button.onclick=()=>window.app.openReject(button.dataset.reject));
    target.querySelectorAll("[data-open-project]").forEach(button=>button.onclick=()=>window.app.openExecution(button.dataset.openProject));
  }catch(error){target.className="";target.innerHTML=emptyState("Unable to load approvals",error.message,"!");}
}

function detailField(label,value){
  return `<div class="detail-item"><small>${esc(label)}</small><strong>${esc(value??"—")}</strong></div>`;
}

function detailBlock(label,value,code=false){
  const content=code?`<pre>${esc(value||"—")}</pre>`:esc(value||"—");
  return `<div style="margin-top:18px"><span class="eyebrow">${esc(label)}</span><div class="approval-preview${code?" code-view":""}" style="max-height:none;overflow:visible;white-space:pre-wrap">${content}</div></div>`;
}

async function openApproval(id){
  const approval=state.approvals.find(item=>item.approval_request_id===id);
  if(!approval) return;
  const subject=approval.subject_type.replaceAll("_"," ");
  window.app.openDrawer(`APPROVAL · ${approval.status.toUpperCase()}`,subject,`<div class="page-loading"><div class="loading-ring"></div></div>`);
  try{
    let item;
    let body="";
    switch(approval.subject_type){
      case "marketing_content":
        item=await api.contentOne(approval.subject_id);
        body=`<div class="detail-grid">${detailField("STATUS",item.status)}${detailField("PLATFORM",item.platform)}${detailField("TONE",item.tone)}${detailField("AUDIENCE",item.audience)}${detailField("CALL TO ACTION",item.call_to_action)}</div>${detailBlock("FULL CONTENT",item.content)}`;
        break;
      case "sales_lead":
        item=await api.lead(approval.subject_id);
        body=`<div class="detail-grid">${detailField("STATUS",item.status)}${detailField("NAME",item.name)}${detailField("EMAIL",item.email)}${detailField("PHONE",item.phone)}${detailField("LEAD ID",item.lead_id)}</div>`;
        break;
      case "sales_follow_up":
        item=await api.followUp(approval.subject_id);
        body=`<div class="detail-grid">${detailField("STATUS",item.status)}${detailField("CHANNEL",item.channel)}${detailField("LEAD ID",item.lead_id)}${detailField("SCHEDULED",fmtDate(item.scheduled_at))}</div>${detailBlock("FULL MESSAGE",item.message)}`;
        break;
      case "tech_ticket":
        item=await api.ticket(approval.subject_id);
        body=`<div class="detail-grid">${detailField("STATUS",item.status)}${detailField("CATEGORY",item.category)}${detailField("PRIORITY",item.priority)}${detailField("TICKET ID",item.ticket_id)}</div>${detailBlock("PROBLEM",item.description)}${detailBlock("PROPOSED APPROACH",item.proposed_fix,true)}`;
        break;
      case "tech_ticket_fix":
        item=await api.fix(approval.subject_id);
        body=`<div class="detail-grid">${detailField("STATUS",item.status)}${detailField("TICKET ID",item.ticket_id)}${detailField("FIX ID",item.fix_id)}</div>${detailBlock("FULL GENERATED CODE",item.proposed_fix,true)}`;
        break;
      default:
        body=detailBlock("APPROVAL DETAILS",approval.reason||"No additional details are available.");
    }
    body=`<div class="detail-grid">${detailField("PROJECT ID",approval.execution_id)}${detailField("CREATED",fmtDate(approval.created_at))}</div>${body}${approval.reason?detailBlock(approval.status==="rejected"?"CORRECTION":"REVIEW NOTE",approval.reason):""}`;
    document.querySelector("#drawer-body").innerHTML=body;
  }catch(error){
    document.querySelector("#drawer-body").innerHTML=detailBlock("DETAILS UNAVAILABLE",error.message);
  }
}

async function decide(id,type,reason=null){
  try{
    const approval=state.approvals.find(item=>item.approval_request_id===id);
    const userId=window.app.currentUserId()||(approval?(await api.execution(approval.execution_id)).user_id:window.app.operatorId());
    const result=type==="approve"?await api.approve(id,userId):await api.reject(id,userId,reason);
    window.app.toast(type==="approve"?"Approved":"Correction sent",result.status,"success");
    await load();
  }catch(error){window.app.toast(type==="approve"?"Approval failed":"Rejection failed",error.message,"error");}
}

export {decide};
