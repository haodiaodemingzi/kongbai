import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService } from '../../services/auth';

const initialState = {
  user: null,
  token: null,
  isLoading: true,
  error: null
};

const authReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'AUTH_RESTORE_TOKEN':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false
      };

    case 'AUTH_LOGIN_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case 'AUTH_LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        error: null
      };

    case 'AUTH_LOGIN_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload
      };

    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        error: null
      };

    case 'AUTH_ERROR':
      return {
        ...state,
        error: action.payload
      };

    default:
      return state;
  }
};

// Actions
export const restoreToken = () => async (dispatch) => {
  try {
    const token = await AsyncStorage.getItem('authToken');
    const user = await AsyncStorage.getItem('authUser');
    
    if (token && user) {
      dispatch({
        type: 'AUTH_RESTORE_TOKEN',
        payload: {
          token,
          user: JSON.parse(user)
        }
      });
    } else {
      dispatch({
        type: 'AUTH_RESTORE_TOKEN',
        payload: { token: null, user: null }
      });
    }
  } catch (error) {
    dispatch({
      type: 'AUTH_RESTORE_TOKEN',
      payload: { token: null, user: null }
    });
  }
};

export const login = (username, password) => async (dispatch) => {
  dispatch({ type: 'AUTH_LOGIN_REQUEST' });
  
  try {
    const response = await authService.login(username, password);
    
    await AsyncStorage.setItem('authToken', response.token);
    await AsyncStorage.setItem('authUser', JSON.stringify(response.user));
    
    dispatch({
      type: 'AUTH_LOGIN_SUCCESS',
      payload: {
        user: response.user,
        token: response.token
      }
    });
  } catch (error) {
    dispatch({
      type: 'AUTH_LOGIN_FAILURE',
      payload: error.message
    });
    throw error;
  }
};

export const logout = () => async (dispatch) => {
  try {
    await authService.logout();
  } catch (error) {
    console.error('Logout error:', error);
  }
  
  await AsyncStorage.removeItem('authToken');
  await AsyncStorage.removeItem('authUser');
  
  dispatch({ type: 'AUTH_LOGOUT' });
};

export default authReducer;
