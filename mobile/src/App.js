import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import Toast from 'react-native-toast-message';
import { store } from './store/store';
import RootNavigator from './navigation/RootNavigator';
import { restoreToken } from './store/actions/authActions';

export default function App() {
  useEffect(() => {
    // 应用启动时恢复认证状态
    store.dispatch(restoreToken());
  }, []);

  return (
    <Provider store={store}>
      <NavigationContainer>
        <RootNavigator />
      </NavigationContainer>
      <Toast />
    </Provider>
  );
}
