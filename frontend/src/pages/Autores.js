import React, { useEffect, useState } from "react";

export default function Autores() {
  const [autores, setAutores] = useState([]);
  const [novoNome, setNovoNome] = useState("");
  const [novoSobrenome, setNovoSobrenome] = useState("");
  const [mostrarForm, setMostrarForm] = useState(false);

  useEffect(() => {
    async function carregarAutores() {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/api/autores/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) throw new Error("Erro ao carregar autores");
        const data = await response.json();
        setAutores(data);
      } catch (error) {
        console.error("Erro:", error);
      }
    }

    carregarAutores();
  }, []);

  const handleCriarAutor = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/api/autores/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          nome: novoNome,
          sobrenome: novoSobrenome || null, // envia null se vazio
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Falha ao criar autor");
      }

      const autorCriado = await response.json();
      setAutores([...autores, autorCriado]);
      setNovoNome("");
      setNovoSobrenome("");
      setMostrarForm(false);
    } catch (error) {
      alert(`Falha ao criar autor: ${error.message}`);
    }
  };

  return (
    <div className="autores-container">
      <h2>Autores</h2>

      <button
        className="btn-criar"
        onClick={() => setMostrarForm(!mostrarForm)}
      >
        Criar Autor
      </button>

      {mostrarForm && (
        <form className="form-autor" onSubmit={handleCriarAutor}>
          <input
            type="text"
            placeholder="Nome"
            value={novoNome}
            onChange={(e) => setNovoNome(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Sobrenome"
            value={novoSobrenome}
            onChange={(e) => setNovoSobrenome(e.target.value)}
          />

          <button type="submit" className="btn-salvar">
            Salvar
          </button>
        </form>
      )}

      <table className="autores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Sobrenome</th>
          </tr>
        </thead>

        <tbody>
          {autores.map((a) => (
            <tr key={a.id_autor}>
              <td>{a.id_autor}</td>
              <td>{a.nome}</td>
              <td>{a.sobrenome || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
