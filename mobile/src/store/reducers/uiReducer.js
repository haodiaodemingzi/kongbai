const initialState = {
  activeTab: 'home',
  modalVisible: false,
  refreshing: false,
  toastMessage: null,
  loading: false
};

const uiReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'UI_SET_ACTIVE_TAB':
      return {
        ...state,
        activeTab: action.payload
      };

    case 'UI_SET_MODAL_VISIBLE':
      return {
        ...state,
        modalVisible: action.payload
      };

    case 'UI_SET_REFRESHING':
      return {
        ...state,
        refreshing: action.payload
      };

    case 'UI_SHOW_TOAST':
      return {
        ...state,
        toastMessage: action.payload
      };

    case 'UI_HIDE_TOAST':
      return {
        ...state,
        toastMessage: null
      };

    case 'UI_SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };

    default:
      return state;
  }
};

// Actions
export const setActiveTab = (tab) => (dispatch) => {
  dispatch({
    type: 'UI_SET_ACTIVE_TAB',
    payload: tab
  });
};

export const setModalVisible = (visible) => (dispatch) => {
  dispatch({
    type: 'UI_SET_MODAL_VISIBLE',
    payload: visible
  });
};

export const setRefreshing = (refreshing) => (dispatch) => {
  dispatch({
    type: 'UI_SET_REFRESHING',
    payload: refreshing
  });
};

export const showToast = (message) => (dispatch) => {
  dispatch({
    type: 'UI_SHOW_TOAST',
    payload: message
  });
  
  setTimeout(() => {
    dispatch({ type: 'UI_HIDE_TOAST' });
  }, 3000);
};

export const setLoading = (loading) => (dispatch) => {
  dispatch({
    type: 'UI_SET_LOADING',
    payload: loading
  });
};

export default uiReducer;
