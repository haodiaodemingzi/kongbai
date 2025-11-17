import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import authReducer from './reducers/authReducer';
import rankingReducer from './reducers/rankingReducer';
import playerReducer from './reducers/playerReducer';
import uiReducer from './reducers/uiReducer';

const rootReducer = combineReducers({
  auth: authReducer,
  ranking: rankingReducer,
  player: playerReducer,
  ui: uiReducer
});

export const store = createStore(
  rootReducer,
  applyMiddleware(thunk)
);
