import { rankingService } from '../../services/ranking';

const initialState = {
  currentPlayer: null,
  playerDetail: null,
  isLoading: false,
  error: null
};

const playerReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'PLAYER_FETCH_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case 'PLAYER_FETCH_SUCCESS':
      return {
        ...state,
        playerDetail: action.payload,
        isLoading: false
      };

    case 'PLAYER_FETCH_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload
      };

    case 'PLAYER_SET_CURRENT':
      return {
        ...state,
        currentPlayer: action.payload
      };

    case 'PLAYER_CLEAR':
      return {
        ...state,
        playerDetail: null,
        currentPlayer: null
      };

    default:
      return state;
  }
};

// Actions
export const fetchPlayerDetail = (playerName) => async (dispatch) => {
  dispatch({ type: 'PLAYER_FETCH_REQUEST' });
  
  try {
    const response = await rankingService.getPlayerDetail(playerName);
    dispatch({
      type: 'PLAYER_FETCH_SUCCESS',
      payload: response
    });
  } catch (error) {
    dispatch({
      type: 'PLAYER_FETCH_FAILURE',
      payload: error.message
    });
  }
};

export const setCurrentPlayer = (player) => (dispatch) => {
  dispatch({
    type: 'PLAYER_SET_CURRENT',
    payload: player
  });
};

export const clearPlayerDetail = () => (dispatch) => {
  dispatch({ type: 'PLAYER_CLEAR' });
};

export default playerReducer;
