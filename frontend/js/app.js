import {api} from "./api.js";
import {state,setUserId} from "./state.js";
import {esc,executionFlow,shortId} from "./components.js";
import {renderApprovals} from "./views/approvals.js";
import {renderExecutions,openExecution} from "./views/executions.js";
import {renderMarketing} from "./views/marketing.js";
import {renderSales} from "./views/sales.js";
import {renderTech} from "./views/tech.js";

const pageNames={"/projects":"Previous Projects","/executions":"Previous Projects","/approvals":"Approvals","/marketing":"Marketing","/sales":"Sales","/tech":"Tech"};
let executionTimer=null;

function route(){
  const raw=location.hash.replace(/^#/ ,"")||"/projects";
  const parts=raw.split("/").filter(Boolean);
  return {path:parts.length?`/${parts[0]}`:"/",id:parts[1]||null};
}

async function render(){
  const current=route();
  const base=current.path;
  document.querySelector("#page-name").textContent=pageNames[base]||"Execution Detail";
  document.querySelectorAll(".nav a").forEach(link=>link.classList.toggle("active",link.dataset.route===base));
  window.scrollTo({top:0,behavior:"smooth"});
  try{
    if(current.path==="/projects"||current.path==="/executions"){
      if(current.id){
        document.querySelector("#page").innerHTML=`<div class="page-head"><div><span class="eyebrow">PREVIOUS PROJECT</span><h1>${shortId(current.id)}</h1><p class="page-subtitle">Loading saved workflow history…</p></div></div><div class="page-loading"><div class="loading-ring"></div></div>`;
        await openExecution(current.id);
      }else await renderExecutions();
    }
    else if(current.path==="/approvals") await renderApprovals();
    else if(current.path==="/marketing") await renderMarketing();
    else if(current.path==="/sales") await renderSales();
    else if(current.path==="/tech") await renderTech();
    else window.location.hash="#/projects";
  }catch(error){
    window.app.toast("Page error",error.message,"error");
  }
}

function toast(title,detail="",kind="success"){
  const element=document.createElement("div");
  element.className=`toast ${kind}`;
  element.innerHTML=`<strong>${esc(title)}</strong>${detail?`<small>${esc(detail)}</small>`:""}`;
  document.querySelector("#toast-region").appendChild(element);
  setTimeout(()=>element.remove(),4500);
}

function openDrawer(kicker,title,body){
  const drawer=document.querySelector("#drawer");
  document.querySelector("#drawer-kicker").textContent=kicker;
  document.querySelector("#drawer-title").textContent=title;
  document.querySelector("#drawer-body").innerHTML=body;
  drawer.classList.remove("hidden");
  drawer.setAttribute("aria-hidden","false");
}

function closeDrawer(){
  const drawer=document.querySelector("#drawer");
  drawer.classList.add("hidden");
  drawer.setAttribute("aria-hidden","true");
}

function openModal(title,body){
  const modal=document.querySelector("#modal");
  document.querySelector("#modal-title").textContent=title;
  document.querySelector("#modal-body").innerHTML=body;
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden","false");
}

function closeModal(){
  const modal=document.querySelector("#modal");
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden","true");
}

function openReject(id){
  openModal("Reject and regenerate",`<p class="page-subtitle" style="margin-bottom:12px">Give the workflow useful feedback. The rejection reason is passed back into the real LangGraph state for regeneration.</p><textarea id="reject-reason" placeholder="Tell the workflow what needs to change…"></textarea><div class="modal-footer"><button class="button" id="reject-cancel">Cancel</button><button class="button reject" id="reject-submit">Reject and Regenerate</button></div>`);
  document.querySelector("#reject-cancel").onclick=closeModal;
  document.querySelector("#reject-submit").onclick=async()=>{
    const reason=document.querySelector("#reject-reason").value.trim();
    if(!reason) return toast("Feedback required","Tell the workflow what needs to change.","error");
    try{
      const {decide}=await import("./views/approvals.js");
      await decide(id,"reject",reason);
      closeModal();
    }catch(error){toast("Rejection failed",error.message,"error");}
  };
}

function currentUserId(){return state.userId;}
function operatorId(){
  if(state.userId) return state.userId;
  const id=prompt("Operator user ID (optional). Leave blank to use the backend's default operator.");
  if(id){setUserId(id);return id;}
  return null;
}
function updateApprovalCount(){
  const count=document.querySelector("#approval-count");
  const pending=state.approvals.filter(approval=>approval.status==="pending").length;
  count.textContent=pending;
  count.classList.toggle("hidden",pending===0);
}
async function refreshHealth(){
  try{
    await api.health();
    state.health=true;
    document.querySelector("#sidebar-health").textContent="Healthy";
    document.querySelector("#top-health").textContent="API healthy";
    document.querySelector("#top-health-dot").classList.add("healthy");
    document.querySelector("#top-health-dot").classList.remove("bad");
  }catch{
    state.health=false;
    document.querySelector("#sidebar-health").textContent="Offline";
    document.querySelector("#top-health").textContent="API offline";
    document.querySelector("#top-health-dot").classList.add("bad");
    document.querySelector("#top-health-dot").classList.remove("healthy");
  }
}
function watchExecution(id){
  clearTimeout(executionTimer);
  const tick=async()=>{
    try{
      const execution=await api.execution(id);
      if(!["running","waiting"].includes(execution.status)){
        clearTimeout(executionTimer);
        toast("Execution updated",`${shortId(id)} is ${execution.status}.`);
        return;
      }
      executionTimer=setTimeout(tick,7000);
    }catch{executionTimer=setTimeout(tick,10000);}
  };
  executionTimer=setTimeout(tick,5000);
}

window.app={toast,openDrawer,closeDrawer,openExecution,openReject,flow:executionFlow,operatorId,currentUserId,updateApprovalCount,watchExecution};

document.querySelector("#drawer-close").onclick=closeDrawer;
document.querySelector("#modal-close").onclick=closeModal;
document.querySelector("#drawer").addEventListener("click",event=>{
  if(event.target.id==="drawer") closeDrawer();
});
document.querySelector("#modal").addEventListener("click",event=>{
  if(event.target.id==="modal") closeModal();
});
document.addEventListener("keydown",event=>{
  if(event.key==="Escape"){
    closeDrawer();
    closeModal();
  }
});
document.querySelector("#mobile-menu").onclick=()=>document.querySelector("#sidebar").classList.toggle("open");
document.querySelectorAll(".nav a").forEach(link=>link.addEventListener("click",event=>{
  event.preventDefault();
  document.querySelector("#sidebar").classList.remove("open");
  const nextHash=link.getAttribute("href");
  if(location.hash===nextHash) render();
  else location.hash=nextHash;
}));
document.querySelector("#settings-button").onclick=()=>{
  openModal(
    "Operator settings",
    `<p class="page-subtitle">Login is not required. Set an operator ID only if you already have a user ID in the database.</p><div style="margin-top:16px"><span class="eyebrow">OPERATOR USER ID</span><input id="operator-id-input" value="${esc(state.userId||"")}" placeholder="UUID (optional)" style="width:100%;margin-top:7px;border:1px solid #30343d;background:#0a0c0f;color:#eee;border-radius:10px;padding:11px;outline:none"></div><div class="modal-footer"><button class="button" id="operator-clear">Clear</button><button class="button blue" id="operator-save">Save</button></div>`,
  );
  document.querySelector("#operator-save").onclick=()=>{
    setUserId(document.querySelector("#operator-id-input").value);
    closeModal();
    toast("Operator settings saved","Local browser preference updated.");
  };
  document.querySelector("#operator-clear").onclick=()=>{
    setUserId(null);
    closeModal();
    toast("Operator ID cleared");
  };
};

window.addEventListener("hashchange",render);
if(!location.hash) location.hash="#/projects";
refreshHealth();
render();
setInterval(refreshHealth,30000);
