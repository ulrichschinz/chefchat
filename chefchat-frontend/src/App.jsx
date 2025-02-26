import React, { useContext } from 'react';
import ChatWindow from './ChatWindow';
import './App.css';
import Login from './Login';
import { AuthContext } from './AuthContext';

function App() {
  const {authTokens, setAuthTokens} = useContext(AuthContext);

  console.log("in app: " + authTokens);

  const handleLogin = (tokens) => {
    setAuthTokens(tokens);
  };

  return (
      <div className="App">
        {authTokens ? (
          <ChatWindow />
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
  );
}

export default App;
