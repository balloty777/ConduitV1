export const state = {
  health: false,
  approvals: [],
  executions: [],
  content: [],
  leads: [],
  followUps: [],
  tickets: [],
  fixes: [],
  activeExecution: null,
  userId: localStorage.getItem("conduit_user_id") || null,
};

export function setUserId(id) {
  state.userId = id?.trim() || null;
  if (state.userId) localStorage.setItem("conduit_user_id", state.userId);
  else localStorage.removeItem("conduit_user_id");
}
