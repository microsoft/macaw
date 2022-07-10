interface Message {
  user_interface: string,
  user_id: string | number, // number as in integer
  text: string,
  timestamp: Date, // datetime.utcnow()
  user_info?: {[user_detail: string]: any},
  msg_info?: {[msg_detail: string]: any},
  actions: {
    [action: string]: string | {[action_var: string]: any}
  },
  dialog_state_tracking: {
    state: string,
    [dialog_state_tracking_var: string]: string
  },
  nlp_pipeline: {
    [module: string]: {[module_var: string]: any}
  }
  user_attributes: {
    [attribute: string]: any
  }
}