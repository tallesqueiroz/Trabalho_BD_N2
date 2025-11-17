import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error("Usuário ou senha inválidos");
      }

      const data = await response.json();
      // Salva token no localStorage
      localStorage.setItem("token", data.access_token);

      // Redireciona para o dashboard
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>BiblioTech</h1>

        <label>Usuário</label>
        <input
          type="text"
          placeholder="Digite seu usuário"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label>Senha</label>
        <input
          type="password"
          placeholder="Digite sua senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p style={{ color: "red" }}>{error}</p>}

        <button onClick={handleLogin}>Entrar</button>
      </div>
    </div>
  );
}
