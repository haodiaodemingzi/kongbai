import { rankingService } from '../../services/ranking';

const initialState = {
  players: [],
  factionStats: null,
  selectedFaction: 'all',
  selectedJob: null,
  selectedTimeRange: 'week',
  isLoading: false,
  error: null,
  lastUpdated: null
};

const rankingReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'RANKING_FETCH_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case 'RANKING_FETCH_SUCCESS':
      return {
        ...state,
        players: action.payload,
        isLoading: false,
        lastUpdated: new Date()
      };

    case 'RANKING_FETCH_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload
      };

    case 'RANKING_SET_FILTER':
      return {
        ...state,
        selectedFaction: action.payload.faction || state.selectedFaction,
        selectedJob: action.payload.job !== undefined ? action.payload.job : state.selectedJob,
        selectedTimeRange: action.payload.timeRange || state.selectedTimeRange
      };

    case 'FACTION_STATS_SUCCESS':
      return {
        ...state,
        factionStats: action.payload
      };

    default:
      return state;
  }
};

// Actions
export const fetchPlayerRankings = (faction, timeRange, job) => async (dispatch) => {
  dispatch({ type: 'RANKING_FETCH_REQUEST' });
  
  try {
    const response = await rankingService.getPlayerRankings(faction, timeRange, job);
    dispatch({
      type: 'RANKING_FETCH_SUCCESS',
      payload: response
    });
  } catch (error) {
    dispatch({
      type: 'RANKING_FETCH_FAILURE',
      payload: error.message
    });
  }
};

export const setRankingFilter = (faction, job, timeRange) => (dispatch) => {
  dispatch({
    type: 'RANKING_SET_FILTER',
    payload: { faction, job, timeRange }
  });
};

export const fetchFactionStats = (dateRange) => async (dispatch) => {
  try {
    const response = await rankingService.getFactionStats(dateRange);
    dispatch({
      type: 'FACTION_STATS_SUCCESS',
      payload: response
    });
  } catch (error) {
    console.error('Fetch faction stats error:', error);
  }
};

export default rankingReducer;
