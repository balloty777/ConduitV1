const jsonHeaders = {"Content-Type":"application/json"};

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout ?? 15000);
  try {
    const response = await fetch(path, {
      ...options,
      signal: controller.signal,
      headers: {...(options.body ? jsonHeaders : {}), ...(options.headers || {})},
    });
    const text = await response.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!response.ok) {
      const detail = data?.detail || data?.message || `Request failed (${response.status})`;
      throw new Error(detail);
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("The request timed out. Check that the Conduit API is responsive.");
    if (error instanceof TypeError) throw new Error("Unable to reach the Conduit API. Check that the server is running.");
    throw error;
  } finally { clearTimeout(timeout); }
}

export const api = {
  health: () => request("/health"),
  launch: (requestText, userId = null) => request("/executions", {method:"POST", body:JSON.stringify({request:requestText, ...(userId ? {user_id:userId} : {})})}),
  executions: (params = "") => request(`/executions${params ? `?${params}` : ""}`),
  execution: (id) => request(`/executions/${id}`),
  approvals: (status = "") => request(`/approvals${status ? `?status=${encodeURIComponent(status)}` : ""}`),
  approve: (id, userId) => request(`/approvals/${id}/approve`, {method:"POST", body:JSON.stringify({user_id:userId})}),
  reject: (id, userId, reason) => request(`/approvals/${id}/reject`, {method:"POST", body:JSON.stringify({user_id:userId, reason})}),
  content: () => request("/marketing/content"),
  contentOne: (id) => request(`/marketing/content/${id}`),
  scheduleContent: (id, scheduledAt) => request(`/marketing/content/${id}/schedule`, {method:"POST", body:JSON.stringify({scheduled_at:scheduledAt})}),
  leads: () => request("/sales/leads"),
  lead: (id) => request(`/sales/leads/${id}`),
  followUps: () => request("/sales/follow-ups"),
  followUp: (id) => request(`/sales/follow-ups/${id}`),
  scheduleFollowUp: (id, scheduledAt) => request(`/sales/leads/follow-up/${id}/schedule`, {method:"POST", body:JSON.stringify({scheduled_at:scheduledAt})}),
  tickets: () => request("/tech/tickets"),
  ticket: (id) => request(`/tech/tickets/${id}`),
  fixes: () => request("/tech/fixes"),
  fix: (id) => request(`/tech/fixes/${id}`),
  generateFix: (ticketId, executionId, proposedFix) => request(`/tech/tickets/${ticketId}/fix`, {method:"POST", body:JSON.stringify({ticket_id:ticketId, execution_id:executionId, proposed_fix:proposedFix})}),
};
