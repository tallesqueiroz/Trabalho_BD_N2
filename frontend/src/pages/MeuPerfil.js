import React, { useEffect, useState } from "react";

function MeuPerfil() {
  const [perfil, setPerfil] = useState(null);

  useEffect(() => {
    async function carregarPerfil() {
      try {
        // Pega o token do localStorage
        const token = localStorage.getItem("token");
        if (!token) throw new Error("Usuário não autenticado");

        const response = await fetch(
          "http://127.0.0.1:8000/api/usuarios/me",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) throw new Error("Erro ao carregar perfil");

        const data = await response.json();
        setPerfil(data);
      } catch (error) {
        console.error("Erro:", error);
      }
    }

    carregarPerfil();
  }, []);

  if (!perfil) return <p>Carregando...</p>;

  return (
    <div className="perfil-container">
      <h2>Meu Perfil</h2>

      <div className="perfil-card">
        <p><strong>Usuário:</strong> {perfil.username}</p>
        <p><strong>Email:</strong> {perfil.email}</p>

        <h3>Grupo</h3>
        <p><strong>Nome do Grupo:</strong> {perfil.grupo?.nome_grupo}</p>
        <p><strong>Descrição:</strong> {perfil.grupo?.descricao}</p>
      </div>
    </div>
  );
}

export default MeuPerfil;
